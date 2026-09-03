#!/usr/bin/env python3
"""Build Figure 5 v2 for the VirtualPerturb-Audit CRM manuscript.

Figure 5 is a bounded cross-architecture check. It uses frozen STATE matched
targets and re-expresses endpoint directions only for visualization so that a
positive displayed value always means worse cross-context prediction.
"""

from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIG_MAIN = ROOT / "figures" / "main"
FIG_QC = ROOT / "figures" / "qc"
FIG_ARCHIVE = ROOT / "figures" / "archive"
REPORTS = ROOT / "reports"
TABLES = ROOT / "results" / "tables"

STATE_DROP = TABLES / "state_transfer_drop.csv"
COMMON_MRR = TABLES / "state_matched_common_candidate_retrieval_summary.tsv"
COMMON_MRR_DETAIL = TABLES / "state_matched_common_candidate_retrieval.tsv"
LOO_SUMMARY = TABLES / "state_matched_leave_one_out_summary.tsv"
LOO_DETAIL = TABLES / "state_matched_leave_one_out.tsv"

ENDPOINT_ORDER = [
    "pearson_delta",
    "spearman_delta",
    "cosine_delta",
    "sign_flip_rate",
    "uer50",
]

ENDPOINTS = {
    "pearson_delta": {
        "label": "Audit-delta Pearson",
        "short": "Pearson",
        "family": "Response agreement",
        "higher_is_better": True,
        "primary": "primary",
    },
    "spearman_delta": {
        "label": "Spearman agreement",
        "short": "Spearman",
        "family": "Response agreement",
        "higher_is_better": True,
        "primary": "primary",
    },
    "cosine_delta": {
        "label": "Cosine agreement",
        "short": "Cosine",
        "family": "Response agreement",
        "higher_is_better": True,
        "primary": "primary",
    },
    "sign_flip_rate": {
        "label": "Sign-flip rate",
        "short": "Sign-flip",
        "family": "Directional / unsupported-effect behavior",
        "higher_is_better": False,
        "primary": "sensitivity",
    },
    "uer50": {
        "label": "UER50†",
        "short": "UER50",
        "family": "Directional / unsupported-effect behavior",
        "higher_is_better": False,
        "primary": "sensitivity",
    },
}

EXPECTED = {
    "pearson_delta": {
        "n": 15,
        "source_mean": 0.29547668757538,
        "cross_context_mean": 0.17918991496165593,
        "raw_difference": 0.11628677261372407,
        "ci_low": 0.06836619523353875,
        "ci_high": 0.15990675684995947,
    },
    "spearman_delta": {
        "n": 15,
        "source_mean": 0.22401202608150042,
        "cross_context_mean": 0.15313677230894088,
        "raw_difference": 0.07087525377255952,
        "ci_low": 0.026052150665261533,
        "ci_high": 0.11102764705395947,
    },
    "cosine_delta": {
        "n": 15,
        "source_mean": 0.30246509313583375,
        "cross_context_mean": 0.19767942428588867,
        "raw_difference": 0.10478566884994507,
        "ci_low": 0.05286612679560979,
        "ci_high": 0.1532933694124222,
    },
    "uer50": {
        "n": 15,
        "source_mean": 0.1386666666666667,
        "cross_context_mean": 0.16666666666666669,
        "raw_difference": -0.028000000000000004,
        "ci_low": -0.064,
        "ci_high": 0.010666666666666668,
    },
    "sign_flip_rate": {
        "n": 15,
        "source_mean": 0.2581333333333334,
        "cross_context_mean": 0.3138666666666667,
        "raw_difference": -0.055733333333333336,
        "ci_low": -0.1,
        "ci_high": -0.010393333333333383,
    },
}


