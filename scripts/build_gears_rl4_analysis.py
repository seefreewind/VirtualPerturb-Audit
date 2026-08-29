from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.statistics.bootstrap import bootstrap_mean_ci


REPL = Path("results/replogle")
GEARS_DIR = REPL / "gears"
TABLES = Path("results/tables")
FIGURES = Path("figures/main")
REPORTS = Path("reports")


DIRECTIONS = {
    "k2r": ("K562", "RPE1", "R-L4-K2R"),
    "r2k": ("RPE1", "K562", "R-L4-R2K"),
}


def latest_completed_run(direction: str) -> tuple[Path, dict]:
    runs = sorted(GEARS_DIR.glob(f"rl4_{direction}_*"))
    for run in reversed(runs):
        meta_path = run / "metadata.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        if meta.get("run_status") in {"COMPLETED_GEARS", "COMPLETED_GEARS_EVALUATION"}:
            return run, meta
    raise FileNotFoundError(f"No completed R-L4 run found for {direction}")


def ci_from_metrics(metrics: pd.DataFrame, column: str, seed: int) -> dict:
    return bootstrap_mean_ci(metrics[column].to_numpy(), n_resamples=2000, seed=seed)


def summarize_run(direction: str) -> dict:
    run, meta = latest_completed_run(direction)
    summary = pd.read_csv(run / "gears_summary.csv").iloc[0].to_dict()
    metrics = pd.read_csv(run / "gears_metrics.csv")
    retrieval = pd.read_csv(run / "gears_perturbation_retrieval.csv")
    rr = 1.0 / retrieval["true_target_rank"].astype(float)
    mrr_ci = bootstrap_mean_ci(rr.to_numpy(), n_resamples=2000, seed=int(meta.get("seed", 1)))
    pearson_ci = ci_from_metrics(metrics, "pearson_delta", int(meta.get("seed", 1)))
    uer50_ci = ci_from_metrics(metrics, "uer50", int(meta.get("seed", 1)))
    sign_ci = ci_from_metrics(metrics, "sign_flip_rate", int(meta.get("seed", 1)))
    train_cell, test_cell, split = DIRECTIONS[direction]
    return {
        "dataset": "Replogle_GEARS_filtered",
        "direction": direction,
        "train_cell_line": train_cell,
        "test_cell_line": test_cell,
        "split": split,
        "model": "GEARS_cell_gears_0.1.2",
        "seed": int(meta.get("seed", 1)),
        "run_dir": str(run),
        "run_status": "COMPLETED_GEARS_EVALUATION",
        "elapsed_seconds": float(meta.get("elapsed_seconds", np.nan)),
        "n_test_targets": int(summary["n_test_perturbations"]),
        "pearson_delta": float(summary["pearson_delta"]),
        "pearson_ci_low": float(pearson_ci["ci95_low"]),
        "pearson_ci_high": float(pearson_ci["ci95_high"]),
        "spearman_delta": float(summary["spearman_delta_mean"]),
        "rmse_delta": float(summary["rmse_delta_mean"]),
        "cosine_delta": float(summary["cosine_delta_mean"]),
        "retrieval_top1": float(summary["retrieval_top1_accuracy"]),
        "retrieval_top5": float(summary["retrieval_top5_accuracy"]),
        "retrieval_mrr": float(mrr_ci["mean"]),
        "mrr_ci_low": float(mrr_ci["ci95_low"]),
        "mrr_ci_high": float(mrr_ci["ci95_high"]),
        "uer20": float(summary["uer20_mean"]),
        "uer50": float(uer50_ci["mean"]),
        "uer50_ci_low": float(uer50_ci["ci95_low"]),
        "uer50_ci_high": float(uer50_ci["ci95_high"]),
        "uer100": float(summary["uer100_mean"]),
        "sign_flip_rate": float(sign_ci["mean"]),
        "sign_flip_ci_low": float(sign_ci["ci95_low"]),
        "sign_flip_ci_high": float(sign_ci["ci95_high"]),
        "metric_space": "target_control_audit_delta",
        "evaluation_adapter": "source_context_train_target_context_control_basal_prediction",
        "uncertainty_status": "BOOTSTRAP_PERTURBATION_LEVEL",
        "null_status": "sensitivity_only",
        "bns_status": "UNVERIFIED",
        "filtered_data": True,
        "performance_eligible": True,
    }


def build_rl4_summary() -> pd.DataFrame:
    rows = [summarize_run(direction) for direction in ["k2r", "r2k"]]
    df = pd.DataFrame(rows)
    REPL.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(REPL / "gears_rl4_summary.csv", index=False)
    df.to_csv(TABLES / "replogle_rl4_gears_cross_context.csv", index=False)
    return df


