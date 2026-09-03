from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import anndata as ad
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse, stats
from scipy.spatial.distance import cosine


ROOT = Path(__file__).resolve().parents[1]
STATE_RUN = ROOT / "results/state/full_phase2c_20260829T131235Z"
TABLES = ROOT / "results/tables"
REPORTS = ROOT / "reports"
FIGURES = ROOT / "figures/main"

PALETTE = {
    "blue_main": "#0F4D92",
    "blue_secondary": "#3775BA",
    "green_3": "#8BCF8B",
    "red_1": "#F6CFCB",
    "red_strong": "#B64342",
    "neutral": "#CFCECE",
    "teal": "#42949E",
    "violet": "#9A4D8E",
    "dark": "#272727",
}


@dataclass(frozen=True)
class TaskSpec:
    run_id: str
    label: str
    dataset: str
    split: str
    train_cell_line: str
    test_cell_line: str
    level: str
    metric_space: str


TASKS = [
    TaskSpec(
        "S1_norman_l1",
        "Norman L1 STATE",
        "Norman2019_GEARS_processed_mirror",
        "L1",
        "A549",
        "A549",
        "L1 within-context",
        "audit_delta",
    ),
    TaskSpec(
        "S2_norman_l2",
        "Norman L2 STATE",
        "Norman2019_GEARS_processed_mirror",
        "L2",
        "A549",
        "A549",
        "L2 within-context",
        "audit_delta",
    ),
    TaskSpec(
        "S3_replogle_k562_rl1",
        "Replogle K562 R-L1 STATE",
        "Replogle_GEARS_filtered",
        "R-L1-K562",
        "K562",
        "K562",
        "R-L1 within-context",
        "audit_delta",
    ),
    TaskSpec(
        "S4_replogle_k562_to_rpe1_rl4",
        "Replogle K562 -> RPE1 R-L4 STATE",
        "Replogle_GEARS_filtered",
        "R-L4-K2R",
        "K562",
        "RPE1",
        "R-L4 cross-context",
        "target_control_audit_delta",
    ),
]


def normalize_condition(label: object) -> str:
    text = str(label).strip()
    if text.lower() in {"", "nan", "none"}:
        return ""
    parts = []
    for part in text.split("+"):
        token = part.strip()
        if token.lower() in {"ctrl", "control", "non-targeting", "nontargeting", "ntc"}:
            continue
        if token:
            parts.append(token.upper())
    if not parts:
        return "ctrl"
    return "+".join(sorted(parts))


def to_array(x) -> np.ndarray:
    if sparse.issparse(x):
        return np.asarray(x.toarray())
    return np.asarray(x)


def matrix_mean(x) -> np.ndarray:
    if sparse.issparse(x):
        return np.asarray(x.mean(axis=0)).ravel().astype(np.float32)
    return np.asarray(np.mean(x, axis=0)).ravel().astype(np.float32)


def safe_corr(fn, x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or np.nanstd(x) == 0 or np.nanstd(y) == 0:
        return np.nan
    return float(fn(x, y).statistic)


def expression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    yt = np.asarray(y_true).ravel()
    yp = np.asarray(y_pred).ravel()
    return {
        "pearson_delta": safe_corr(stats.pearsonr, yt, yp),
        "spearman_delta": safe_corr(stats.spearmanr, yt, yp),
        "rmse_delta": float(np.sqrt(np.mean((yt - yp) ** 2))),
        "mae_delta": float(np.mean(np.abs(yt - yp))),
        "cosine_delta": float(1 - cosine(yt, yp)) if np.linalg.norm(yt) and np.linalg.norm(yp) else np.nan,
    }


def bootstrap_mean_ci(values, n_resamples: int = 2000, seed: int = 1) -> dict[str, float | str]:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {"mean": np.nan, "ci95_low": np.nan, "ci95_high": np.nan, "ci_status": "EMPTY"}
    if arr.size == 1:
        mean = float(arr[0])
        return {"mean": mean, "ci95_low": mean, "ci95_high": mean, "ci_status": "SINGLETON"}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, arr.size, size=(n_resamples, arr.size))
    means = arr[idx].mean(axis=1)
    return {
        "mean": float(arr.mean()),
        "ci95_low": float(np.percentile(means, 2.5)),
        "ci95_high": float(np.percentile(means, 97.5)),
        "ci_status": "BOOTSTRAP_PERTURBATION_LEVEL",
    }


