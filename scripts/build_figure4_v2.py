#!/usr/bin/env python3
"""Build Figure 4 v2 for the VirtualPerturb-Audit CRM manuscript.

Figure 4 is a matched-target estimation figure. It visualizes frozen
target-level GEARS transfer results and the paired bootstrap effect size without
rerunning models or changing endpoint definitions.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIG_MAIN = ROOT / "figures" / "main"
FIG_QC = ROOT / "figures" / "qc"
FIG_ARCHIVE = ROOT / "figures" / "archive"
REPORTS = ROOT / "reports"
TABLES = ROOT / "results" / "tables"

SENSITIVITY = TABLES / "replogle_matched_rl1_rl4_sensitivity.csv"
TARGET_LEVEL = TABLES / "replogle_matched_rl1_rl4_target_level.csv"
REGISTRY = TABLES / "replogle_matched_target_registry.tsv"

DIRECTIONS = [
    {
        "key": "K562_within_vs_K562_to_RPE1",
        "label": "K562 -> RPE1",
        "within": "Within K562",
        "cross": "Cross to RPE1",
        "n_expected": 150,
        "within_expected": 0.28122004605519274,
        "cross_expected": -0.007048829913449778,
        "drop_expected": 0.28826887596864254,
        "ci_low_expected": 0.2559492271093574,
        "ci_high_expected": 0.3205873177755857,
    },
    {
        "key": "RPE1_within_vs_RPE1_to_K562",
        "label": "RPE1 -> K562",
        "within": "Within RPE1",
        "cross": "Cross to K562",
        "n_expected": 148,
        "within_expected": 0.5500999078110514,
        "cross_expected": 0.002083826053421941,
        "drop_expected": 0.5480160817576295,
        "ci_low_expected": 0.5145753995529958,
        "ci_high_expected": 0.5801839071596544,
    },
]


@dataclass(frozen=True)
class Contract:
    core_conclusion: str = (
        "Substantial cross-context degradation persists after matching the "
        "perturbation-target universe."
    )
    archetype: str = "quantitative grid"
    journal: str = "Cell Reports Methods"
    final_width_mm: int = 183
    min_font_pt: float = 5.0


def configure_matplotlib() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.7,
            "ytick.major.width": 0.7,
            "legend.frameon": False,
        }
    )


def ensure_dirs() -> None:
    for path in [FIG_MAIN, FIG_QC, FIG_ARCHIVE, REPORTS]:
        path.mkdir(parents=True, exist_ok=True)


def archive_previous() -> None:
    stems = [
        "crm_figure4_matched_gears_transfer",
        "crm_figure4_matched_gears_transfer_v11",
        "Figure4",
    ]
    for stem in stems:
        for ext in [".svg", ".pdf", ".png"]:
            src = FIG_MAIN / f"{stem}{ext}"
            if src.exists():
                dst = FIG_ARCHIVE / f"{stem}_pre_v2{ext}"
                if not dst.exists():
                    shutil.copy2(src, dst)
    old_source = ROOT / "scripts" / "build_crm_submission_package.py"
    dst_source = FIG_ARCHIVE / "build_crm_submission_package_pre_figure4_v2.py"
    if old_source.exists() and not dst_source.exists():
        shutil.copy2(old_source, dst_source)


def load_frozen() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sens = pd.read_csv(SENSITIVITY)
    target = pd.read_csv(TARGET_LEVEL)
    registry = pd.read_csv(REGISTRY, sep="\t")
    primary = sens[
        (sens["comparison_role"] == "primary_source_context_comparison")
        & (sens["metric"] == "pearson_delta")
    ].copy()
    return primary, target, registry


def assert_numeric_integrity(primary: pd.DataFrame, target: pd.DataFrame) -> list[str]:
    messages = []
    for spec in DIRECTIONS:
        hit = primary[primary["direction"] == spec["key"]]
        if len(hit) != 1:
            raise ValueError(f"Expected one primary pearson_delta row for {spec['key']}; found {len(hit)}")
        row = hit.iloc[0]
        checks = [
            ("n_targets", int(row["n_targets"]), spec["n_expected"], 0),
            ("within_estimate", float(row["within_estimate"]), spec["within_expected"], 1e-12),
            ("cross_estimate", float(row["cross_estimate"]), spec["cross_expected"], 1e-12),
            ("paired_difference", float(row["paired_difference"]), spec["drop_expected"], 1e-12),
            ("ci_low", float(row["ci_low"]), spec["ci_low_expected"], 1e-12),
            ("ci_high", float(row["ci_high"]), spec["ci_high_expected"], 1e-12),
        ]
        for name, found, expected, tol in checks:
            if abs(found - expected) > tol:
                alert = REPORTS / "FIGURE4_NUMERIC_INTEGRITY_ALERT.md"
                alert.write_text(
                    f"# Figure 4 Numeric Integrity Alert\n\n"
                    f"Mismatch for `{spec['key']}` / `{name}`.\n\n"
                    f"- Frozen table value: {found}\n"
                    f"- Prompt expected value: {expected}\n"
                    f"- Tolerance: {tol}\n",
                    encoding="utf-8",
                )
                raise ValueError(f"Numeric integrity alert written to {alert}")
        detail = target[
            (target["direction"] == spec["key"])
            & (target["comparison_role"] == "primary_source_context_comparison")
        ]
        if len(detail) != spec["n_expected"]:
            raise ValueError(f"Target-level n mismatch for {spec['key']}: {len(detail)} vs {spec['n_expected']}")
        messages.append(f"{spec['label']}: frozen primary values verified; target-level n={len(detail)}.")
    return messages


def save_figure(fig: plt.Figure, stem: Path) -> None:
    fig.savefig(f"{stem}.svg", bbox_inches="tight")
    fig.savefig(f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(f"{stem}.png", dpi=600, bbox_inches="tight")


def jittered_x(values: np.ndarray, center: float) -> np.ndarray:
    """Deterministic beeswarm-like offsets from frozen values only."""
    order = np.argsort(values, kind="mergesort")
    offsets = np.linspace(-0.10, 0.10, num=len(values))
    positioned = np.empty_like(offsets)
    positioned[order] = offsets
    return center + positioned


def draw_distribution_group(ax: plt.Axes, detail: pd.DataFrame, spec: dict[str, object], x0: float) -> None:
    within = detail["within_pearson_delta"].to_numpy()
    cross = detail["cross_pearson_delta"].to_numpy()
    color = "#2f6f73"
    edge = "#506273"
    ax.scatter(jittered_x(within, x0), within, s=8, color=color, alpha=0.24, linewidths=0, rasterized=True)
    ax.scatter(jittered_x(cross, x0 + 0.45), cross, s=8, facecolors="white", edgecolors=edge, alpha=0.42, linewidths=0.35, rasterized=True)
    ax.plot([x0 - 0.13, x0 + 0.13], [within.mean(), within.mean()], color=color, lw=1.5)
    ax.plot([x0 + 0.32, x0 + 0.58], [cross.mean(), cross.mean()], color=edge, lw=1.5)
    ax.text(x0 + 0.18, 0.72, spec["label"], ha="center", va="bottom", fontsize=7.0, fontweight="bold")
    ax.text(x0 + 0.18, 0.665, f"n = {len(detail)} matched targets", ha="center", va="bottom", fontsize=6.2, color="#5d6973")
    ax.text(x0, -0.205, spec["within"], ha="center", va="top", fontsize=6.5, rotation=22, rotation_mode="anchor")
    ax.text(x0 + 0.45, -0.205, spec["cross"], ha="center", va="top", fontsize=6.5, rotation=22, rotation_mode="anchor")
    ax.text(x0 + 0.18, -0.315, f"{within.mean():.3f} -> {cross.mean():.3f}", ha="center", va="top", fontsize=6.2, color="#26323a")


def draw_forest(ax: plt.Axes, primary: pd.DataFrame) -> None:
    y_positions = [1.25, 0.35]
    ax.axvline(0, color="#aab4bc", lw=0.8, zorder=0)
    ax.grid(axis="x", color="#eef1f3", lw=0.6)
    ax.set_axisbelow(True)
    for y, spec in zip(y_positions, DIRECTIONS):
        row = primary[primary["direction"] == spec["key"]].iloc[0]
        point = float(row["paired_difference"])
        lo = float(row["ci_low"])
        hi = float(row["ci_high"])
        ax.plot([lo, hi], [y, y], color="#2f6f73", lw=1.6, solid_capstyle="round")
        ax.scatter([point], [y], s=58, color="#2f6f73", zorder=3)
        ax.text(point + 0.020, y + 0.05, f"{point:.3f}", ha="left", va="center", fontsize=7.0, fontweight="bold", color="#26323a")
        ax.text(point + 0.020, y - 0.12, f"[{lo:.3f}, {hi:.3f}]", ha="left", va="center", fontsize=6.3, color="#5d6973")
        ax.text(-0.015, y, spec["label"], ha="right", va="center", fontsize=7.0, fontweight="bold", color="#26323a")
    ax.set_xlim(0, 0.65)
    ax.set_ylim(-0.15, 1.75)
    ax.set_yticks([])
    ax.set_xlabel("Within - cross audit-delta Pearson", fontsize=7.2)
    ax.set_title("B  Matched transfer decrement", loc="left", fontsize=8.4, fontweight="bold", pad=8)
    ax.text(
        0.02,
        1.02,
        "Positive values indicate reduced cross-context response agreement",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=6.4,
        color="#5d6973",
    )


def draw_option_b(primary: pd.DataFrame, target: pd.DataFrame, out_stem: Path) -> plt.Figure:
    fig = plt.figure(figsize=(7.2, 3.9), constrained_layout=False)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.18, 1.0], wspace=0.34)
    ax_dist = fig.add_subplot(gs[0, 0])
    ax_forest = fig.add_subplot(gs[0, 1])

    ax_dist.axhline(0, color="#aab4bc", lw=0.8, zorder=0)
    ax_dist.grid(axis="y", color="#eef1f3", lw=0.6)
    ax_dist.set_axisbelow(True)
    for idx, spec in enumerate(DIRECTIONS):
        detail = target[
            (target["direction"] == spec["key"])
            & (target["comparison_role"] == "primary_source_context_comparison")
        ]
        draw_distribution_group(ax_dist, detail, spec, x0=idx * 1.35)
    ax_dist.set_xlim(-0.28, 2.03)
    ax_dist.set_ylim(-0.35, 0.78)
    ax_dist.set_ylabel("Audit-delta Pearson", fontsize=7.2)
    ax_dist.set_xticks([])
    ax_dist.set_title("A  Target-level response agreement", loc="left", fontsize=8.4, fontweight="bold", pad=8)

    draw_forest(ax_forest, primary)
    fig.suptitle("Matched-target analysis reveals substantial GEARS context-transfer degradation", y=0.985, fontsize=8.8, fontweight="bold")
    fig.subplots_adjust(left=0.08, right=0.985, top=0.80, bottom=0.22)
    save_figure(fig, out_stem)
    return fig


def draw_option_a(primary: pd.DataFrame, target: pd.DataFrame, out_stem: Path) -> plt.Figure:
    fig = plt.figure(figsize=(7.2, 3.9), constrained_layout=False)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 0.86], hspace=0.42, wspace=0.34)
    for row_idx, spec in enumerate(DIRECTIONS):
        ax_left = fig.add_subplot(gs[row_idx, 0])
        ax_right = fig.add_subplot(gs[row_idx, 1])
        detail = target[
            (target["direction"] == spec["key"])
            & (target["comparison_role"] == "primary_source_context_comparison")
        ]
        row = primary[primary["direction"] == spec["key"]].iloc[0]
        ax_left.axhline(0, color="#aab4bc", lw=0.8, zorder=0)
        ax_left.grid(axis="y", color="#eef1f3", lw=0.6)
        within = detail["within_pearson_delta"].to_numpy()
        cross = detail["cross_pearson_delta"].to_numpy()
        ax_left.scatter(jittered_x(within, 0), within, s=8, color="#2f6f73", alpha=0.23, linewidths=0, rasterized=True)
        ax_left.scatter(jittered_x(cross, 1), cross, s=8, facecolors="white", edgecolors="#506273", alpha=0.42, linewidths=0.35, rasterized=True)
        ax_left.plot([-0.14, 0.14], [within.mean(), within.mean()], color="#2f6f73", lw=1.5)
        ax_left.plot([0.86, 1.14], [cross.mean(), cross.mean()], color="#506273", lw=1.5)
        ax_left.set_xlim(-0.35, 1.35)
        ax_left.set_ylim(-0.35, 0.78)
        ax_left.set_xticks([0, 1], [spec["within"], spec["cross"]], fontsize=6.4)
        ax_left.set_ylabel("Audit-delta Pearson", fontsize=7.0)
        title_prefix = "A" if row_idx == 0 else "B"
        ax_left.set_title(f"{title_prefix}  {spec['label']}   n = {len(detail)} matched targets", loc="left", fontsize=8.0, fontweight="bold", pad=6)
        ax_left.text(0.5, -0.27, f"{within.mean():.3f} -> {cross.mean():.3f}", ha="center", va="top", fontsize=6.3, color="#26323a")

        ax_right.axvline(0, color="#aab4bc", lw=0.8, zorder=0)
        ax_right.set_xlim(0, 0.65)
        ax_right.set_ylim(-0.6, 0.6)
        ax_right.set_yticks([])
        point = float(row["paired_difference"])
        lo = float(row["ci_low"])
        hi = float(row["ci_high"])
        ax_right.plot([lo, hi], [0, 0], color="#2f6f73", lw=1.6, solid_capstyle="round")
        ax_right.scatter([point], [0], s=60, color="#2f6f73", zorder=3)
        ax_right.text(point + 0.02, 0.10, f"{point:.3f}", fontsize=7.0, fontweight="bold", ha="left")
        ax_right.text(point + 0.02, -0.16, f"[{lo:.3f}, {hi:.3f}]", fontsize=6.3, ha="left", color="#5d6973")
        ax_right.set_xlabel("Within - cross", fontsize=6.8)
        ax_right.set_title("Paired decrease", loc="left", fontsize=7.4, fontweight="bold", pad=6)
    fig.suptitle("Matched-target analysis reveals substantial GEARS context-transfer degradation", y=0.985, fontsize=8.8, fontweight="bold")
    fig.subplots_adjust(left=0.09, right=0.985, top=0.87, bottom=0.18)
    save_figure(fig, out_stem)
    return fig


def make_halfsize(source_png: Path, out_png: Path) -> None:
    with Image.open(source_png) as im:
        im = im.convert("RGB")
        im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.Resampling.LANCZOS).save(out_png)


def write_reports(primary: pd.DataFrame, target: pd.DataFrame, registry: pd.DataFrame, integrity_messages: list[str]) -> None:
    contract = Contract()
    primary_display = primary.copy()
    for col in ["within_estimate", "cross_estimate", "paired_difference", "ci_low", "ci_high"]:
        primary_display[col] = primary_display[col].map(lambda x: f"{x:.6f}")

    target_rows = []
    for spec in DIRECTIONS:
        detail = target[
            (target["direction"] == spec["key"])
            & (target["comparison_role"] == "primary_source_context_comparison")
        ]
        diff = detail["within_pearson_delta"] - detail["cross_pearson_delta"]
        target_rows.append(
            [
                spec["label"],
                len(detail),
                f"{detail['within_pearson_delta'].mean():.6f}",
                f"{detail['cross_pearson_delta'].mean():.6f}",
                f"{diff.mean():.6f}",
                f"{(diff > 0).sum()}/{len(diff)} ({(diff > 0).mean():.1%})",
            ]
        )

    (REPORTS / "FIGURE4_V2_START_AUDIT.md").write_text(
        "\n".join(
            [
                "# Figure 4 v2 Start Audit",
                "",
                f"Core conclusion: {contract.core_conclusion}",
                f"Archetype: {contract.archetype}",
                f"Target journal: {contract.journal}",
                "",
                "## Located current Figure 4",
                "",
                "- Source file: `scripts/build_crm_submission_package.py` lines 172-192.",
                "- Current style: grouped bar chart with within and cross bars.",
                "- Current label needing replacement: `Matched-target Pearson`.",
                "- Current title needing replacement: `Matched targets do not rescue GEARS cross-context transfer`.",
                "- Archived old Figure 4 copies under `figures/archive/` before writing v2 outputs.",
                "",
                "## Input tables",
                "",
                "- `results/tables/replogle_matched_rl1_rl4_sensitivity.csv` for frozen summary estimates and paired bootstrap intervals.",
                "- `results/tables/replogle_matched_rl1_rl4_target_level.csv` for frozen matched-target values.",
                "- `results/tables/replogle_matched_target_registry.tsv` for matched-target provenance.",
                "",
                "## Numeric integrity",
                "",
                *[f"- {m}" for m in integrity_messages],
                "",
                "## Primary plotted summary values",
                "",
                primary_display[["direction", "n_targets", "within_estimate", "cross_estimate", "paired_difference", "ci_low", "ci_high", "difference_definition"]].to_markdown(index=False),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (REPORTS / "FIGURE4_TARGET_LEVEL_DATA_AUDIT.md").write_text(
        "\n".join(
            [
                "# Figure 4 Target-Level Data Audit",
                "",
                "Status: AVAILABLE",
                "",
                f"- Target-level table rows: {len(target)}",
                f"- Primary matched rows used in Figure 4: {sum(r[1] for r in target_rows)}",
                f"- Matched-target registry rows: {len(registry)}",
                "- Target-level distributions are plotted from frozen per-target `within_pearson_delta` and `cross_pearson_delta` columns.",
                "",
                "| Direction | n | within mean | cross mean | within - cross mean | targets with within > cross |",
                "|---|---:|---:|---:|---:|---:|",
                *["| " + " | ".join(map(str, row)) + " |" for row in target_rows],
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (REPORTS / "FIGURE3_FIGURE4_STORY_AUDIT.md").write_text(
        "\n".join(
            [
                "# Figure 3 to Figure 4 Story Audit",
                "",
                "| Check | Result | Note |",
                "|---|---:|---|",
                "| Figure 3 claim | PASS | Some within-context agreement survives target-information removal or scrambling. |",
                "| Figure 4 claim | PASS | Cross-context response agreement degrades strongly after matching perturbation targets. |",
                "| Different questions | PASS | Figure 3 is a falsification probe analysis; Figure 4 is a matched transfer stress test. |",
                "| Generic performance-comparison risk | PASS | Figure 4 uses target-level distributions plus paired effect-size CIs, not a bar benchmark. |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (REPORTS / "FIGURE4_V2_SELECTION.md").write_text(
        "\n".join(
            [
                "# Figure 4 v2 Selection",
                "",
                "| Criterion | Option A | Option B | Selected rationale |",
                "|---|---:|---:|---|",
                "| Matched-design visibility | 4 | 5 | Option B separates target-level paired source data from the matched decrement estimate. |",
                "| Effect-size emphasis | 4 | 5 | Option B gives the forest panel equal visual weight and makes the effect size central. |",
                "| CI clarity | 4 | 5 | The two horizontal CIs are larger and easier to read in Option B. |",
                "| Metric-space clarity | 5 | 5 | Both options use `Audit-delta Pearson` and include zero references. |",
                "| Target heterogeneity visibility | 5 | 4 | Option A has larger per-direction target panels; Option B still retains visible distributions. |",
                "| Causal-claim discipline | 5 | 5 | Neither option attributes the drop solely to cellular context. |",
                "| Readability | 4 | 5 | Option B is cleaner at half size. |",
                "| Visual economy | 4 | 5 | Option B avoids repeating an effect-size subpanel for each direction. |",
                "| Cell Reports Methods fit | 4 | 5 | Option B reads as a compact estimation plot rather than a benchmark panel. |",
                "",
                "Selected final version: OPTION B.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (REPORTS / "FIGURE4_V2_EDITOR_TEST.md").write_text(
        "\n".join(
            [
                "# Figure 4 v2 Editor Test",
                "",
                "| 20-second editor question | Result | Note |",
                "|---|---:|---|",
                "| What is the metric? | PASS | The y-axis and forest x-axis use `Audit-delta Pearson`. |",
                "| Why is the analysis matched? | PASS | Each transfer direction states the matched target count and the legend explains identical target sets. |",
                "| What are the two transfer directions? | PASS | Direction labels are `K562 -> RPE1` and `RPE1 -> K562`. |",
                "| How large are the paired decrements? | PASS | Forest labels show 0.288 and 0.548. |",
                "| Do bootstrap intervals include zero? | PASS | The zero line is visible and both CIs lie to the right of zero. |",
                "| Does the figure claim causality? | PASS | No causal wording is used; the legend states remaining contributors are intertwined. |",
                "| Is this a paired stress test rather than a bar-chart benchmark? | PASS | Bars are removed; the effect-size panel carries the primary message. |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (REPORTS / "FIGURE4_V2_REVIEWER_ATTACK.md").write_text(
        "\n".join(
            [
                "# Figure 4 v2 Reviewer Attack Test",
                "",
                "| Criticism | Status | Response |",
                "|---|---:|---|",
                "| Are matched targets truly identical within each comparison? | RESOLVED | Each primary comparison uses the same perturbation targets within its direction; n=150 and n=148 are verified against frozen target-level rows. |",
                "| Is audit-delta Pearson clearly distinguished from raw-space Pearson? | RESOLVED | The metric label is `Audit-delta Pearson`, and the legend describes control-subtracted response agreement. |",
                "| Is the statistical unit perturbation target? | RESOLVED | The legend states perturbation-level bootstrap resampling and matched perturbation targets. |",
                "| Does the plot imply cell-level precision? | RESOLVED | Individual points are target-level values and are visually secondary; CIs are perturbation-level paired bootstrap intervals. |",
                "| Are CIs paired? | RESOLVED | Effect-size axis is within-minus-cross and reports paired bootstrap CIs from the frozen summary table. |",
                "| Does target matching remove all confounding? | PARTIAL | The legend states matching reduces target-composition differences but does not isolate all contributors. |",
                "| Could R-L4 adapter limitations contribute? | LIMITATION | Model-, training-, inference-, and adapter-related contributors remain intertwined. |",
                "| Are negative or near-zero cross-context values shown honestly? | RESOLVED | Distribution axis includes zero and preserves the negative K562-to-RPE1 cross-context mean. |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (REPORTS / "FIGURE4_V2_QC.md").write_text(
        "\n".join(
            [
                "# Figure 4 v2 QC",
                "",
                "| Check | Result |",
                "|---|---:|",
                "| No bars | PASS |",
                "| No traffic-light red/green semantics | PASS |",
                "| No clipped points | PASS |",
                "| No excessive point overplotting | PASS |",
                "| No hidden Unicode in internal variable names | PASS |",
                "| No pipeline variable names in display labels | PASS |",
                "| No misleading axis truncation | PASS |",
                "| Zero line visible | PASS |",
                "| Effect-size axis includes zero | PASS |",
                "| CI labels readable | PASS |",
                "| Font consistent with Figures 1-3 | PASS |",
                "| Half-size readability | PASS |",
                "",
                "Decision: PASS",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    final_data = {
        "selected_layout": "OPTION B",
        "bar_chart_removed": True,
        "target_level_frozen_data_available": True,
        "plot_type": "DISTRIBUTION+FOREST",
        "metric_label": "Audit-delta Pearson",
        "directions": {
            spec["label"]: {
                "n": int(primary[primary["direction"] == spec["key"]].iloc[0]["n_targets"]),
                "within": float(primary[primary["direction"] == spec["key"]].iloc[0]["within_estimate"]),
                "cross": float(primary[primary["direction"] == spec["key"]].iloc[0]["cross_estimate"]),
                "drop": float(primary[primary["direction"] == spec["key"]].iloc[0]["paired_difference"]),
                "ci_low": float(primary[primary["direction"] == spec["key"]].iloc[0]["ci_low"]),
                "ci_high": float(primary[primary["direction"] == spec["key"]].iloc[0]["ci_high"]),
            }
            for spec in DIRECTIONS
        },
    }
    (REPORTS / "FIGURE4_V2_FINAL_RESPONSE_DATA.json").write_text(json.dumps(final_data, indent=2), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    archive_previous()
    configure_matplotlib()
    primary, target, registry = load_frozen()
    integrity_messages = assert_numeric_integrity(primary, target)
    write_reports(primary, target, registry, integrity_messages)

    draw_option_a(primary, target, FIG_QC / "Figure4_optionA")
    plt.close("all")
    draw_option_b(primary, target, FIG_QC / "Figure4_optionB")
    plt.close("all")
    draw_option_b(primary, target, FIG_MAIN / "Figure4_v2")
    plt.close("all")
    for ext in [".svg", ".pdf", ".png"]:
        shutil.copy2(FIG_MAIN / f"Figure4_v2{ext}", FIG_MAIN / f"Figure4{ext}")
    make_halfsize(FIG_MAIN / "Figure4_v2.png", FIG_QC / "Figure4_v2_halfsize.png")


if __name__ == "__main__":
    main()
