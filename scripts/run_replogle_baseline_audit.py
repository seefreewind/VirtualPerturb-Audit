from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

from scripts.audit_replogle_processed import standardized_obs
from scripts.run_baseline_pilot import perturbation_feature_matrix
from src.data.perturbations import normalize_condition
from src.hallucination.metrics import sign_flip_rate, unsupported_effect_rate_at_k
from src.metrics.expression import expression_metrics
from src.metrics.retrieval import perturbation_centroid_retrieval, perturbation_retrieval_rows
from src.models.baselines import PCARidgeBaseline
from src.splits.builders import assign_replogle_l1_context_perturbation_holdout, assign_replogle_l4_cross_context
from src.statistics.bootstrap import bootstrap_mean_ci


def read_h5ad(path: str):
    import scanpy as sc

    return sc.read_h5ad(path)


warnings.filterwarnings("ignore", category=RuntimeWarning)


def mean_expr(x, mask: np.ndarray) -> np.ndarray:
    if int(np.asarray(mask).sum()) == 0:
        raise ValueError("Cannot compute mean expression for an empty mask")
    sub = x[mask]
    if sparse.issparse(sub):
        return np.asarray(sub.mean(axis=0)).ravel()
    return np.asarray(sub).mean(axis=0)


def deltas_by_perturbation(x, obs: pd.DataFrame, mask: np.ndarray, ctrl_mask: np.ndarray) -> dict[str, np.ndarray]:
    ctrl = mean_expr(x, ctrl_mask)
    out = {}
    perts = sorted(obs.loc[mask & obs["control_status"].eq("perturbed"), "perturbation"].unique())
    for pert in perts:
        pert_mask = mask & obs["perturbation"].eq(pert).to_numpy()
        out[pert] = mean_expr(x, pert_mask) - ctrl
    return out


def pca_ridge_predictions(
    train_deltas: dict[str, np.ndarray], test_perts: list[str], fallback: np.ndarray
) -> tuple[dict[str, np.ndarray], str]:
    train_perts = sorted(train_deltas)
    vocabulary = sorted(set(train_perts) | set(test_perts))
    if len(train_perts) < 2:
        return {pert: fallback for pert in test_perts}, "FAILED_B4_TOO_FEW_TRAIN_TARGETS_FALLBACK_MEAN_EFFECT"
    x_train = perturbation_feature_matrix(train_perts, vocabulary)
    y_train = np.vstack([train_deltas[p] for p in train_perts])
    if np.linalg.matrix_rank(x_train) == 0:
        return {pert: fallback for pert in test_perts}, "FAILED_B4_RANK_ZERO_FALLBACK_MEAN_EFFECT"
    if not np.isfinite(y_train).all():
        return {pert: fallback for pert in test_perts}, "FAILED_B4_NONFINITE_TRAIN_DELTAS_FALLBACK_MEAN_EFFECT"
    try:
        model = PCARidgeBaseline(n_components=20, alpha=1.0).fit(x_train, y_train)
        x_test = perturbation_feature_matrix(test_perts, vocabulary)
        pred = model.predict_delta(x_test)
        if not np.isfinite(pred).all():
            return {pert: fallback for pert in test_perts}, "FAILED_B4_NONFINITE_PREDICTIONS_FALLBACK_MEAN_EFFECT"
    except Exception as exc:
        return {pert: fallback for pert in test_perts}, f"FAILED_B4_NUMERIC_FALLBACK_MEAN_EFFECT_{type(exc).__name__}"
    return {pert: pred[i] for i, pert in enumerate(test_perts)}, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"