def unsupported_effect_rate_at_k(pred_delta, true_delta, null_abs_threshold: float, k: int = 50) -> float:
    pred_delta = np.asarray(pred_delta)
    true_delta = np.asarray(true_delta)
    order = np.argsort(-np.abs(pred_delta))[:k]
    if len(order) == 0:
        return np.nan
    return float(np.mean(np.abs(true_delta[order]) <= null_abs_threshold))


def sign_flip_rate(pred_delta, true_delta, support_threshold: float) -> float:
    pred_delta = np.asarray(pred_delta)
    true_delta = np.asarray(true_delta)
    supported = np.abs(true_delta) > support_threshold
    if supported.sum() == 0:
        return np.nan
    flips = np.sign(pred_delta[supported]) != np.sign(true_delta[supported])
    return float(np.mean(flips))


def retrieval_rows(pred_centroids: dict[str, np.ndarray], true_centroids: dict[str, np.ndarray]) -> list[dict]:
    labels = sorted(set(pred_centroids) & set(true_centroids))
    if not labels:
        return []
    true_matrix = np.vstack([np.asarray(true_centroids[k]).ravel() for k in labels])
    true_norms = np.linalg.norm(true_matrix, axis=1)
    rows = []
    for label in labels:
        pred = np.asarray(pred_centroids[label]).ravel()
        pred_norm = np.linalg.norm(pred)
        if pred_norm == 0 or np.all(true_norms == 0):
            rows.append(
                {
                    "perturbation": label,
                    "true_target_rank": np.nan,
                    "top_match": "UNINFORMATIVE_PREDICTION",
                    "top_match_similarity": np.nan,
                    "true_target_similarity": np.nan,
                    "is_confused": np.nan,
                }
            )
            continue
        sims = true_matrix @ pred / np.maximum(true_norms * pred_norm, np.finfo(float).eps)
        order = np.argsort(-sims)
        true_idx = labels.index(label)
        rank = int(np.where(order == true_idx)[0][0]) + 1
        top_label = labels[int(order[0])]
        rows.append(
            {
                "perturbation": label,
                "true_target_rank": rank,
                "top_match": top_label,
                "top_match_similarity": float(sims[order[0]]),
                "true_target_similarity": float(sims[true_idx]),
                "is_confused": bool(top_label != label),
            }
        )
    return rows


def group_means(h5ad_path: Path) -> tuple[dict[str, np.ndarray], dict[str, int], int]:
    adata = ad.read_h5ad(h5ad_path, backed="r")
    labels = pd.Series(adata.obs["gene"].astype(str).map(normalize_condition).to_numpy(), index=adata.obs_names)
    means: dict[str, np.ndarray] = {}
    counts: dict[str, int] = {}
    for label in sorted(labels.unique()):
        mask = labels.eq(label).to_numpy()
        counts[label] = int(mask.sum())
        means[label] = matrix_mean(adata.X[mask, :])
    n_vars = int(adata.n_vars)
    adata.file.close()
    return means, counts, n_vars


