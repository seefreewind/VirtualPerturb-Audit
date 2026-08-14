from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

from src.data.loaders import normalize_norman_gears_schema, read_h5ad
from src.hallucination.metrics import sign_flip_rate, unsupported_effect_rate_at_k
from src.metrics.bounds import bound_normalized_score
from src.metrics.expression import expression_metrics
from src.metrics.retrieval import perturbation_centroid_retrieval, perturbation_retrieval_rows
from src.models.baselines import PCARidgeBaseline
from src.splits.builders import assign_l0_random_cells, assign_l1_perturbation_holdout, assign_l2_component_holdout
from src.statistics.bootstrap import bootstrap_mean_ci


SPLITTERS = {
    "L0": assign_l0_random_cells,
    "L1": assign_l1_perturbation_holdout,
    "L2": assign_l2_component_holdout,
}


def as_array(x):
    return x.toarray() if sparse.issparse(x) else np.asarray(x)


def mean_expr(adata, mask):
    x = adata.X[np.asarray(mask)]
    if sparse.issparse(x):
        return np.asarray(x.mean(axis=0)).ravel()
    return np.asarray(x).mean(axis=0)


def perturbation_deltas(adata, split_label):
    obs = adata.obs
    control_mask = obs["control_status"].astype(str).eq("control")
    ctrl = mean_expr(adata, control_mask)
    out = {}
    for pert in sorted(obs.loc[(obs["split_group"] == split_label) & ~control_mask, "perturbation"].astype(str).unique()):
        mask = (obs["split_group"] == split_label) & obs["perturbation"].astype(str).eq(pert)
        out[pert] = mean_expr(adata, mask) - ctrl
    return out, ctrl


def train_mean_delta(adata):
    obs = adata.obs
    control_mask = obs["control_status"].astype(str).eq("control")
    ctrl = mean_expr(adata, control_mask)
    train_mask = (obs["split_group"] == "train") & ~control_mask
    return mean_expr(adata, train_mask) - ctrl


def train_global_perturbed_mean_delta(adata):
    obs = adata.obs
    control_mask = obs["control_status"].astype(str).eq("control")
    ctrl = mean_expr(adata, control_mask)
    train_mask = (obs["split_group"] == "train") & ~control_mask
    return mean_expr(adata, train_mask) - ctrl


def context_column(adata) -> str | None:
    for col in ["cell_type", "context", "gemgroup", "batch"]:
        if col in adata.obs.columns and adata.obs[col].astype(str).nunique() > 1:
            return col
    return None


def context_matched_delta_map(adata, fallback: np.ndarray | None = None) -> dict[str, np.ndarray]:
    obs = adata.obs
    ctx_col = context_column(adata)
    fallback_delta = train_mean_delta(adata) if fallback is None else fallback
    control_mask = obs["control_status"].astype(str).eq("control")
    test_perts = sorted(obs.loc[(obs["split_group"] == "test") & ~control_mask, "perturbation"].astype(str).unique())
    if ctx_col is None:
        return {pert: fallback_delta for pert in test_perts}

    context_deltas = {}
    for ctx in sorted(obs[ctx_col].astype(str).unique()):
        train_ctx = (obs["split_group"] == "train") & ~control_mask & obs[ctx_col].astype(str).eq(ctx)
        ctrl_ctx = control_mask & obs[ctx_col].astype(str).eq(ctx)
        if int(train_ctx.sum()) == 0 or int(ctrl_ctx.sum()) == 0:
            continue
        context_deltas[ctx] = mean_expr(adata, train_ctx) - mean_expr(adata, ctrl_ctx)

    out = {}
    for pert in test_perts:
        test_mask = (obs["split_group"] == "test") & ~control_mask & obs["perturbation"].astype(str).eq(pert)
        weights = obs.loc[test_mask, ctx_col].astype(str).value_counts(normalize=True)
        pred = np.zeros(adata.n_vars)
        used = 0.0
        for ctx, weight in weights.items():
            if ctx in context_deltas:
                pred += float(weight) * context_deltas[ctx]
                used += float(weight)
        out[pert] = pred + (1.0 - used) * fallback_delta if used else fallback_delta
    return out


def train_perturbation_deltas(adata) -> dict[str, np.ndarray]:
    obs = adata.obs
    control_mask = obs["control_status"].astype(str).eq("control")
    ctrl = mean_expr(adata, control_mask)
    out = {}
    train_perts = sorted(obs.loc[(obs["split_group"] == "train") & ~control_mask, "perturbation"].astype(str).unique())
    for pert in train_perts:
        mask = (obs["split_group"] == "train") & obs["perturbation"].astype(str).eq(pert)
        out[pert] = mean_expr(adata, mask) - ctrl
    return out


def perturbation_components(perturbation: str) -> list[str]:
    if perturbation == "ctrl":
        return []
    return [part for part in str(perturbation).split("+") if part != "ctrl"]


