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
        for pert, true_delta in true_deltas.items():
            pred_delta = pred.get(pert, np.zeros(adata.n_vars)) if isinstance(pred, dict) else pred
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
            "uncertainty_status": pearson_ci["ci_status"],
            "notes": f"{note_prefix}; replicate upper bound not yet verified. " + metric_note,
        })
    return rows


def evaluate_split(adata, split):
    lower_pred = np.zeros(adata.n_vars)
    mean_pred = train_mean_delta(adata)
    return summarize_delta_models(
        adata,
        split,
        [
            ("B0_no_change", lower_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            ("B5_mean_effect", mean_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
        ],
    )


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
    for split, fn in SPLITTERS.items():
        adata.obs["split_group"] = fn(adata, seed=args.seed)
        rows.extend(evaluate_split(adata, split))
    out = Path("results/pilot/pilot_summary.csv")
    baseline = pd.DataFrame(rows)
    if out.exists():
        existing = pd.read_csv(out)
        existing = existing[~existing["model"].astype(str).isin(["B0_no_change", "B5_mean_effect"])]
        baseline = pd.concat([baseline, existing], ignore_index=True)
    baseline.to_csv(out, index=False)


if __name__ == "__main__":
    main()