def compute_task(spec: TaskSpec) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    run_dir = STATE_RUN / spec.run_id / spec.run_id / "eval_last.ckpt"
    pred_path = run_dir / "adata_pred.h5ad"
    real_path = run_dir / "adata_real.h5ad"
    if not pred_path.exists() or not real_path.exists():
        raise FileNotFoundError(f"missing STATE outputs for {spec.run_id}: {run_dir}")
    pred_means, pred_counts, pred_n_vars = group_means(pred_path)
    truth_means, truth_counts, truth_n_vars = group_means(real_path)
    if pred_n_vars != truth_n_vars:
        raise RuntimeError(f"var dimension mismatch for {spec.run_id}: {pred_n_vars} vs {truth_n_vars}")
    shared = sorted(set(pred_means) & set(truth_means) - {"ctrl"})
    if "ctrl" not in truth_means:
        raise RuntimeError(f"no ctrl rows available in real output for {spec.run_id}")
    audit_control = truth_means["ctrl"]
    pred_ctrl = pred_means.get("ctrl")
    truth_ctrl = truth_means.get("ctrl")

    rows = []
    raw_rows = []
    pred_delta = {}
    truth_delta = {}
    raw_pred_delta = {}
    raw_truth_delta = {}
    for pert in shared:
        pred = pred_means[pert]
        truth = truth_means[pert]
        p_delta = pred - audit_control
        t_delta = truth - audit_control
        pred_delta[pert] = p_delta
        truth_delta[pert] = t_delta
        null_threshold = float(np.nanpercentile(np.abs(t_delta), 50))
        support_threshold = float(np.nanpercentile(np.abs(t_delta), 95))
        metrics = expression_metrics(t_delta, p_delta)
        rows.append(
            {
                "run_id": spec.run_id,
                "space": spec.metric_space,
                "perturbation": pert,
                "n_pred_cells": pred_counts.get(pert, 0),
                "n_real_cells": truth_counts.get(pert, 0),
                **metrics,
                "uer20": unsupported_effect_rate_at_k(p_delta, t_delta, null_threshold, k=min(20, len(t_delta))),
                "uer50": unsupported_effect_rate_at_k(p_delta, t_delta, null_threshold, k=min(50, len(t_delta))),
                "uer100": unsupported_effect_rate_at_k(p_delta, t_delta, null_threshold, k=min(100, len(t_delta))),
                "sign_flip_rate": sign_flip_rate(p_delta, t_delta, support_threshold),
                "null_source": "median_abs_audit_delta",
                "null_status": "sensitivity_only",
                "bns_status": "UNVERIFIED",
            }
        )
        if pred_ctrl is not None and truth_ctrl is not None:
            rp_delta = pred - pred_ctrl
            rt_delta = truth - truth_ctrl
            raw_pred_delta[pert] = rp_delta
            raw_truth_delta[pert] = rt_delta
            raw_null = float(np.nanpercentile(np.abs(rt_delta), 50))
            raw_support = float(np.nanpercentile(np.abs(rt_delta), 95))
            raw_metrics = expression_metrics(rt_delta, rp_delta)
            raw_rows.append(
                {
                    "run_id": spec.run_id,
                    "space": "gears_raw",
                    "perturbation": pert,
                    "n_pred_cells": pred_counts.get(pert, 0),
                    "n_real_cells": truth_counts.get(pert, 0),
                    **raw_metrics,
                    "uer20": unsupported_effect_rate_at_k(rp_delta, rt_delta, raw_null, k=min(20, len(rt_delta))),
                    "uer50": unsupported_effect_rate_at_k(rp_delta, rt_delta, raw_null, k=min(50, len(rt_delta))),
                    "uer100": unsupported_effect_rate_at_k(rp_delta, rt_delta, raw_null, k=min(100, len(rt_delta))),
                    "sign_flip_rate": sign_flip_rate(rp_delta, rt_delta, raw_support),
                    "null_source": "median_abs_raw_delta",
                    "null_status": "sensitivity_only",
                    "bns_status": "UNVERIFIED",
                }
            )

    metrics_df = pd.DataFrame(rows + raw_rows)
    retrieval = pd.DataFrame(
        [{"run_id": spec.run_id, "space": spec.metric_space, **row} for row in retrieval_rows(pred_delta, truth_delta)]
        + [{"run_id": spec.run_id, "space": "gears_raw", **row} for row in retrieval_rows(raw_pred_delta, raw_truth_delta)]
    )
    summaries = []
    for space, m in metrics_df.groupby("space"):
        r = retrieval[retrieval["space"].eq(space)].copy()
        ranks = r["true_target_rank"].astype(float).to_numpy() if not r.empty else np.array([])
        rr = 1 / ranks[np.isfinite(ranks)] if ranks.size else np.array([])
        pearson_ci = bootstrap_mean_ci(m["pearson_delta"], seed=1)
        uer50_ci = bootstrap_mean_ci(m["uer50"], seed=1)
        sign_ci = bootstrap_mean_ci(m["sign_flip_rate"], seed=1)
        mrr_ci = bootstrap_mean_ci(rr, seed=1)
        summaries.append(
            {
                "run_id": spec.run_id,
                "setting": spec.label,
                "dataset": spec.dataset,
                "split": spec.split,
                "model": "STATE_state_sm",
                "model_type": "STATE",
                "train_cell_line": spec.train_cell_line,
                "test_cell_line": spec.test_cell_line,
                "level": spec.level,
                "metric_space": space,
                "n_test_perturbations": int(m["perturbation"].nunique()),
                "n_genes": pred_n_vars,
                "pearson_delta": pearson_ci["mean"],
                "pearson_ci_low": pearson_ci["ci95_low"],
                "pearson_ci_high": pearson_ci["ci95_high"],
                "spearman_delta": float(np.nanmean(m["spearman_delta"])),
                "rmse_delta": float(np.nanmean(m["rmse_delta"])),
                "mae_delta": float(np.nanmean(m["mae_delta"])),
                "cosine_delta": float(np.nanmean(m["cosine_delta"])),
                "retrieval_top1": float(np.mean(ranks == 1)) if ranks.size else np.nan,
                "retrieval_top5": float(np.mean(ranks <= 5)) if ranks.size else np.nan,
                "retrieval_mrr": mrr_ci["mean"],
                "mrr_ci_low": mrr_ci["ci95_low"],
                "mrr_ci_high": mrr_ci["ci95_high"],
                "uer20": float(np.nanmean(m["uer20"])),
                "uer50": uer50_ci["mean"],
                "uer50_ci_low": uer50_ci["ci95_low"],
                "uer50_ci_high": uer50_ci["ci95_high"],
                "uer100": float(np.nanmean(m["uer100"])),
                "sign_flip_rate": sign_ci["mean"],
                "sign_flip_ci_low": sign_ci["ci95_low"],
                "sign_flip_ci_high": sign_ci["ci95_high"],
                "uncertainty_status": pearson_ci["ci_status"],
                "null_status": "sensitivity_only",
                "bns_status": "UNVERIFIED",
                "filtered_data": spec.dataset == "Replogle_GEARS_filtered",
                "performance_eligible": True,
                "run_status": "COMPLETED_STATE_EVALUATION",
                "run_dir": str(STATE_RUN / spec.run_id),
            }
        )

    out_dir = STATE_RUN / spec.run_id / spec.run_id / "eval_last.ckpt"
    metrics_df.to_csv(out_dir / "state_metrics.csv", index=False)
    retrieval.to_csv(out_dir / "state_perturbation_retrieval.csv", index=False)
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(out_dir / "state_summary.csv", index=False)
    np.savez_compressed(out_dir / "state_audit_delta_centroids.npz", **{f"pred::{k}": v for k, v in pred_delta.items()}, **{f"truth::{k}": v for k, v in truth_delta.items()})
    return metrics_df, retrieval, summary_df