def additive_delta_map(adata, fallback: np.ndarray | None = None) -> dict[str, np.ndarray]:
    obs = adata.obs
    control_mask = obs["control_status"].astype(str).eq("control")
    test_perts = sorted(obs.loc[(obs["split_group"] == "test") & ~control_mask, "perturbation"].astype(str).unique())
    train_deltas = train_perturbation_deltas(adata)
    fallback_delta = train_mean_delta(adata) if fallback is None else fallback
    out = {}
    for pert in test_perts:
        components = perturbation_components(pert)
        component_deltas = []
        for gene in components:
            exact = train_deltas.get(gene)
            direct = train_deltas.get(f"{gene}+ctrl")
            reverse = train_deltas.get(f"ctrl+{gene}")
            if exact is not None:
                component_deltas.append(exact)
            elif direct is not None:
                component_deltas.append(direct)
            elif reverse is not None:
                component_deltas.append(reverse)
        out[pert] = np.sum(component_deltas, axis=0) if component_deltas else fallback_delta
    return out


def perturbation_feature_matrix(perturbations: list[str], vocabulary: list[str]) -> np.ndarray:
    gene_to_idx = {gene: i for i, gene in enumerate(vocabulary)}
    x = np.zeros((len(perturbations), len(vocabulary)), dtype=float)
    for row, pert in enumerate(perturbations):
        for gene in perturbation_components(pert):
            if gene in gene_to_idx:
                x[row, gene_to_idx[gene]] += 1.0
    return x


def pca_ridge_delta_map(adata, fallback: np.ndarray | None = None) -> dict[str, np.ndarray]:
    obs = adata.obs
    control_mask = obs["control_status"].astype(str).eq("control")
    test_perts = sorted(obs.loc[(obs["split_group"] == "test") & ~control_mask, "perturbation"].astype(str).unique())
    fallback_delta = train_mean_delta(adata) if fallback is None else fallback
    train_deltas = train_perturbation_deltas(adata)
    train_perts = sorted(train_deltas)
    vocabulary = sorted({gene for pert in train_perts + test_perts for gene in perturbation_components(pert)})
    if len(train_perts) < 2 or not vocabulary:
        return {pert: fallback_delta for pert in test_perts}
    x_train = perturbation_feature_matrix(train_perts, vocabulary)
    y_train = np.vstack([train_deltas[pert] for pert in train_perts])
    if np.linalg.matrix_rank(x_train) == 0:
        return {pert: fallback_delta for pert in test_perts}
    model = PCARidgeBaseline(n_components=20, alpha=1.0).fit(x_train, y_train)
    x_test = perturbation_feature_matrix(test_perts, vocabulary)
    y_pred = model.predict_delta(x_test)
    return {pert: y_pred[i] for i, pert in enumerate(test_perts)}


def split_half_upper(delta_true):
    # Placeholder until replicate labels are verified; this keeps BNS uninterpreted.
    return np.nan


def summarize_delta_models(
    adata,
    split,
    model_preds: list[tuple[str, np.ndarray | dict[str, np.ndarray], str] | tuple[str, np.ndarray | dict[str, np.ndarray], str, str]],
):
    true_deltas, _ = perturbation_deltas(adata, "test")
    rows = []
    retrieval_rows = []
    for entry in model_preds:
        if len(entry) == 3:
            model_name, pred, status = entry
            note_prefix = "Baseline pseudobulk pilot"
        else:
            model_name, pred, status, note_prefix = entry
        perts = []
        pearsons = []
        uers = []
        sfrs = []
        pred_deltas = {}
        for pert, true_delta in true_deltas.items():
            pred_delta = pred.get(pert, np.zeros(adata.n_vars)) if isinstance(pred, dict) else pred
            pred_deltas[pert] = pred_delta
            m = expression_metrics(true_delta, pred_delta)
            halluc = sign_flip_rate(pred_delta, true_delta, support_threshold=np.nanpercentile(np.abs(true_delta), 95))
            null_threshold = np.nanpercentile(np.abs(true_delta), 50)
            perts.append(pert)
            pearsons.append(m["pearson"])
            uers.append(unsupported_effect_rate_at_k(pred_delta, true_delta, null_threshold, k=min(50, len(true_delta))))
            sfrs.append(halluc["sign_flip_rate"])
        pearson_ci = bootstrap_mean_ci(pearsons, seed=1)
        uer_ci = bootstrap_mean_ci(uers, seed=1)
        sfr_ci = bootstrap_mean_ci(sfrs, seed=1)
        mean_pearson = pearson_ci["mean"]
        lower = mean_pearson if model_name == "B0_no_change" else np.nan
        upper = split_half_upper(true_deltas)
        bns, bns_status = bound_normalized_score(mean_pearson, lower, upper)
        retrieval = perturbation_centroid_retrieval(pred_deltas, true_deltas)
        for retrieval_row in perturbation_retrieval_rows(pred_deltas, true_deltas):
            retrieval_rows.append({
                "dataset": "Norman2019_GEARS_processed_mirror",
                "model": model_name,
                "split": split,
                **retrieval_row,
            })
        metric_note = "Delta Pearson undefined for zero-vector prediction." if not np.isfinite(mean_pearson) else ""
        rows.append({
            "dataset": "Norman2019_GEARS_processed_mirror",
            "model": model_name,
            "split": split,
            "status": status,
            "n_test_perturbations": len(perts),
            "pearson_delta": mean_pearson,
            "pearson_delta_ci95_low": pearson_ci["ci95_low"],
            "pearson_delta_ci95_high": pearson_ci["ci95_high"],
            "bns": bns,
            "bns_status": bns_status,
            "UER_at_50": np.nanmean(uers),
            "UER_at_50_ci95_low": uer_ci["ci95_low"],
            "UER_at_50_ci95_high": uer_ci["ci95_high"],
            "sign_flip_rate": np.nanmean(sfrs),
            "sign_flip_rate_ci95_low": sfr_ci["ci95_low"],
            "sign_flip_rate_ci95_high": sfr_ci["ci95_high"],
            "retrieval_top1_accuracy": retrieval["top1_accuracy"],
            "retrieval_top5_accuracy": retrieval["top5_accuracy"],
            "retrieval_mrr": retrieval["mrr"],
            "uncertainty_status": pearson_ci["ci_status"],
            "notes": f"{note_prefix}; replicate upper bound not yet verified. " + metric_note,
        })
    return rows, retrieval_rows


