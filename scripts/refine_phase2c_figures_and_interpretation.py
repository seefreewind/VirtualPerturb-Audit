from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"
FIGURES = ROOT / "figures/main"
REPORTS = ROOT / "reports"

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


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "font.size": 12,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 1.8,
            "legend.frameon": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    )


def save(fig, basename: Path, formats: list[str]) -> None:
    basename.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=1.1)
    for fmt in formats:
        fig.savefig(basename.with_suffix("." + fmt), dpi=450, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def fmt(value: object, digits: int = 4) -> str:
    if value is None or pd.isna(value):
        return "NA"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.{digits}f}"
    return str(value)


def md_table(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def load_primary() -> pd.DataFrame:
    df = pd.read_csv(TABLES / "state_phase2c_primary_metrics.csv")
    return df[df["metric_space"].isin(["audit_delta", "target_control_audit_delta"])].copy()


def load_transfer() -> pd.DataFrame:
    return pd.read_csv(TABLES / "state_transfer_drop.csv")


def load_perturbation_metrics() -> pd.DataFrame:
    df = pd.read_csv(TABLES / "state_phase2c_perturbation_metrics.csv")
    return df[df["space"].isin(["audit_delta", "target_control_audit_delta"])].copy()


def plot_phase2c_state_summary(primary: pd.DataFrame, transfer: pd.DataFrame, perturb: pd.DataFrame) -> None:
    style()
    fig = plt.figure(figsize=(14.2, 8.6))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.12], width_ratios=[1.0, 1.0, 1.05, 1.05])
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2:])
    ax_d = fig.add_subplot(gs[1, :2])
    ax_e = fig.add_subplot(gs[1, 2:])

    order = [
        "Norman L1 STATE",
        "Norman L2 STATE",
        "Replogle K562 R-L1 STATE",
        "Replogle K562 -> RPE1 R-L4 STATE",
    ]
    labels = ["Norman\nL1", "Norman\nL2", "K562\nR-L1", "K562->RPE1\nR-L4"]
    primary = primary.set_index("setting").loc[order].reset_index()
    colors = [PALETTE["neutral"], PALETTE["neutral"], PALETTE["blue_main"], PALETTE["red_strong"]]

    for ax, metric, ylabel, title, ylim in [
        (ax_a, "pearson_delta", "Delta-Pearson", "A. STATE target-level agreement", (0, 0.55)),
        (ax_b, "uer50", "UER@50", "B. Unsupported-effect burden", (0, 0.22)),
    ]:
        vals = primary[metric].astype(float).to_numpy()
        err_low = vals - primary[f"{metric.split('_')[0] if metric == 'pearson_delta' else 'uer50'}_ci_low"].astype(float).to_numpy() if metric in {"pearson_delta", "uer50"} else np.zeros_like(vals)
        err_high = primary[f"{metric.split('_')[0] if metric == 'pearson_delta' else 'uer50'}_ci_high"].astype(float).to_numpy() - vals if metric in {"pearson_delta", "uer50"} else np.zeros_like(vals)
        ax.bar(range(len(vals)), vals, color=colors, edgecolor="black", linewidth=1.0)
        ax.errorbar(range(len(vals)), vals, yerr=np.vstack([err_low, err_high]), fmt="none", ecolor=PALETTE["dark"], elinewidth=1.2, capsize=3)
        for i, val in enumerate(vals):
            ax.text(i, val + (ylim[1] * 0.025), f"{val:.3f}", ha="center", va="bottom", fontsize=9)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylabel(ylabel)
        ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
        ax.set_ylim(*ylim)

    matched = transfer.set_index("metric")
    contrast_metrics = ["pearson_delta", "spearman_delta", "cosine_delta", "uer50", "sign_flip_rate"]
    contrast_labels = ["Pearson", "Spearman", "Cosine", "UER@50", "Sign flip"]
    vals = matched.loc[contrast_metrics, "mean_drop_source_minus_cross"].astype(float).to_numpy()
    lows = matched.loc[contrast_metrics, "ci95_low"].astype(float).to_numpy()
    highs = matched.loc[contrast_metrics, "ci95_high"].astype(float).to_numpy()
    ccolors = [PALETTE["blue_main"], PALETTE["blue_secondary"], PALETTE["teal"], PALETTE["red_strong"], PALETTE["red_strong"]]
    ax_c.barh(range(len(vals)), vals, color=ccolors, edgecolor="black", linewidth=1.0)
    ax_c.errorbar(vals, range(len(vals)), xerr=np.vstack([vals - lows, highs - vals]), fmt="none", ecolor=PALETTE["dark"], elinewidth=1.2, capsize=3)
    ax_c.axvline(0, color=PALETTE["dark"], linewidth=1)
    ax_c.set_yticks(range(len(vals)))
    ax_c.set_yticklabels(contrast_labels, fontsize=9)
    ax_c.set_xlabel("R-L1 minus R-L4")
    ax_c.set_title("C. Matched-target STATE contrast", loc="left", fontsize=12, fontweight="bold")
    ax_c.set_xlim(min(-0.13, float(np.nanmin(lows)) - 0.02), max(0.19, float(np.nanmax(highs)) + 0.02))

    repl = perturb[
        perturb["run_id"].isin(["S3_replogle_k562_rl1", "S4_replogle_k562_to_rpe1_rl4"])
        & perturb["space"].isin(["audit_delta", "target_control_audit_delta"])
    ].copy()
    repl["task"] = repl["run_id"].map({"S3_replogle_k562_rl1": "K562 R-L1", "S4_replogle_k562_to_rpe1_rl4": "K562->RPE1 R-L4"})
    positions = {"K562 R-L1": 0, "K562->RPE1 R-L4": 1}
    rng = np.random.default_rng(7)
    for task, grp in repl.groupby("task"):
        x = positions[task] + rng.normal(0, 0.045, size=len(grp))
        ax_d.scatter(x, grp["pearson_delta"].astype(float), s=16, alpha=0.45, color=PALETTE["blue_main"] if task == "K562 R-L1" else PALETTE["red_strong"], linewidth=0)
        ax_d.boxplot(
            grp["pearson_delta"].astype(float),
            positions=[positions[task]],
            widths=0.32,
            showfliers=False,
            patch_artist=True,
            boxprops={"facecolor": "white", "edgecolor": "black", "linewidth": 1.2},
            medianprops={"color": "black", "linewidth": 1.4},
            whiskerprops={"color": "black", "linewidth": 1.0},
            capprops={"color": "black", "linewidth": 1.0},
        )
    ax_d.axhline(0, color=PALETTE["dark"], linewidth=1)
    ax_d.set_xticks([0, 1])
    ax_d.set_xticklabels(["Replogle K562\nR-L1 (216 targets)", "Replogle K562->RPE1\nR-L4 (73 targets)"])
    ax_d.set_ylabel("Per-target delta-Pearson")
    ax_d.set_title("D. Replogle target-level distribution", loc="left", fontsize=12, fontweight="bold")
    ax_d.set_xlim(-0.45, 1.45)
    ax_d.set_ylim(-0.25, 0.8)

    s3 = repl[repl["run_id"].eq("S3_replogle_k562_rl1")].set_index("perturbation")
    s4 = repl[repl["run_id"].eq("S4_replogle_k562_to_rpe1_rl4")].set_index("perturbation")
    common = sorted(set(s3.index) & set(s4.index))
    for pert in common:
        y0 = float(s3.loc[pert, "pearson_delta"])
        y1 = float(s4.loc[pert, "pearson_delta"])
        ax_e.plot([0, 1], [y0, y1], color=PALETTE["neutral"], linewidth=1.0, alpha=0.85)
        ax_e.scatter([0], [y0], color=PALETTE["blue_main"], s=26, edgecolor="black", linewidth=0.4, zorder=3)
        ax_e.scatter([1], [y1], color=PALETTE["red_strong"], s=26, edgecolor="black", linewidth=0.4, zorder=3)
    ax_e.plot(
        [0, 1],
        [float(s3.loc[common, "pearson_delta"].mean()), float(s4.loc[common, "pearson_delta"].mean())],
        color=PALETTE["dark"],
        linewidth=2.4,
        zorder=4,
    )
    ax_e.axhline(0, color=PALETTE["dark"], linewidth=1)
    ax_e.set_xticks([0, 1])
    ax_e.set_xticklabels(["Matched K562\nR-L1", "Matched K562->RPE1\nR-L4"])
    ax_e.set_ylabel("Per-target delta-Pearson")
    ax_e.set_title("E. Matched targets paired by perturbation", loc="left", fontsize=12, fontweight="bold")
    ax_e.set_xlim(-0.25, 1.25)
    ax_e.set_ylim(-0.25, 0.8)

    save(fig, FIGURES / "phase2c_state_interpretation", ["pdf", "svg", "png"])