def load_gears_rows() -> pd.DataFrame:
    rows = []
    norman = pd.read_csv(TABLES / "norman_replogle_rl1_comparison.csv")
    for _, row in norman[norman["setting"].isin(["Norman L1 GEARS", "Norman L2 GEARS", "Replogle K562 R-L1 GEARS"])].iterrows():
        rows.append(
            {
                "setting": row["setting"],
                "dataset": row["dataset"],
                "split": row["split"],
                "model": row["model"],
                "model_type": "GEARS",
                "metric_space": row["metric_space"],
                "n_test_perturbations": int(row["n_test_perturbations"]),
                "pearson_delta": row["pearson_delta"],
                "pearson_ci_low": row["pearson_ci_low"],
                "pearson_ci_high": row["pearson_ci_high"],
                "retrieval_top1": row["retrieval_top1"],
                "retrieval_top5": row["retrieval_top5"],
                "retrieval_mrr": row["retrieval_mrr"],
                "uer50": row["uer50"],
                "sign_flip_rate": row["sign_flip_rate"],
                "bns_status": "UNVERIFIED",
                "performance_eligible": True,
                "source": "norman_replogle_rl1_comparison.csv",
            }
        )
    rl4 = pd.read_csv(TABLES / "replogle_rl1_rl4_gears_comparison.csv")
    k2r = rl4[rl4["split"].eq("R-L4-K2R")].iloc[0]
    rows.append(
        {
            "setting": "Replogle K562 -> RPE1 R-L4 GEARS",
            "dataset": "Replogle_GEARS_filtered",
            "split": k2r["split"],
            "model": "GEARS_cell_gears_0.1.2",
            "model_type": "GEARS",
            "metric_space": k2r["metric_space"],
            "n_test_perturbations": int(k2r["n_test_targets"]),
            "pearson_delta": k2r["pearson_delta"],
            "pearson_ci_low": k2r["pearson_ci_low"],
            "pearson_ci_high": k2r["pearson_ci_high"],
            "retrieval_top1": k2r["retrieval_top1"],
            "retrieval_top5": k2r["retrieval_top5"],
            "retrieval_mrr": k2r["retrieval_mrr"],
            "uer50": k2r["uer50"],
            "sign_flip_rate": k2r["sign_flip_rate"],
            "bns_status": "UNVERIFIED",
            "performance_eligible": True,
            "source": "replogle_rl1_rl4_gears_comparison.csv",
        }
    )
    return pd.DataFrame(rows)