def evaluate_split(adata, split):
    lower_pred = np.zeros(adata.n_vars)
    global_mean_pred = train_global_perturbed_mean_delta(adata)
    mean_pred = train_mean_delta(adata)
    additive_pred = additive_delta_map(adata, fallback=mean_pred)
    context_pred = context_matched_delta_map(adata, fallback=mean_pred)
    ridge_pred = pca_ridge_delta_map(adata, fallback=mean_pred)
    rows, _ = summarize_delta_models(
        adata,
        split,
        [
            ("B0_no_change", lower_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            ("B1_global_perturbed_mean", global_mean_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            ("B2_context_matched_perturbed_mean", context_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            ("B3_additive_seen_component", additive_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            ("B4_pca_ridge", ridge_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            ("B5_mean_effect", mean_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
        ],
    )
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5ad", default="data/raw/norman/perturb_processed.h5ad")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    h5ad = Path(args.h5ad)
    if not h5ad.exists():
        raise FileNotFoundError(f"Norman file not found: {h5ad}")
    adata = normalize_norman_gears_schema(read_h5ad(h5ad))
    rows = []
    retrieval_rows = []
    for split, fn in SPLITTERS.items():
        adata.obs["split_group"] = fn(adata, seed=args.seed)
        split_rows, split_retrieval = summarize_delta_models(
            adata,
            split,
            [
                ("B0_no_change", np.zeros(adata.n_vars), "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
                (
                    "B1_global_perturbed_mean",
                    train_global_perturbed_mean_delta(adata),
                    "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND",
                ),
                (
                    "B2_context_matched_perturbed_mean",
                    context_matched_delta_map(adata, fallback=train_mean_delta(adata)),
                    "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND",
                ),
                (
                    "B3_additive_seen_component",
                    additive_delta_map(adata, fallback=train_mean_delta(adata)),
                    "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND",
                ),
                (
                    "B4_pca_ridge",
                    pca_ridge_delta_map(adata, fallback=train_mean_delta(adata)),
                    "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND",
                ),
                ("B5_mean_effect", train_mean_delta(adata), "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            ],
        )
        rows.extend(split_rows)
        retrieval_rows.extend(split_retrieval)
    out = Path("results/pilot/pilot_summary.csv")
    baseline = pd.DataFrame(rows)
    if out.exists():
        existing = pd.read_csv(out)
        existing = existing[
            ~existing["model"].astype(str).isin(
                [
                    "B0_no_change",
                    "B1_global_perturbed_mean",
                    "B2_context_matched_perturbed_mean",
                    "B3_additive_seen_component",
                    "B4_pca_ridge",
                    "B5_mean_effect",
                ]
            )
        ]
        baseline = pd.concat([baseline, existing], ignore_index=True)
    baseline.to_csv(out, index=False)
    retrieval_out = Path("results/pilot/perturbation_retrieval.csv")
    retrieval = pd.DataFrame(retrieval_rows)
    if retrieval_out.exists():
        existing_retrieval = pd.read_csv(retrieval_out)
        existing_retrieval = existing_retrieval[
            ~existing_retrieval["model"].astype(str).isin(
                [
                    "B0_no_change",
                    "B1_global_perturbed_mean",
                    "B2_context_matched_perturbed_mean",
                    "B3_additive_seen_component",
                    "B4_pca_ridge",
                    "B5_mean_effect",
                ]
            )
        ]
        retrieval = pd.concat([existing_retrieval, retrieval], ignore_index=True)
    retrieval.to_csv(retrieval_out, index=False)


if __name__ == "__main__":
    main()