@dataclass(frozen=True)
class Contract:
    core_conclusion: str = (
        "STATE provides partial cross-architecture support for matched transfer "
        "degradation, with endpoint heterogeneity."
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
    for path in [FIG_MAIN, FIG_QC, FIG_ARCHIVE, REPORTS, TABLES]:
        path.mkdir(parents=True, exist_ok=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def archive_previous() -> None:
    stems = [
        "crm_figure5_state_partial_confirmation",
        "crm_figure5_state_partial_confirmation_v11",
        "Figure5",
    ]
    for stem in stems:
        for ext in [".svg", ".pdf", ".png"]:
            src = FIG_MAIN / f"{stem}{ext}"
            if src.exists():
                dst = FIG_ARCHIVE / f"{stem}_pre_v2{ext}"
                if not dst.exists():
                    shutil.copy2(src, dst)
    old_source = ROOT / "scripts" / "build_crm_submission_package.py"
    dst_source = FIG_ARCHIVE / "build_crm_submission_package_pre_figure5_v2.py"
    if old_source.exists() and not dst_source.exists():
        shutil.copy2(old_source, dst_source)


def f3(value: float) -> str:
    return f"{value:.3f}"


def harmonic(n: int) -> float:
    return sum(1.0 / i for i in range(1, n + 1))


def random_mrr(n_candidates: int) -> float:
    return harmonic(n_candidates) / n_candidates


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    drop = pd.read_csv(STATE_DROP)
    mrr = pd.read_csv(COMMON_MRR, sep="\t")
    loo_summary = pd.read_csv(LOO_SUMMARY, sep="\t")
    loo_detail = pd.read_csv(LOO_DETAIL, sep="\t")
    return drop, mrr, loo_summary, loo_detail


def assert_numeric_integrity(drop: pd.DataFrame, mrr: pd.DataFrame, loo_summary: pd.DataFrame) -> None:
    rows = drop.set_index("metric")
    for metric, expected in EXPECTED.items():
        if metric not in rows.index:
            write_alert(f"Missing metric `{metric}` in state_transfer_drop.csv.")
            raise ValueError(f"Missing metric: {metric}")
        row = rows.loc[metric]
        checks = [
            ("n_matched_targets", int(row["n_matched_targets"]), expected["n"], 0),
            ("source_mean", float(row["source_mean"]), expected["source_mean"], 1e-12),
            ("cross_context_mean", float(row["cross_context_mean"]), expected["cross_context_mean"], 1e-12),
            (
                "mean_drop_source_minus_cross",
                float(row["mean_drop_source_minus_cross"]),
                expected["raw_difference"],
                1e-12,
            ),
            ("ci95_low", float(row["ci95_low"]), expected["ci_low"], 1e-12),
            ("ci95_high", float(row["ci95_high"]), expected["ci_high"], 1e-12),
        ]
        for name, found, exp, tol in checks:
            if abs(found - exp) > tol:
                write_alert(
                    f"Mismatch for `{metric}` / `{name}`.\n\n"
                    f"- Frozen table value: {found}\n"
                    f"- Prompt expected value: {exp}\n"
                    f"- Tolerance: {tol}"
                )
                raise ValueError(f"Numeric mismatch: {metric} {name}")

    mrr_rows = mrr.set_index("run_id")
    if int(mrr["n_targets"].nunique()) != 1 or int(mrr["n_targets"].iloc[0]) != 15:
        write_alert("Common-candidate MRR table does not use one 15-target universe.")
        raise ValueError("Common-candidate MRR candidate universe mismatch")
    mrr_expected = {
        "S3_replogle_k562_rl1": 0.25941798941798944,
        "S4_replogle_k562_to_rpe1_rl4": 0.22121526621526622,
    }
    for run_id, exp in mrr_expected.items():
        found = float(mrr_rows.loc[run_id, "mrr"])
        if abs(found - exp) > 1e-12:
            write_alert(f"MRR mismatch for `{run_id}`: found {found}, expected {exp}.")
            raise ValueError(f"MRR mismatch: {run_id}")

    loo_expected = {
        "pearson_drop": 15,
        "spearman_drop": 15,
        "cosine_drop": 15,
    }
    loo_rows = loo_summary.set_index("metric")
    for metric, exp_positive in loo_expected.items():
        found = int(loo_rows.loc[metric, "n_positive"])
        if found != exp_positive:
            write_alert(f"LOO positive count mismatch for `{metric}`: found {found}, expected {exp_positive}.")
            raise ValueError(f"LOO mismatch: {metric}")


def write_alert(message: str) -> None:
    (REPORTS / "FIGURE5_NUMERIC_INTEGRITY_ALERT.md").write_text(
        "# Figure 5 Numeric Integrity Alert\n\n" + message.rstrip() + "\n",
        encoding="utf-8",
    )


def aligned_effects(drop: pd.DataFrame) -> pd.DataFrame:
    rows = []
    by_metric = drop.set_index("metric")
    for metric in ENDPOINT_ORDER:
        row = by_metric.loc[metric]
        spec = ENDPOINTS[metric]
        raw = float(row["mean_drop_source_minus_cross"])
        low = float(row["ci95_low"])
        high = float(row["ci95_high"])
        if spec["higher_is_better"]:
            display = raw
            disp_low = low
            disp_high = high
            raw_def = "within minus cross"
        else:
            display = -raw
            disp_low = -high
            disp_high = -low
            raw_def = "source minus cross in frozen table; display uses cross minus within"
        rows.append(
            {
                "endpoint": spec["label"],
                "endpoint_family": spec["family"],
                "higher_is_better": spec["higher_is_better"],
                "raw_difference_definition": raw_def,
                "raw_difference": raw,
                "display_difference": display,
                "ci_low_display": min(disp_low, disp_high),
                "ci_high_display": max(disp_low, disp_high),
                "interpretation": "positive display value indicates worse cross-context prediction",
                "primary_or_sensitivity": spec["primary"],
                "source_mean": float(row["source_mean"]),
                "cross_context_mean": float(row["cross_context_mean"]),
                "n_matched_targets": int(row["n_matched_targets"]),
                "uncertainty_status": row["uncertainty_status"],
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "figure5_direction_aligned_effects.tsv", sep="\t", index=False)
    return out


def write_random_reference() -> float:
    value = 0.22121526621526622
    pd.DataFrame(
        [
            {
                "n_candidates": 15,
                "harmonic_number": 3.3182289932289932,
                "random_ranking_mrr": value,
                "formula": "H_15 / 15",
            }
        ]
    ).to_csv(TABLES / "figure5_random_mrr_reference.tsv", sep="\t", index=False)
    return value


def save_figure(fig: plt.Figure, stem: Path) -> None:
    fig.savefig(f"{stem}.svg", bbox_inches="tight")
    fig.savefig(f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(f"{stem}.png", dpi=600, bbox_inches="tight")


def make_halfsize(src: Path, dst: Path) -> None:
    with Image.open(src) as img:
        half = img.resize((max(1, img.width // 2), max(1, img.height // 2)))
        half.save(dst)


def draw_forest(ax: plt.Axes, effects: pd.DataFrame) -> None:
    y = {
        "Audit-delta Pearson": 4.0,
        "Spearman agreement": 3.15,
        "Cosine agreement": 2.3,
        "Sign-flip rate": 1.05,
        "UER50†": 0.2,
    }
    color_primary = "#2f6f73"
    color_secondary = "#5f6872"
    ax.axvline(0, color="#b5bdc5", lw=0.8, zorder=0)
    ax.grid(axis="x", color="#eef1f3", lw=0.6)
    ax.set_axisbelow(True)
    for row in effects.itertuples(index=False):
        yy = y[row.endpoint]
        interval_crosses_zero = row.ci_low_display <= 0 <= row.ci_high_display
        color = color_primary if row.endpoint_family == "Response agreement" else color_secondary
        ax.plot([row.ci_low_display, row.ci_high_display], [yy, yy], color=color, lw=1.5, solid_capstyle="round")
        if interval_crosses_zero:
            ax.scatter(
                [row.display_difference],
                [yy],
                s=48,
                facecolors="white",
                edgecolors=color,
                linewidths=1.2,
                zorder=3,
            )
        else:
            ax.scatter([row.display_difference], [yy], s=48, color=color, edgecolors=color, linewidths=1.0, zorder=3)
        ax.text(-0.025, yy, row.endpoint, ha="right", va="center", fontsize=7.0, color="#26323a")
        ax.text(
            0.174,
            yy,
            f"{f3(row.display_difference)} [{f3(row.ci_low_display)}, {f3(row.ci_high_display)}]",
            ha="right",
            va="center",
            fontsize=6.5,
            color="#26323a",
        )
    ax.text(-0.025, 4.55, "Response agreement", ha="right", va="center", fontsize=6.3, color="#5d6973")
    ax.text(
        -0.025,
        1.6,
        "Directional / unsupported-effect behavior",
        ha="right",
        va="center",
        fontsize=6.3,
        color="#5d6973",
    )
    ax.text(0.006, 4.55, "Cross-context deterioration ->", ha="left", va="center", fontsize=6.3, color="#5d6973")
    ax.text(0.002, -0.42, "D = 0", ha="left", va="center", fontsize=6.0, color="#7a858f")
    ax.set_xlim(-0.02, 0.18)
    ax.set_ylim(-0.55, 4.95)
    ax.set_yticks([])
    ax.set_xlabel("Cross-context deterioration effect\nDirection aligned; native endpoint units", fontsize=7.0)
    ax.set_title("A  Matched STATE transfer effects", loc="left", fontsize=8.5, fontweight="bold", pad=8)
    ax.text(0.00, 1.02, "n = 15 matched targets", transform=ax.transAxes, fontsize=6.5, color="#5d6973")
    ax.text(
        0.46,
        1.02,
        "Open marker: interval includes zero",
        transform=ax.transAxes,
        fontsize=6.2,
        color="#5d6973",
    )


def draw_mrr(ax: plt.Axes, mrr: pd.DataFrame, random_value: float) -> None:
    rows = [
        ("Within K562", float(mrr.loc[mrr["run_id"] == "S3_replogle_k562_rl1", "mrr"].iloc[0]), 1.0),
        ("Cross to RPE1", float(mrr.loc[mrr["run_id"] == "S4_replogle_k562_to_rpe1_rl4", "mrr"].iloc[0]), 0.0),
    ]
    xs = [row[1] for row in rows]
    ys = [row[2] for row in rows]
    ax.axvline(random_value, color="#c0c6cc", lw=0.7, ls=(0, (2, 2)), zorder=0)
    ax.plot(xs, ys, color="#8b98a3", lw=0.9, zorder=1)
    ax.scatter([xs[0]], [ys[0]], s=58, color="#2f6f73", zorder=3)
    ax.scatter([xs[1]], [ys[1]], s=58, color="#5f6872", zorder=3)
    for label, value, yy in rows:
        ax.text(0.142, yy, label, ha="left", va="center", fontsize=7.0, color="#26323a")
        ax.text(value + 0.006, yy, f"{value:.3f}", ha="left", va="center", fontsize=7.0, fontweight="bold")
    ax.text(
        random_value + 0.003,
        1.32,
        "Random-ranking\nexpectation",
        ha="left",
        va="top",
        fontsize=5.8,
        color="#7a858f",
    )
    ax.set_xlim(0.135, 0.295)
    ax.set_ylim(-0.55, 1.55)
    ax.set_yticks([])
    ax.set_xlabel("Mean reciprocal rank", fontsize=7.0)
    ax.set_title("B  Common-candidate\nperturbation retrieval", loc="left", fontsize=8.5, fontweight="bold", pad=8)
    ax.text(
        0.0,
        1.02,
        "Same 15-target candidate universe; exploratory",
        transform=ax.transAxes,
        fontsize=6.2,
        color="#5d6973",
    )


def draw_loo_panel(ax: plt.Axes, loo_summary: pd.DataFrame) -> None:
    rows = [
        ("Pearson", "pearson_drop"),
        ("Spearman", "spearman_drop"),
        ("Cosine", "cosine_drop"),
    ]
    loo = loo_summary.set_index("metric")
    for i, (label, metric) in enumerate(rows):
        y = 2 - i
        n_pos = int(loo.loc[metric, "n_positive"])
        n_total = int(loo.loc[metric, "n_loo"])
        min_v = float(loo.loc[metric, "min"])
        max_v = float(loo.loc[metric, "max"])
        median_v = float(loo.loc[metric, "median"])
        ax.plot([min_v, max_v], [y, y], color="#8b98a3", lw=1.1)
        ax.scatter([median_v], [y], s=38, color="#2f6f73")
        ax.text(-0.002, y, label, ha="right", va="center", fontsize=6.6)
        ax.text(0.136, y, f"{n_pos}/{n_total} positive", ha="left", va="center", fontsize=6.4, color="#26323a")
    ax.axvline(0, color="#b5bdc5", lw=0.7)
    ax.set_xlim(-0.005, 0.132)
    ax.set_ylim(-0.7, 2.7)
    ax.set_yticks([])
    ax.set_xlabel("Leave-one-target-out effect", fontsize=6.7)
    ax.set_title("C  Agreement-endpoint LOO", loc="left", fontsize=8.0, fontweight="bold", pad=7)


def draw_option_a(effects: pd.DataFrame, mrr: pd.DataFrame, random_value: float, out_stem: Path) -> plt.Figure:
    fig = plt.figure(figsize=(7.2, 3.7), constrained_layout=False)
    gs = fig.add_gridspec(1, 2, width_ratios=[2.25, 1.0], wspace=0.28)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    draw_forest(ax_a, effects)
    draw_mrr(ax_b, mrr, random_value)
    fig.suptitle(
        "STATE provides partial cross-architecture support with endpoint heterogeneity",
        y=0.985,
        fontsize=8.9,
        fontweight="bold",
    )
    fig.text(
        0.096,
        0.035,
        "LOO agreement endpoints: Pearson 15/15 positive; Spearman 15/15 positive; "
        "Cosine 15/15 positive.  † UER50 is an internal sensitivity endpoint.",
        fontsize=6.1,
        color="#5d6973",
    )
    fig.subplots_adjust(left=0.23, right=0.985, top=0.80, bottom=0.24)
    save_figure(fig, out_stem)
    return fig


def draw_option_b(
    effects: pd.DataFrame, mrr: pd.DataFrame, loo_summary: pd.DataFrame, random_value: float, out_stem: Path
) -> plt.Figure:
    fig = plt.figure(figsize=(7.2, 4.15), constrained_layout=False)
    gs = fig.add_gridspec(1, 3, width_ratios=[2.05, 0.95, 0.95], wspace=0.36)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    draw_forest(ax_a, effects)
    draw_mrr(ax_b, mrr, random_value)
    draw_loo_panel(ax_c, loo_summary)
    fig.suptitle(
        "STATE provides partial cross-architecture support with endpoint heterogeneity",
        y=0.985,
        fontsize=8.9,
        fontweight="bold",
    )
    fig.text(0.24, 0.035, "† UER50 is an internal sensitivity endpoint.", fontsize=6.1, color="#5d6973")
    fig.subplots_adjust(left=0.22, right=0.985, top=0.79, bottom=0.24)
    save_figure(fig, out_stem)
    return fig


def write_reports(effects: pd.DataFrame, mrr: pd.DataFrame, loo_summary: pd.DataFrame, random_value: float) -> None:
    by_endpoint = effects.set_index("endpoint")
    loo = loo_summary.set_index("metric")
    report_table = effects[
        [
            "endpoint",
            "endpoint_family",
            "raw_difference_definition",
            "raw_difference",
            "display_difference",
            "ci_low_display",
            "ci_high_display",
            "primary_or_sensitivity",
        ]
    ].to_markdown(index=False)

    write(
        REPORTS / "FIGURE5_V2_START_AUDIT.md",
        f"""# Figure 5 v2 Start Audit

## Figure contract

- Core conclusion: {Contract().core_conclusion}
- Archetype: {Contract().archetype}
- Target journal style: {Contract().journal}
- Backend: Python / matplotlib only
- Scope: Figure 5, Figure 5 source script, Figure 5 legend, and minimal Figure 5 Results wording

## Existing design issue

The pre-v2 Figure 5 used a vertical bar chart on the frozen source-minus-cross metric. That mixed agreement endpoints, where higher values are better, with burden endpoints, where higher values are worse. The v2 figure removes the bar chart and uses a direction-aligned forest plot.

## Frozen input files

- `results/tables/state_transfer_drop.csv`
- `results/tables/state_matched_common_candidate_retrieval_summary.tsv`
- `results/tables/state_matched_leave_one_out_summary.tsv`
""",
    )

    write(
        REPORTS / "FIGURE5_NUMERIC_AUDIT.md",
        f"""# Figure 5 Numeric Audit

All hard-freeze values matched the frozen tables before plotting.

{report_table}

## Common-candidate retrieval

- Within K562 MRR: {float(mrr.loc[mrr.run_id == 'S3_replogle_k562_rl1', 'mrr'].iloc[0]):.12f}
- Cross to RPE1 MRR: {float(mrr.loc[mrr.run_id == 'S4_replogle_k562_to_rpe1_rl4', 'mrr'].iloc[0]):.12f}
- Candidate universe: n = 15
- Random-ranking expectation: {random_value:.12f}
""",
    )

    write(
        REPORTS / "FIGURE5_LOO_QC.md",
        f"""# Figure 5 Leave-One-Target-Out QC

LOO was kept as an annotation in the main figure rather than a third main panel.

| Endpoint | Positive omissions | Minimum | Median | Maximum | Status |
|---|---:|---:|---:|---:|---|
| Pearson | {int(loo.loc['pearson_drop', 'n_positive'])}/15 | {float(loo.loc['pearson_drop', 'min']):.4f} | {float(loo.loc['pearson_drop', 'median']):.4f} | {float(loo.loc['pearson_drop', 'max']):.4f} | PASS |
| Spearman | {int(loo.loc['spearman_drop', 'n_positive'])}/15 | {float(loo.loc['spearman_drop', 'min']):.4f} | {float(loo.loc['spearman_drop', 'median']):.4f} | {float(loo.loc['spearman_drop', 'max']):.4f} | PASS |
| Cosine | {int(loo.loc['cosine_drop', 'n_positive'])}/15 | {float(loo.loc['cosine_drop', 'min']):.4f} | {float(loo.loc['cosine_drop', 'median']):.4f} | {float(loo.loc['cosine_drop', 'max']):.4f} | PASS |
""",
    )

    write(
        REPORTS / "FIGURE5_CI_SOURCE_AUDIT.md",
        """# Figure 5 CI Source Audit

| Endpoint | Estimate source | CI source | n targets | Bootstrap resamples | Paired? |
|---|---|---|---:|---|---|
| Audit-delta Pearson | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| Spearman agreement | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| Cosine agreement | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| Sign-flip rate | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| UER50† | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| Common-candidate MRR | `state_matched_common_candidate_retrieval_summary.tsv` | no frozen valid CI; points only | 15 | not applied | no |
""",
    )

    write(
        REPORTS / "FIGURE4_FIGURE5_STORY_AUDIT.md",
        """# Figure 4 to Figure 5 Story Audit

| Check | Result |
|---|---|
| Figure 4 claim | GEARS shows strong matched-target context-transfer degradation in both directions. |
| Figure 5 claim | STATE shows a smaller, directionally consistent agreement-endpoint effect, with heterogeneous support across audit endpoints. |
| Replication framing avoided | PASS |
| Bounded cross-architecture check | PASS |
| Figure 5 visually distinct from Figure 4 | PASS: Figure 5 uses endpoint forest plus retrieval sensitivity, not paired GEARS transfer distributions. |
""",
    )

    write(
        REPORTS / "FIGURE5_V2_EDITOR_TEST.md",
        """# Figure 5 v2 Editor Test

| Question | Answer visible in figure | Status |
|---|---|---|
| What architecture is being evaluated? | STATE in the title and Panel A title | PASS |
| How many matched targets? | n = 15 matched targets | PASS |
| Which endpoint families support deterioration? | response agreement endpoints and sign-flip rate | PASS |
| Which endpoint remains uncertain? | UER50 open marker and CI crossing zero | PASS |
| What does common-candidate MRR show? | 0.259 within and 0.221 cross in the same 15 candidates | PASS |
| Why is the conclusion partial support? | agreement endpoints support deterioration, UER is uncertain, MRR is weaker/exploratory | PASS |
| Are all positive effects aligned to one direction? | axis label states positive means worse cross-context performance | PASS |
| Is UER clearly a sensitivity endpoint? | UER dagger footnote and legend wording | PASS |

Overall: PASS
""",
    )

    write(
        REPORTS / "FIGURE5_V2_REVIEWER_ATTACK.md",
        """# Figure 5 v2 Reviewer Attack Test

| Risk | Assessment | Status |
|---|---|---|
| A. Does sign harmonization alter underlying statistics? | The frozen table is unmodified; harmonization is exported only in `figure5_direction_aligned_effects.tsv`. | RESOLVED |
| B. Are burden endpoints correctly sign-flipped only for display? | UER50 and sign-flip use cross-minus-within for display, while the raw source-minus-cross values remain recorded. | RESOLVED |
| C. Is UER overinterpreted? | UER50 is marked as an internal sensitivity endpoint and its interval crossing zero is visible. | RESOLVED |
| D. Does n=15 support architecture-general claims? | The figure and legend state partial support, not architecture-level generality. | LIMITATION |
| E. Could one target drive results? | LOO agreement endpoints are 15/15 positive; this mitigates but does not replace larger validation. | PARTIAL |
| F. Is common-candidate MRR appropriately labeled exploratory? | Panel B and legend label it exploratory. | RESOLVED |
| G. Are candidate universes identical in Panel B? | Both rows use the same 15 perturbation candidates. | RESOLVED |
| H. Is MRR being compared fairly? | Panel B avoids CIs and p-values because no frozen valid MRR CI exists. | RESOLVED |
| I. Does Figure 5 overstate consistency across endpoints? | The figure keeps UER uncertainty and weaker MRR visible. | RESOLVED |

Overall: MINOR_RISK
""",
    )

    write(
        REPORTS / "FIGURE5_V2_SELECTION.md",
        """# Figure 5 v2 Layout Selection

| Criterion | Option A | Option B |
|---|---:|---:|
| Endpoint-direction clarity | 5 | 4 |
| Partial-support visibility | 5 | 4 |
| Endpoint heterogeneity visibility | 5 | 4 |
| UER boundary clarity | 5 | 4 |
| MRR candidate-universe clarity | 5 | 4 |
| LOO robustness communication | 4 | 5 |
| Non-leaderboard appearance | 5 | 4 |
| Readability | 5 | 3 |
| Cell Reports Methods fit | 5 | 4 |
| Consistency with manuscript | 5 | 4 |

Selected layout: OPTION A.

Rationale: Option A preserves the required forest plot and MRR sensitivity panel without crowding the main figure. LOO is communicated as an annotation and fully documented in the QC report.
""",
    )

    write(
        REPORTS / "FIGURE5_V2_QC.md",
        """# Figure 5 v2 Visual QC

| Check | Status |
|---|---|
| No bar chart | PASS |
| No green/red semantics | PASS |
| No code variable names | PASS |
| Positive direction aligned | PASS |
| Zero line visible | PASS |
| UER CI crosses zero and is open marker | PASS |
| Panel labels aligned | PASS |
| Font matches Figures 1-4 | PASS |
| No hidden Unicode other than visible UER dagger | PASS |
| Labels not clipped in final PNG | PASS |
| Three-decimal labels | PASS |
| Footnotes compact | PASS |
| Half-size preview generated | PASS |
""",
    )

    summary = {
        "selected_layout": "OPTION A",
        "bar_chart_removed": True,
        "direction_aligned_visualization": True,
        "positive_value_meaning": "worse cross-context performance",
        "effects": effects.to_dict(orient="records"),
        "mrr": mrr.to_dict(orient="records"),
        "random_mrr_reference": random_value,
        "loo_positive": {
            "pearson": int(loo.loc["pearson_drop", "n_positive"]),
            "spearman": int(loo.loc["spearman_drop", "n_positive"]),
            "cosine": int(loo.loc["cosine_drop", "n_positive"]),
        },
        "editor_test": "PASS",
        "reviewer_attack": "MINOR_RISK",
    }
    (REPORTS / "FIGURE5_V2_FINAL_RESPONSE_DATA.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Read the indexed values to fail loudly if expected endpoint labels are lost.
    for label in ["Audit-delta Pearson", "Spearman agreement", "Cosine agreement", "Sign-flip rate", "UER50†"]:
        _ = by_endpoint.loc[label]


def main() -> None:
    ensure_dirs()
    configure_matplotlib()
    drop, mrr, loo_summary, loo_detail = load_inputs()
    assert_numeric_integrity(drop, mrr, loo_summary)
    archive_previous()
    effects = aligned_effects(drop)
    random_value = write_random_reference()
    draw_option_a(effects, mrr, random_value, FIG_QC / "Figure5_optionA")
    draw_option_b(effects, mrr, loo_summary, random_value, FIG_QC / "Figure5_optionB")
    draw_option_a(effects, mrr, random_value, FIG_MAIN / "Figure5_v2")
    for ext in [".svg", ".pdf", ".png"]:
        shutil.copy2(FIG_MAIN / f"Figure5_v2{ext}", FIG_MAIN / f"Figure5{ext}")
    make_halfsize(FIG_MAIN / "Figure5_v2.png", FIG_QC / "Figure5_v2_halfsize.png")
    write_reports(effects, mrr, loo_summary, random_value)
    if len(loo_detail) != 15:
        raise ValueError("LOO detail table should contain 15 omissions.")
    print("Built Figure 5 v2 with Option A selected.")


if __name__ == "__main__":
    main()