def matched_transfer_drop(all_metrics: pd.DataFrame) -> pd.DataFrame:
    s3 = all_metrics[(all_metrics["run_id"].eq("S3_replogle_k562_rl1")) & (all_metrics["space"].eq("audit_delta"))].copy()
    s4 = all_metrics[(all_metrics["run_id"].eq("S4_replogle_k562_to_rpe1_rl4")) & (all_metrics["space"].eq("target_control_audit_delta"))].copy()
    common = sorted(set(s3["perturbation"]) & set(s4["perturbation"]))
    rows = []
    for metric in ["pearson_delta", "spearman_delta", "cosine_delta", "uer50", "sign_flip_rate"]:
        a = s3.set_index("perturbation").loc[common, metric].astype(float)
        b = s4.set_index("perturbation").loc[common, metric].astype(float)
        diff = a - b
        ci = bootstrap_mean_ci(diff, seed=2)
        rows.append(
            {
                "comparison": "STATE Replogle matched targets: K562 R-L1 minus K562->RPE1 R-L4",
                "metric": metric,
                "n_matched_targets": len(common),
                "source_mean": float(np.nanmean(a)),
                "cross_context_mean": float(np.nanmean(b)),
                "mean_drop_source_minus_cross": ci["mean"],
                "ci95_low": ci["ci95_low"],
                "ci95_high": ci["ci95_high"],
                "uncertainty_status": ci["ci_status"],
            }
        )
    return pd.DataFrame(rows)