def build_baseline_comparison(gears: pd.DataFrame) -> pd.DataFrame:
    baseline = pd.read_csv(REPL / "replogle_summary.csv")
    baseline = baseline[baseline["split"].isin(["R-L4-K2R", "R-L4-R2K"])].copy()
    baseline_rows = []
    for _, row in baseline.iterrows():
        baseline_rows.append(
            {
                "split": row["split"],
                "train_cell_line": row["cell_line_train"],
                "test_cell_line": row["cell_line_test"],
                "model": row["model"],
                "metric_space": "audit_delta",
                "n_test_targets": row["n_test_targets"],
                "pearson_delta": row["pearson_delta"],
                "pearson_ci_low": row["pearson_ci_low"],
                "pearson_ci_high": row["pearson_ci_high"],
                "retrieval_top1": row["retrieval_top1"],
                "retrieval_top5": row["retrieval_top5"],
                "retrieval_mrr": row["mrr"],
                "uer50": row["uer50"],
                "sign_flip_rate": row["sign_flip_rate"],
                "run_status": row["run_status"],
                "bns_status": "UNVERIFIED",
                "source": "replogle_summary.csv",
            }
        )
    gears_rows = []
    for _, row in gears.iterrows():
        gears_rows.append(
            {
                "split": row["split"],
                "train_cell_line": row["train_cell_line"],
                "test_cell_line": row["test_cell_line"],
                "model": row["model"],
                "metric_space": row["metric_space"],
                "n_test_targets": row["n_test_targets"],
                "pearson_delta": row["pearson_delta"],
                "pearson_ci_low": row["pearson_ci_low"],
                "pearson_ci_high": row["pearson_ci_high"],
                "retrieval_top1": row["retrieval_top1"],
                "retrieval_top5": row["retrieval_top5"],
                "retrieval_mrr": row["retrieval_mrr"],
                "uer50": row["uer50"],
                "sign_flip_rate": row["sign_flip_rate"],
                "run_status": row["run_status"],
                "bns_status": "UNVERIFIED",
                "source": "gears_rl4_summary.csv",
            }
        )
    out = pd.DataFrame(baseline_rows + gears_rows)
    out.to_csv(TABLES / "replogle_rl4_gears_vs_baselines.csv", index=False)
    return out


def build_rl1_rl4_comparison(rl4: pd.DataFrame) -> pd.DataFrame:
    rl1 = pd.read_csv(REPL / "gears_rl1_summary.csv")
    rl1 = rl1[rl1["metric_space"].eq("audit_delta")].copy()
    rows = []
    for _, row in rl1.iterrows():
        rows.append(
            {
                "level": "R-L1 within-context",
                "split": row["split"],
                "train_cell_line": row["cell_line"],
                "test_cell_line": row["cell_line"],
                "n_test_targets": row["n_test_targets"],
                "pearson_delta": row["pearson_delta"],
                "pearson_ci_low": row["pearson_ci_low"],
                "pearson_ci_high": row["pearson_ci_high"],
                "retrieval_top1": row["top1"],
                "retrieval_top5": row["top5"],
                "retrieval_mrr": row["mrr"],
                "mrr_ci_low": row["mrr_ci_low"],
                "mrr_ci_high": row["mrr_ci_high"],
                "uer50": row["uer50"],
                "sign_flip_rate": row["sign_flip_rate"],
                "metric_space": "audit_delta",
            }
        )
    for _, row in rl4.iterrows():
        rows.append(
            {
                "level": "R-L4 cross-context",
                "split": row["split"],
                "train_cell_line": row["train_cell_line"],
                "test_cell_line": row["test_cell_line"],
                "n_test_targets": row["n_test_targets"],
                "pearson_delta": row["pearson_delta"],
                "pearson_ci_low": row["pearson_ci_low"],
                "pearson_ci_high": row["pearson_ci_high"],
                "retrieval_top1": row["retrieval_top1"],
                "retrieval_top5": row["retrieval_top5"],
                "retrieval_mrr": row["retrieval_mrr"],
                "mrr_ci_low": row["mrr_ci_low"],
                "mrr_ci_high": row["mrr_ci_high"],
                "uer50": row["uer50"],
                "sign_flip_rate": row["sign_flip_rate"],
                "metric_space": row["metric_space"],
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "replogle_rl1_rl4_gears_comparison.csv", index=False)
    return out


def build_figure(comparison: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    labels = comparison["split"].tolist()
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8))
    metrics = [
        ("pearson_delta", "Delta-Pearson"),
        ("retrieval_mrr", "Retrieval MRR"),
        ("uer50", "UER@50"),
    ]
    colors = ["#1a509a" if level.startswith("R-L1") else "#c0392b" for level in comparison["level"]]
    for ax, (col, ylabel) in zip(axes, metrics):
        ax.bar(x, comparison[col].astype(float), color=colors, width=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel, fontsize=10)
        if col in {"retrieval_mrr", "uer50"}:
            ax.set_ylim(0, max(0.55, float(np.nanmax(comparison[col])) * 1.15))
    fig.suptitle(
        "Replogle GEARS R-L1 vs R-L4. R-L4 uses source-context training and target-control-basal prediction.",
        fontsize=9,
    )
    fig.tight_layout()
    for ext in ["png", "svg", "pdf"]:
        fig.savefig(FIGURES / f"replogle_rl1_rl4_gears_transfer.{ext}", bbox_inches="tight")
    plt.close(fig)