def summarize(setting: dict, true_deltas: dict[str, np.ndarray], predictions: list[tuple[str, dict[str, np.ndarray], str]], seed: int):
    rows = []
    retrieval_rows = []
    for model, pred_map, status in predictions:
        pearsons = []
        uers = []
        sfrs = []
        aligned_pred = {}
        for pert, true_delta in true_deltas.items():
            pred = pred_map.get(pert)
            if pred is None:
                pred = np.zeros_like(true_delta)
            aligned_pred[pert] = pred
            pearsons.append(expression_metrics(true_delta, pred)["pearson"])
            threshold = np.nanpercentile(np.abs(true_delta), 50)
            uers.append(unsupported_effect_rate_at_k(pred, true_delta, threshold, k=min(50, len(true_delta))))
            support = np.nanpercentile(np.abs(true_delta), 95)
            sfrs.append(sign_flip_rate(pred, true_delta, support_threshold=support)["sign_flip_rate"])
        ci = bootstrap_mean_ci(pearsons, seed=seed, n_resamples=2000)
        uer_ci = bootstrap_mean_ci(uers, seed=seed, n_resamples=2000)
        sfr_ci = bootstrap_mean_ci(sfrs, seed=seed, n_resamples=2000)
        retrieval = perturbation_centroid_retrieval(aligned_pred, true_deltas)
        row = {
            **setting,
            "model": model,
            "seed": seed,
            "n_test_targets": len(true_deltas),
            "pearson_delta": ci["mean"],
            "pearson_ci_low": ci["ci95_low"],
            "pearson_ci_high": ci["ci95_high"],
            "retrieval_top1": retrieval["top1_accuracy"],
            "retrieval_top5": retrieval["top5_accuracy"],
            "mrr": retrieval["mrr"],
            "uer20": np.nan,
            "uer50": float(np.nanmean(uers)),
            "uer100": np.nan,
            "uer50_ci_low": uer_ci["ci95_low"],
            "uer50_ci_high": uer_ci["ci95_high"],
            "sign_flip_rate": float(np.nanmean(sfrs)),
            "sign_flip_ci_low": sfr_ci["ci95_low"],
            "sign_flip_ci_high": sfr_ci["ci95_high"],
            "bns": np.nan,
            "bns_status": "UNVERIFIED",
            "replicate_status": "NOT_AVAILABLE",
            "run_status": status,
            "uncertainty_status": ci["ci_status"],
        }
        rows.append(row)
        for rr in perturbation_retrieval_rows(aligned_pred, true_deltas):
            retrieval_rows.append({**setting, "model": model, **rr})
    return rows, retrieval_rows


def build_context(name: str, path: str, cell_line: str):
    adata = read_h5ad(path)
    obs = standardized_obs(adata, f"Replogle_{cell_line}_GEARS_filtered", cell_line)
    return {"name": name, "adata": adata, "obs": obs, "x": adata.X}