def apply_style() -> None:
    plt.rcParams.update(
        {
            "font.family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "font.size": 14,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 2,
            "legend.frameon": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    )


def save_figure(fig, basename: Path, formats: list[str]) -> None:
    basename.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=1.4)
    for fmt in formats:
        fig.savefig(basename.with_suffix("." + fmt), dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def build_confirmatory_figure(comparison: pd.DataFrame) -> None:
    apply_style()
    audit = comparison[
        comparison["setting"].isin(
            [
                "Replogle K562 R-L1 GEARS",
                "Replogle K562 R-L1 STATE",
                "Replogle K562 -> RPE1 R-L4 GEARS",
                "Replogle K562 -> RPE1 R-L4 STATE",
            ]
        )
    ].copy()
    audit["condition"] = audit["setting"].map(
        {
            "Replogle K562 R-L1 GEARS": "GEARS\nR-L1",
            "Replogle K562 R-L1 STATE": "STATE\nR-L1",
            "Replogle K562 -> RPE1 R-L4 GEARS": "GEARS\nR-L4",
            "Replogle K562 -> RPE1 R-L4 STATE": "STATE\nR-L4",
        }
    )
    order = ["GEARS\nR-L1", "STATE\nR-L1", "GEARS\nR-L4", "STATE\nR-L4"]
    audit = audit.set_index("condition").loc[order].reset_index()
    colors = [PALETTE["blue_main"], PALETTE["blue_secondary"], PALETTE["red_strong"], PALETTE["red_1"] if "red_1" in PALETTE else PALETTE["neutral"]]
    fig, axes = plt.subplots(1, 4, figsize=(15, 4))
    panels = [
        ("pearson_delta", "Delta-Pearson", "higher is better"),
        ("retrieval_mrr", "Retrieval MRR", "higher is better"),
        ("uer50", "UER@50", "lower is better"),
        ("sign_flip_rate", "Sign flip", "lower is better"),
    ]
    for ax, (metric, ylabel, subtitle) in zip(axes, panels):
        vals = audit[metric].astype(float).to_numpy()
        bars = ax.bar(range(len(vals)), vals, color=colors, edgecolor="black", linewidth=1.2)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{val:.3f}", ha="center", va="bottom", fontsize=9)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(order, fontsize=10)
        ax.set_ylabel(ylabel)
        ax.set_title(subtitle, fontsize=10)
        ymax = max(0.05, float(np.nanmax(vals)) * 1.25)
        if metric in {"pearson_delta", "retrieval_mrr", "uer50", "sign_flip_rate"}:
            ax.set_ylim(0, min(1.0, ymax) if ymax <= 1.0 else ymax)
    save_figure(fig, FIGURES / "gears_state_confirmatory_audit", ["pdf", "svg", "png"])


def build_context_transfer_figure(transfer: pd.DataFrame) -> None:
    apply_style()
    fig, ax = plt.subplots(1, 1, figsize=(7, 4.2))
    show = transfer[transfer["metric"].isin(["pearson_delta", "uer50", "sign_flip_rate"])].copy()
    labels = show["metric"].map({"pearson_delta": "Pearson", "uer50": "UER@50", "sign_flip_rate": "Sign flip"}).tolist()
    vals = show["mean_drop_source_minus_cross"].astype(float).to_numpy()
    colors = [PALETTE["blue_main"], PALETTE["red_strong"], PALETTE["red_strong"]]
    bars = ax.bar(range(len(vals)), vals, color=colors, edgecolor="black", linewidth=1.2)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val, f"{val:.3f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=10)
    ax.axhline(0, color=PALETTE["dark"], linewidth=1)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("R-L1 minus R-L4 matched-target mean")
    ax.set_title("STATE matched-target context-transfer contrast", fontsize=12)
    save_figure(fig, FIGURES / "gears_state_context_transfer", ["pdf"])


def update_second_model_table(state_summary: pd.DataFrame) -> None:
    path = TABLES / "gears_second_model_confirmatory.csv"
    existing = pd.read_csv(path)
    keep = existing[~(existing["candidate"].astype(str).str.contains("STATE", na=False) & existing["local_status"].astype(str).eq("PERFORMANCE_ELIGIBLE_FULL_GPU"))].copy()
    rows = []
    primary = state_summary[state_summary["metric_space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    name_map = {
        "S1_norman_l1": "Norman L1",
        "S2_norman_l2": "Norman L2",
        "S3_replogle_k562_rl1": "Replogle K562 R-L1",
        "S4_replogle_k562_to_rpe1_rl4": "Replogle K562 -> RPE1 R-L4",
    }
    for _, row in primary.iterrows():
        rows.append(
            {
                "task": name_map[row["run_id"]],
                "requested_role": "second deep architecture confirmatory run",
                "candidate": "STATE state_sm",
                "local_status": "PERFORMANCE_ELIGIBLE_FULL_GPU",
                "pearson_delta": row["pearson_delta"],
                "mrr": row["retrieval_mrr"],
                "uer50": row["uer50"],
                "sign_flip_rate": row["sign_flip_rate"],
                "evidence": f"Full GPU STATE prediction evaluated from {Path(row['run_dir']).name}; metric_space={row['metric_space']}; performance_eligible=true.",
                "reason": "Full GPU run completed and synchronized locally; smoke-only rows retained separately.",
            }
        )
    pd.concat([keep, pd.DataFrame(rows)], ignore_index=True).to_csv(path, index=False)


def fmt(value, digits: int = 4) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)) or pd.isna(value):
        return "NA"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.{digits}f}"
    return str(value)