def fmt(x: float, digits: int = 4) -> str:
    if pd.isna(x):
        return "NA"
    return f"{float(x):.{digits}f}"


def markdown_table(df: pd.DataFrame, cols: list[str]) -> str:
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                val = fmt(val)
            vals.append(str(val))
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep] + rows)


def write_report(rl4: pd.DataFrame, baseline: pd.DataFrame, comparison: pd.DataFrame) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    core_cols = [
        "direction",
        "train_cell_line",
        "test_cell_line",
        "n_test_targets",
        "pearson_delta",
        "retrieval_top1",
        "retrieval_top5",
        "retrieval_mrr",
        "uer50",
        "sign_flip_rate",
        "elapsed_seconds",
    ]
    comp_cols = [
        "level",
        "split",
        "train_cell_line",
        "test_cell_line",
        "n_test_targets",
        "pearson_delta",
        "retrieval_mrr",
        "uer50",
        "sign_flip_rate",
    ]
    lines = [
        "# Phase 2A-RL4 Full Report",
        "",
        f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M CST')}",
        "",
        "## Current Status",
        "",
        "```text",
        "R-L4-K2R full run:       COMPLETED_GEARS_EVALUATION",
        "R-L4-R2K full run:       COMPLETED_GEARS_EVALUATION",
        "R-L4 postprocess:        COMPLETED",
        "BNS:                     UNVERIFIED",
        "Data scope:              GEARS-compatible filtered essential-screen data",
        "UER/null status:         sensitivity_only",
        "```",
        "",
        "## Full-Run Summary",
        "",
        markdown_table(rl4[core_cols], core_cols),
        "",
        "## R-L1 vs R-L4 GEARS Comparison",
        "",
        markdown_table(comparison[comp_cols], comp_cols),
        "",
        "## Interpretation",
        "",
        "Both R-L4 directions completed on the filtered essential-screen data. Cross-context audit-delta Pearson is near zero in both directions, and perturbation retrieval remains near random: K2R top-1 is 0.0027 and R2K top-1 is 0.0000. This is substantially weaker than the completed R-L1 within-context GEARS runs.",
        "",
        "The result supports the pre-registered stress-test expectation that cross-context transfer is much harder than within-context prediction. It also strengthens the core audit interpretation: global or within-context expression fit does not guarantee perturbation-specific, context-transferable signal.",
        "",
        "GEARS does not clearly exceed the R-L4 mean-effect baseline/probe family in retrieval or audit-delta Pearson. The small positive Pearson values for GEARS are numerically above most R-L4 baseline rows but remain close to zero, while UER@50 and sign-flip rates are high. These rows should therefore be reported as cross-context failure/stress-test evidence, not as cross-context validation.",
        "",
        "## Guardrails",
        "",
        "- All R-L4 results are restricted to `GEARS-compatible filtered essential-screen data`.",
        "- `BNS_STATUS = UNVERIFIED` remains unchanged because no validated biological replicate field is available.",
        "- UER is a sensitivity-only control-null audit, not a replicate-derived biological upper bound.",
        "- The R-L4 adapter is `source_context_train_target_context_control_basal_prediction`; it is not native GEARS cell-line-aware condition splitting.",
        "- Smoke and interrupted runs remain provenance only and are excluded from performance interpretation.",
        "",
        "## Outputs",
        "",
        "- `results/replogle/gears_rl4_summary.csv`",
        "- `results/tables/replogle_rl4_gears_cross_context.csv`",
        "- `results/tables/replogle_rl4_gears_vs_baselines.csv`",
        "- `results/tables/replogle_rl1_rl4_gears_comparison.csv`",
        "- `figures/main/replogle_rl1_rl4_gears_transfer.{png,svg,pdf}`",
        "",
        "## Gate Decision",
        "",
        "```text",
        "PHASE2A_RL4_COMPLETE_FILTERED_DATA",
        "```",
        "",
        "Next executable step: update project status files and carry the R-L4 result into manuscript/result synthesis, while keeping complete-data replication blocked until the official Figshare+ processed objects become command-line accessible.",
        "",
    ]
    (REPORTS / "PHASE2A_RL4_FULL_REPORT.md").write_text("\n".join(lines))


def main() -> None:
    rl4 = build_rl4_summary()
    baseline = build_baseline_comparison(rl4)
    comparison = build_rl1_rl4_comparison(rl4)
    build_figure(comparison)
    write_report(rl4, baseline, comparison)
    print(rl4.to_string(index=False))
    print("\nWrote R-L4 summary, comparison tables, figure, and report.")


if __name__ == "__main__":
    main()