def plot_gears_state_directionality() -> None:
    style()
    comp = pd.read_csv(TABLES / "gears_state_primary_comparison.csv")
    keep = comp[comp["setting"].isin([
        "Replogle K562 R-L1 GEARS",
        "Replogle K562 -> RPE1 R-L4 GEARS",
        "Replogle K562 R-L1 STATE",
        "Replogle K562 -> RPE1 R-L4 STATE",
    ])].copy()
    keep["model_level"] = keep["setting"].map(
        {
            "Replogle K562 R-L1 GEARS": "GEARS R-L1",
            "Replogle K562 -> RPE1 R-L4 GEARS": "GEARS R-L4",
            "Replogle K562 R-L1 STATE": "STATE R-L1",
            "Replogle K562 -> RPE1 R-L4 STATE": "STATE R-L4",
        }
    )
    order = ["GEARS R-L1", "GEARS R-L4", "STATE R-L1", "STATE R-L4"]
    keep = keep.set_index("model_level").loc[order].reset_index()
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.6))
    metrics = [("pearson_delta", "Delta-Pearson"), ("uer50", "UER@50"), ("sign_flip_rate", "Sign flip")]
    colors = [PALETTE["blue_main"], PALETTE["red_strong"], PALETTE["blue_secondary"], PALETTE["red_1"]]
    for ax, (metric, ylabel) in zip(axes, metrics):
        vals = keep[metric].astype(float).to_numpy()
        ax.bar(range(len(vals)), vals, color=colors, edgecolor="black", linewidth=1.0)
        for i, val in enumerate(vals):
            ax.text(i, val, f"{val:.3f}", ha="center", va="bottom", fontsize=8)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(order, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel, fontsize=11, fontweight="bold")
        ax.set_ylim(0, max(0.08, float(np.nanmax(vals)) * 1.25))
    save(fig, FIGURES / "phase2c_gears_state_directionality", ["pdf", "svg", "png"])