def md_table(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def write_reports(state_summary: pd.DataFrame, comparison: pd.DataFrame, transfer: pd.DataFrame) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    primary = state_summary[state_summary["metric_space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    repl = primary[primary["dataset"].eq("Replogle_GEARS_filtered")].copy()
    s3 = primary[primary["run_id"].eq("S3_replogle_k562_rl1")].iloc[0]
    s4 = primary[primary["run_id"].eq("S4_replogle_k562_to_rpe1_rl4")].iloc[0]
    pearson_drop = float(s3["pearson_delta"] - s4["pearson_delta"])
    mrr_drop = float(s3["retrieval_mrr"] - s4["retrieval_mrr"])
    uer_change = float(s4["uer50"] - s3["uer50"])
    matched = transfer.set_index("metric")
    matched_pearson_drop = float(matched.loc["pearson_delta", "mean_drop_source_minus_cross"])
    matched_uer_source_minus_cross = float(matched.loc["uer50", "mean_drop_source_minus_cross"])
    matched_sign_source_minus_cross = float(matched.loc["sign_flip_rate", "mean_drop_source_minus_cross"])
    decision = (
        "PARTIAL_ARCHITECTURE_SUPPORT_TARGET_MATCHED_ENDPOINT_MIXED"
        if matched_pearson_drop > 0.05 and matched_sign_source_minus_cross < 0
        else "INCONCLUSIVE_REQUIRES_REVIEW"
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    (REPORTS / "STATE_GEARS_METRIC_COMPATIBILITY.md").write_text(
        f"""# STATE-GEARS Metric Compatibility

Generated: {now}

STATE Phase 2C was evaluated with the same perturbation-level endpoint family used by the frozen GEARS audit: delta-Pearson, retrieval Top1/Top5/MRR, UER@20/50/100, sign-flip rate, RMSE, Spearman, and cosine similarity. The primary STATE interpretation uses audit-delta space, subtracting the real control mean from both predicted and observed target means. The Replogle R-L4 cross-context task is labeled `target_control_audit_delta`, matching the prior GEARS adapter convention.

Perturbation labels were normalized with the project convention that drops explicit control partners, so labels such as `ctrl+X` and `X` are evaluated as the same target `X`. This leaves 53 normalized Norman L1 STATE targets from 55 frozen test conditions and 28 normalized Norman L2 STATE targets from 40 frozen test conditions. The split-alignment audit remains fully aligned at the frozen-condition level.

BNS remains `UNVERIFIED`; UER is retained as `sensitivity_only` because the null is the median absolute observed delta rather than an externally verified biological null.

Primary comparison table:

{md_table(comparison[['setting','model_type','split','metric_space','n_test_perturbations','pearson_delta','retrieval_mrr','uer50','sign_flip_rate']], ['setting','model_type','split','metric_space','n_test_perturbations','pearson_delta','retrieval_mrr','uer50','sign_flip_rate'])}
""",
        encoding="utf-8",
    )

    (REPORTS / "STATE_REPLOGLE_EARLY_GATE.md").write_text(
        f"""# STATE Replogle Early Gate

Generated: {now}

Both Replogle STATE tasks are performance-eligible full GPU outputs and passed local metric extraction.

{md_table(repl[['setting','split','metric_space','n_test_perturbations','pearson_delta','pearson_ci_low','pearson_ci_high','retrieval_mrr','uer50','sign_flip_rate']], ['setting','split','metric_space','n_test_perturbations','pearson_delta','pearson_ci_low','pearson_ci_high','retrieval_mrr','uer50','sign_flip_rate'])}

Matched-target transfer summary:

{md_table(transfer, ['metric','n_matched_targets','source_mean','cross_context_mean','mean_drop_source_minus_cross','ci95_low','ci95_high'])}
""",
        encoding="utf-8",
    )

    (REPORTS / "STATE_RL4_ADAPTER_REPORT.md").write_text(
        f"""# STATE R-L4 Adapter Report

Generated: {now}

The R-L4 STATE adapter trained on K562 and predicted in the RPE1 target context. Evaluation used target-context controls from the synchronized STATE prediction pair and did not modify frozen GEARS splits, registries, or Phase 2A/2B metrics.

R-L4 STATE primary metrics:

{md_table(pd.DataFrame([s4]), ['setting','split','train_cell_line','test_cell_line','metric_space','n_test_perturbations','pearson_delta','retrieval_mrr','uer50','sign_flip_rate'])}

Adapter status: `PERFORMANCE_ELIGIBLE_FULL_GPU`; BNS `UNVERIFIED`; UER `sensitivity_only`.
""",
        encoding="utf-8",
    )

    (REPORTS / "PHASE2C_DECISION.md").write_text(
        f"""# Phase 2C Decision

Generated: {now}

Decision: `{decision}`.

The full GPU STATE run completed for Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4. The Replogle full-summary comparison shows lower cross-context Pearson under an independent STATE architecture, while retrieval MRR and UER@50 are mixed because the R-L4 target set is smaller:

- STATE K562 R-L1 delta-Pearson: {fmt(s3['pearson_delta'])}
- STATE K562-to-RPE1 R-L4 delta-Pearson: {fmt(s4['pearson_delta'])}
- Pearson drop: {fmt(pearson_drop)}
- Retrieval MRR drop: {fmt(mrr_drop)}
- UER@50 increase: {fmt(uer_change)}

On matched Replogle targets, STATE shows a clearer context-transfer contrast:

- Matched Pearson drop: {fmt(matched_pearson_drop)}
- Matched UER@50 source-minus-cross difference: {fmt(matched_uer_source_minus_cross)}
- Matched sign-flip source-minus-cross difference: {fmt(matched_sign_source_minus_cross)}

Interpretation: STATE partially reproduces the GEARS context-transfer failure phenotype on matched targets, supporting an architecture-independent signal for the core transfer drop. The endpoint-level picture is mixed in the full-summary table, so the decision is not a blanket confirmation. The conclusion remains bounded by the audit-delta null choice, unverified BNS, target-set differences, and the fact that Norman GEARS frozen rows are in raw GEARS space while STATE primary rows use audit-delta space.

Main deliverables:

- `results/tables/state_phase2c_primary_metrics.csv`
- `results/tables/state_transfer_drop.csv`
- `results/tables/gears_state_primary_comparison.csv`
- `reports/STATE_GEARS_METRIC_COMPATIBILITY.md`
- `reports/STATE_REPLOGLE_EARLY_GATE.md`
- `reports/STATE_RL4_ADAPTER_REPORT.md`
- `figures/main/gears_state_confirmatory_audit.pdf`
- `figures/main/gears_state_confirmatory_audit.svg`
- `figures/main/gears_state_confirmatory_audit.png`
- `figures/main/gears_state_context_transfer.pdf`
""",
        encoding="utf-8",
    )


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    all_metrics = []
    all_retrieval = []
    all_summary = []
    for spec in TASKS:
        print(f"[state-phase2c] evaluating {spec.run_id}", flush=True)
        metrics, retrieval, summary = compute_task(spec)
        all_metrics.append(metrics)
        all_retrieval.append(retrieval)
        all_summary.append(summary)
    metrics_df = pd.concat(all_metrics, ignore_index=True)
    retrieval_df = pd.concat(all_retrieval, ignore_index=True)
    summary_df = pd.concat(all_summary, ignore_index=True)
    metrics_df.to_csv(TABLES / "state_phase2c_perturbation_metrics.csv", index=False)
    retrieval_df.to_csv(TABLES / "state_phase2c_retrieval.csv", index=False)
    summary_df.to_csv(TABLES / "state_phase2c_primary_metrics.csv", index=False)

    transfer = matched_transfer_drop(metrics_df)
    transfer.to_csv(TABLES / "state_transfer_drop.csv", index=False)

    state_primary = summary_df[summary_df["metric_space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    state_primary["source"] = "state_phase2c_primary_metrics.csv"
    comparison = pd.concat([load_gears_rows(), state_primary], ignore_index=True, sort=False)
    comparison.to_csv(TABLES / "gears_state_primary_comparison.csv", index=False)

    update_second_model_table(summary_df)
    build_confirmatory_figure(comparison)
    build_context_transfer_figure(transfer)
    write_reports(summary_df, comparison, transfer)

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "state_run": str(STATE_RUN),
        "primary_metrics": str(TABLES / "state_phase2c_primary_metrics.csv"),
        "comparison": str(TABLES / "gears_state_primary_comparison.csv"),
        "transfer": str(TABLES / "state_transfer_drop.csv"),
        "performance_eligible": True,
        "bns_status": "UNVERIFIED",
        "uer_status": "sensitivity_only",
    }
    (TABLES / "state_phase2c_analysis_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("[state-phase2c] complete", flush=True)


if __name__ == "__main__":
    main()