def evaluate_setting(setting_name: str, train_ctx: dict, test_ctx: dict, labels: pd.Series, seed: int):
    obs_train = train_ctx["obs"].copy()
    obs_test = test_ctx["obs"].copy()
    same_context = train_ctx is test_ctx
    if same_context:
        obs = obs_train
        obs["split_group"] = labels.reindex(obs.index).to_numpy()
        train_mask = obs["split_group"].eq("train").to_numpy()
        test_mask = obs["split_group"].eq("test").to_numpy()
        ctrl_train = train_mask & obs["control_status"].eq("control").to_numpy()
        ctrl_test = test_mask & obs["control_status"].eq("control").to_numpy()
        if int(ctrl_test.sum()) == 0:
            ctrl_test = obs["control_status"].eq("control").to_numpy()
        train_deltas = deltas_by_perturbation(train_ctx["x"], obs, train_mask, ctrl_train)
        true_deltas = deltas_by_perturbation(train_ctx["x"], obs, test_mask, ctrl_test)
        n_train_cells = int(train_mask.sum())
        n_test_cells = int(test_mask.sum())
    else:
        obs_tr = obs_train
        obs_te = obs_test
        train_labels = labels.reindex(obs_tr.index)
        test_labels = labels.reindex(obs_te.index)
        train_mask = train_labels.eq("train").to_numpy()
        test_mask = test_labels.eq("test").to_numpy()
        ctrl_train = train_mask & obs_tr["control_status"].eq("control").to_numpy()
        ctrl_test = test_mask & obs_te["control_status"].eq("control").to_numpy()
        train_deltas = deltas_by_perturbation(train_ctx["x"], obs_tr, train_mask, ctrl_train)
        true_deltas = deltas_by_perturbation(test_ctx["x"], obs_te, test_mask, ctrl_test)
        n_train_cells = int(train_mask.sum())
        n_test_cells = int(test_mask.sum())
    if not true_deltas:
        raise ValueError(f"No test deltas for {setting_name}")
    test_perts = sorted(true_deltas)
    fallback = np.mean(np.vstack(list(train_deltas.values())), axis=0)
    zero = {p: np.zeros_like(fallback) for p in test_perts}
    mean_pred = {p: fallback for p in test_perts}
    ridge, ridge_status = pca_ridge_predictions(train_deltas, test_perts, fallback)
    rng = np.random.default_rng(seed)
    train_keys = sorted(train_deltas)
    shuffled = {p: train_deltas[rng.choice(train_keys)] for p in test_perts}
    setting = {
        "dataset": "Replogle_GEARS_filtered",
        "cell_line_train": train_ctx["name"],
        "cell_line_test": test_ctx["name"],
        "split": setting_name,
        "n_train_cells": n_train_cells,
        "n_test_cells": n_test_cells,
        "n_train_targets": len(train_deltas),
    }
    preds = [
        ("B0_no_change", zero, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
        ("B1_global_perturbed_mean", mean_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
        ("B2_context_matched_perturbed_mean", mean_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
        ("B4_pca_ridge", ridge, ridge_status),
        ("B5_mean_effect", mean_pred, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
        ("FP1_perturbation_blind_mean_effect", mean_pred, "COMPLETED_FALSIFICATION_PROBE"),
        ("FP3_label_shuffled_mean_effect", shuffled, "COMPLETED_FALSIFICATION_PROBE"),
    ]
    return summarize(setting, true_deltas, preds, seed)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k562", default="data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad")
    parser.add_argument("--rpe1", default="data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    k = build_context("K562", args.k562, "K562")
    r = build_context("RPE1", args.rpe1, "RPE1")
    overlap = pd.read_csv("results/tables/replogle_context_target_overlap.tsv", sep="\t")
    eligible = set(overlap.loc[overlap["cross_context_eligible"], "target"].astype(str).map(normalize_condition))
    settings = [
        (
            "R-L1-K562",
            k,
            k,
            pd.Series(assign_replogle_l1_context_perturbation_holdout(ObsLike(k["obs"]), "K562", seed=args.seed), index=k["obs"].index),
        ),
        (
            "R-L1-RPE1",
            r,
            r,
            pd.Series(assign_replogle_l1_context_perturbation_holdout(ObsLike(r["obs"]), "RPE1", seed=args.seed), index=r["obs"].index),
        ),
    ]
    combined = pd.concat([k["obs"], r["obs"]])
    settings.append(
        (
            "R-L4-K2R",
            k,
            r,
            pd.Series(assign_replogle_l4_cross_context(ObsLike(combined), "K562", "RPE1", eligible), index=combined.index),
        )
    )
    settings.append(
        (
            "R-L4-R2K",
            r,
            k,
            pd.Series(assign_replogle_l4_cross_context(ObsLike(combined), "RPE1", "K562", eligible), index=combined.index),
        )
    )
    rows = []
    retrieval = []
    for name, train_ctx, test_ctx, labels in settings:
        split_rows, split_ret = evaluate_setting(name, train_ctx, test_ctx, labels, args.seed)
        rows.extend(split_rows)
        retrieval.extend(split_ret)
    Path("results/replogle").mkdir(parents=True, exist_ok=True)
    summary = pd.DataFrame(rows)
    retrieval_df = pd.DataFrame(retrieval)
    summary.to_csv("results/replogle/replogle_summary.csv", index=False)
    retrieval_df.to_csv("results/replogle/replogle_perturbation_retrieval.csv", index=False)
    write_report(summary)


class ObsLike:
    def __init__(self, obs: pd.DataFrame):
        self.obs = obs


def write_report(summary: pd.DataFrame) -> None:
    primary = summary[summary["model"].isin(["B0_no_change", "B1_global_perturbed_mean", "B2_context_matched_perturbed_mean", "B4_pca_ridge", "B5_mean_effect"])]
    compact = primary[
        [
            "split",
            "model",
            "n_test_targets",
            "pearson_delta",
            "pearson_ci_low",
            "pearson_ci_high",
            "retrieval_top1",
            "retrieval_top5",
            "mrr",
            "uer50",
            "sign_flip_rate",
            "bns_status",
        ]
    ].copy()
    lines = [
        "# Replogle Baseline Audit",
        "",
        "Status: **COMPLETED_BASELINE_FIRST_AUDIT_ON_GEARS_FILTERED_ESSENTIAL_DATA**",
        "",
        "The current audit uses GEARS-compatible filtered Replogle essential screen files from Harvard Dataverse, not the complete Figshare+ single-cell deposits.",
        "",
        "## Primary Baseline Metrics",
        "",
        compact.to_csv(index=False),
        "",
        "## Interpretation",
        "",
        "- BNS remains `UNVERIFIED`; no biological replicate label is available in the filtered h5ad obs fields.",
        "- B1, B2, B5, and FP-1 are expected to be identical in this first pass because no within-context replicate or richer context covariate is exposed.",
        "- B3/FP-2 are not included in the first Replogle essential baseline because these filtered Replogle files contain single-gene `GENE+ctrl` perturbations rather than Norman-style combinatorial perturbations.",
    ]
    Path("reports/REPLOGLE_BASELINE_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