def write_interpretation_report(primary: pd.DataFrame, transfer: pd.DataFrame) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    primary_show = primary[
        [
            "setting",
            "split",
            "metric_space",
            "n_test_perturbations",
            "pearson_delta",
            "pearson_ci_low",
            "pearson_ci_high",
            "retrieval_mrr",
            "uer50",
            "sign_flip_rate",
        ]
    ].copy()
    matched = transfer.set_index("metric")
    text = f"""# Phase 2C Result Interpretation and Figure Notes

Generated: {now}

## Interpretation

The Phase 2C STATE run changes the second-model status from compute-blocked to performance-eligible. The four locked tasks completed, and the synchronized outputs support perturbation-level evaluation with the same endpoint family used in the GEARS audit.

The main scientific reading is partial cross-architecture support. STATE shows a lower Replogle cross-context Pearson than within-context K562 in the full summary, and the matched-target subset strengthens this direction: Pearson drops by {fmt(matched.loc['pearson_delta', 'mean_drop_source_minus_cross'])} with a 95% interval of [{fmt(matched.loc['pearson_delta', 'ci95_low'])}, {fmt(matched.loc['pearson_delta', 'ci95_high'])}]. Spearman and cosine show the same direction. The sign-flip rate is also worse in cross-context transfer, with source-minus-cross difference {fmt(matched.loc['sign_flip_rate', 'mean_drop_source_minus_cross'])}.

The result should not be described as a complete confirmation. Full-summary retrieval MRR is higher in STATE R-L4 than STATE R-L1, and UER@50 is slightly lower in the R-L4 full summary. These mixed endpoints are plausibly influenced by the smaller normalized R-L4 target set. The manuscript should therefore lead with matched-target transfer degradation and state the endpoint-level caveat explicitly.

## Primary STATE Metrics

{md_table(primary_show, ['setting','split','metric_space','n_test_perturbations','pearson_delta','pearson_ci_low','pearson_ci_high','retrieval_mrr','uer50','sign_flip_rate'])}

## Matched-Target Transfer Contrast

Positive values for Pearson, Spearman, and cosine mean within-context R-L1 is higher. Negative values for UER@50 and sign flip mean the lower-is-better endpoint is worse in cross-context R-L4.

{md_table(transfer, ['metric','n_matched_targets','source_mean','cross_context_mean','mean_drop_source_minus_cross','ci95_low','ci95_high'])}

## Figure Decisions

- `phase2c_state_interpretation` is the preferred main Phase 2C explanatory figure. It separates STATE-only performance, matched-target contrast, and target-level distribution.
- Panel E in `phase2c_state_interpretation` pairs the 15 shared Replogle targets, so it is the cleanest visual evidence for the STATE context-transfer Pearson drop.
- `phase2c_gears_state_directionality` is a supplementary or reviewer-response figure. It shows that GEARS and STATE both have lower R-L4 Pearson than R-L1, while preserving the mixed endpoint picture.
- `gears_state_confirmatory_audit` is retained as the original compact comparison, but it should not be the main narrative figure because it places GEARS raw-space and STATE audit-delta values side by side.

## Suggested Caption

Phase 2C STATE cross-architecture audit. STATE was evaluated on the locked Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4 tasks using audit-delta endpoints. In Replogle, cross-context transfer showed lower target-level agreement than within-context K562, and the matched-target contrast confirmed a Pearson drop with perturbation-level bootstrap uncertainty. Retrieval and UER endpoints were mixed in the full-summary table, so the result supports a bounded, partial architecture-independent transfer-degradation claim.
"""
    (REPORTS / "PHASE2C_RESULT_INTERPRETATION.md").write_text(text, encoding="utf-8")


def main() -> None:
    primary = load_primary()
    transfer = load_transfer()
    perturb = load_perturbation_metrics()
    plot_phase2c_state_summary(primary, transfer, perturb)
    plot_gears_state_directionality()
    write_interpretation_report(primary, transfer)
    print("phase2c_refined_figures_and_interpretation_ok")


if __name__ == "__main__":
    main()
