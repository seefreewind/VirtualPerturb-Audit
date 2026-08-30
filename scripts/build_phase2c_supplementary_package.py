from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"
REPORTS = ROOT / "reports"
FIGURES = ROOT / "figures/supplementary"
MANUSCRIPT = ROOT / "manuscript"

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


def save(fig, basename: Path, formats: list[str] | None = None) -> None:
    formats = formats or ["pdf", "svg", "png"]
    basename.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=1.1)
    for fmt in formats:
        fig.savefig(basename.with_suffix("." + fmt), dpi=450, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def fmt(v, digits: int = 4) -> str:
    if pd.isna(v):
        return "NA"
    if isinstance(v, (float, np.floating)):
        return f"{float(v):.{digits}f}"
    return str(v)


def md_table(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "state_primary": pd.read_csv(TABLES / "state_phase2c_primary_metrics.csv"),
        "state_transfer": pd.read_csv(TABLES / "state_transfer_drop.csv"),
        "state_perturbation": pd.read_csv(TABLES / "state_phase2c_perturbation_metrics.csv"),
        "comparison": pd.read_csv(TABLES / "gears_state_primary_comparison.csv"),
        "second_model": pd.read_csv(TABLES / "gears_second_model_confirmatory.csv"),
        "split_alignment": pd.read_csv(TABLES / "state_gears_split_alignment.tsv", sep="\t"),
        "dataset_manifest": pd.read_csv(TABLES / "state_phase2c_dataset_manifest.csv"),
    }


def build_supplementary_tables(data: dict[str, pd.DataFrame]) -> None:
    primary = data["state_primary"]
    primary = primary[primary["metric_space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    supp1 = primary[
        [
            "setting",
            "dataset",
            "split",
            "metric_space",
            "n_test_perturbations",
            "n_genes",
            "pearson_delta",
            "pearson_ci_low",
            "pearson_ci_high",
            "spearman_delta",
            "cosine_delta",
            "rmse_delta",
            "retrieval_top1",
            "retrieval_top5",
            "retrieval_mrr",
            "mrr_ci_low",
            "mrr_ci_high",
            "uer20",
            "uer50",
            "uer100",
            "sign_flip_rate",
            "bns_status",
            "null_status",
        ]
    ]
    supp1.to_csv(TABLES / "supp_phase2c_state_primary_metrics.csv", index=False)

    supp2 = data["state_transfer"].copy()
    supp2["interpretation_direction"] = supp2["metric"].map(
        {
            "pearson_delta": "positive means within-context agreement is higher",
            "spearman_delta": "positive means within-context rank agreement is higher",
            "cosine_delta": "positive means within-context direction agreement is higher",
            "uer50": "negative means cross-context unsupported-effect burden is higher",
            "sign_flip_rate": "negative means cross-context sign-flip burden is higher",
        }
    )
    supp2.to_csv(TABLES / "supp_phase2c_matched_transfer_contrast.csv", index=False)

    align = data["split_alignment"]
    supp3 = (
        align.groupby(["dataset", "split", "alignment_status"], as_index=False)
        .size()
        .rename(columns={"size": "n_conditions"})
    )
    supp3.to_csv(TABLES / "supp_phase2c_split_alignment_summary.csv", index=False)

    caveats = pd.DataFrame(
        [
            {
                "issue": "Metric space",
                "status": "GEARS Norman frozen rows are raw GEARS-space; STATE primary rows are audit-delta.",
                "handling": "Do not make absolute GEARS-vs-STATE performance claims from raw side-by-side values.",
            },
            {
                "issue": "Normalized targets",
                "status": "STATE collapses explicit control partners, e.g. ctrl+X and X.",
                "handling": "Report both frozen condition counts and normalized target counts.",
            },
            {
                "issue": "R-L4 target set",
                "status": "STATE R-L4 has 73 normalized targets; Replogle K562 R-L1 has 216.",
                "handling": "Use matched-target contrast for the strongest context-transfer interpretation.",
            },
            {
                "issue": "BNS",
                "status": "Bound-normalized score remains unverified.",
                "handling": "Keep BNS out of confirmatory claims until replicate-bound nulls are verified.",
            },
            {
                "issue": "UER null",
                "status": "UER uses median absolute observed delta as an internal null.",
                "handling": "Label UER as sensitivity-only.",
            },
        ]
    )
    caveats.to_csv(TABLES / "supp_phase2c_endpoint_caveats.csv", index=False)

    file_manifest = pd.DataFrame(
        [
            {"role": "main_phase2c_report", "path": "reports/PHASE2C_DECISION.md"},
            {"role": "interpretation_report", "path": "reports/PHASE2C_RESULT_INTERPRETATION.md"},
            {"role": "preferred_main_figure", "path": "figures/main/phase2c_state_interpretation.pdf"},
            {"role": "directionality_figure", "path": "figures/main/phase2c_gears_state_directionality.pdf"},
            {"role": "supplementary_heatmap", "path": "figures/supplementary/phase2c_endpoint_heatmap.pdf"},
            {"role": "supplementary_retrieval_rank", "path": "figures/supplementary/phase2c_retrieval_rank_distribution.pdf"},
            {"role": "primary_state_table", "path": "results/tables/supp_phase2c_state_primary_metrics.csv"},
            {"role": "matched_transfer_table", "path": "results/tables/supp_phase2c_matched_transfer_contrast.csv"},
            {"role": "caveat_table", "path": "results/tables/supp_phase2c_endpoint_caveats.csv"},
            {"role": "reviewer_response_prep", "path": "reports/PHASE2C_REVIEWER_RESPONSE_PREP.md"},
            {"role": "integrated_manuscript_draft", "path": "manuscript/MANUSCRIPT_v0.3.md"},
        ]
    )
    file_manifest.to_csv(TABLES / "supp_phase2c_file_manifest.csv", index=False)


def plot_endpoint_heatmap(data: dict[str, pd.DataFrame]) -> None:
    style()
    primary = data["state_primary"]
    primary = primary[primary["metric_space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    primary["short"] = primary["setting"].map(
        {
            "Norman L1 STATE": "Norman L1",
            "Norman L2 STATE": "Norman L2",
            "Replogle K562 R-L1 STATE": "K562 R-L1",
            "Replogle K562 -> RPE1 R-L4 STATE": "K562->RPE1 R-L4",
        }
    )
    metrics = ["pearson_delta", "spearman_delta", "cosine_delta", "retrieval_mrr", "uer50", "sign_flip_rate"]
    matrix = primary.set_index("short")[metrics]
    z = matrix.copy()
    for col in z.columns:
        values = z[col].astype(float)
        lo, hi = values.min(), values.max()
        z[col] = 0.5 if hi == lo else (values - lo) / (hi - lo)
    fig, ax = plt.subplots(1, 1, figsize=(8.2, 3.8))
    im = ax.imshow(z.to_numpy(), cmap="viridis", aspect="auto", vmin=0, vmax=1)
    ax.set_yticks(range(len(z.index)))
    ax.set_yticklabels(z.index)
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(["Pearson", "Spearman", "Cosine", "MRR", "UER@50", "Sign flip"], rotation=25, ha="right")
    for i in range(matrix.shape[0]):
        for j, col in enumerate(metrics):
            ax.text(j, i, fmt(matrix.iloc[i, j], 3), ha="center", va="center", fontsize=8, color="white" if z.iloc[i, j] < 0.45 else "black")
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("Column-normalized value")
    ax.set_title("Supplementary endpoint heatmap for STATE Phase 2C", loc="left", fontsize=12, fontweight="bold")
    save(fig, FIGURES / "phase2c_endpoint_heatmap")


def plot_retrieval_rank_distribution(data: dict[str, pd.DataFrame]) -> None:
    style()
    retrieval = pd.read_csv(TABLES / "state_phase2c_retrieval.csv")
    retrieval = retrieval[retrieval["space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    retrieval["task"] = retrieval["run_id"].map(
        {
            "S1_norman_l1": "Norman L1",
            "S2_norman_l2": "Norman L2",
            "S3_replogle_k562_rl1": "K562 R-L1",
            "S4_replogle_k562_to_rpe1_rl4": "K562->RPE1 R-L4",
        }
    )
    order = ["Norman L1", "Norman L2", "K562 R-L1", "K562->RPE1 R-L4"]
    colors = [PALETTE["neutral"], PALETTE["neutral"], PALETTE["blue_main"], PALETTE["red_strong"]]
    fig, ax = plt.subplots(1, 1, figsize=(8.4, 4.4))
    rng = np.random.default_rng(19)
    for i, task in enumerate(order):
        ranks = retrieval[retrieval["task"].eq(task)]["true_target_rank"].astype(float).dropna().to_numpy()
        if ranks.size == 0:
            continue
        ax.boxplot(
            np.log10(ranks),
            positions=[i],
            widths=0.34,
            showfliers=False,
            patch_artist=True,
            boxprops={"facecolor": "white", "edgecolor": "black", "linewidth": 1.2},
            medianprops={"color": "black", "linewidth": 1.4},
            whiskerprops={"color": "black", "linewidth": 1.0},
            capprops={"color": "black", "linewidth": 1.0},
        )
        x = i + rng.normal(0, 0.055, size=ranks.size)
        ax.scatter(x, np.log10(ranks), s=12, color=colors[i], alpha=0.45, linewidth=0)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order, rotation=15, ha="right")
    ax.set_ylabel("log10 true-target retrieval rank")
    ax.set_title("Supplementary retrieval-rank distribution", loc="left", fontsize=12, fontweight="bold")
    save(fig, FIGURES / "phase2c_retrieval_rank_distribution")


def write_reviewer_response_prep(data: dict[str, pd.DataFrame]) -> None:
    transfer = data["state_transfer"].copy()
    caveats = pd.read_csv(TABLES / "supp_phase2c_endpoint_caveats.csv")
    primary = data["state_primary"]
    primary = primary[primary["metric_space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    text = f"""# Phase 2C Reviewer-Response Preparation

Generated: {now}

Task mode: triage-only pre-submission response preparation. Decision type: not applicable because no journal decision letter has been supplied.

## Response Strategy Summary

- Overall posture: evidence-first and bounded. Lead with matched-target STATE evidence, then name endpoint limitations plainly.
- Main risk: overclaiming Phase 2C as full cross-architecture confirmation.
- Best response anchor: matched-target Replogle Pearson drop, supported by Spearman, cosine, and sign-flip direction.
- Package readiness: draft-ready for anticipated reviewer concerns; final response letters require actual reviewer comments and manuscript line numbers.

## Internal Master Tracker (Not Reviewer-Facing)

| ID | Anticipated concern | Type | Severity | Proposed action | Work status | Expected output | Blocks finalization? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P2C.1 | STATE and GEARS are not directly comparable because metric spaces differ. | metric compatibility | major | State that Phase 2C tests directionality within STATE and does not claim absolute GEARS-vs-STATE performance equivalence. | VERIFIED_DONE | `STATE_GEARS_METRIC_COMPATIBILITY.md`; caveat table | no |
| P2C.2 | The R-L4 STATE target set is smaller than R-L1. | target-set composition | major | Lead with matched-target analysis and report full-summary endpoints as mixed. | VERIFIED_DONE | `state_transfer_drop.csv`; `phase2c_state_interpretation` Panel E | no |
| P2C.3 | Retrieval and UER do not uniformly support transfer degradation. | endpoint heterogeneity | major | Describe partial architecture support, not complete confirmation. | VERIFIED_DONE | `PHASE2C_DECISION.md`; interpretation report | no |
| P2C.4 | BNS and UER nulls are not externally verified. | biological-null validity | major | Keep BNS unverified and UER sensitivity-only. | VERIFIED_DONE | endpoint caveat table | no |
| P2C.5 | The second model was previously compute-blocked. | reproducibility | moderate | Preserve compute-blocked Phase 2B rows and append full-GPU performance-eligible Phase 2C rows. | VERIFIED_DONE | `gears_second_model_confirmatory.csv` | no |
| P2C.6 | Large STATE output files are not versioned in git. | reproducibility logistics | moderate | Track manifests, scripts, reports, and figures; keep large h5ad outputs local under ignored `results/state/`. | VERIFIED_DONE | analysis manifest and file manifest | no |

## Draft Response Language

Concern: The cross-context failure may be specific to GEARS.

Response: We addressed this concern by adding an independent STATE audit under the same locked Phase 2C task definitions. The STATE run completed Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4 on a CUDA-capable Linux GPU server. In the Replogle matched-target subset, within-context K562 R-L1 had higher agreement than K562-to-RPE1 R-L4, with a Pearson drop of {fmt(transfer.loc[transfer.metric.eq('pearson_delta'), 'mean_drop_source_minus_cross'].iloc[0])} and a 95% bootstrap interval of [{fmt(transfer.loc[transfer.metric.eq('pearson_delta'), 'ci95_low'].iloc[0])}, {fmt(transfer.loc[transfer.metric.eq('pearson_delta'), 'ci95_high'].iloc[0])}]. Spearman and cosine showed the same direction, and the sign-flip endpoint worsened in cross-context transfer. We therefore describe the result as partial cross-architecture support rather than complete confirmation.

Concern: STATE uses a different target set from GEARS.

Response: We audited split alignment against the frozen GEARS split files before STATE execution. STATE perturbation labels were normalized by the project convention that collapses explicit control partners, so `ctrl+X` and `X` are evaluated as the same target. The manuscript now reports normalized target counts and uses matched-target Replogle contrasts for the main Phase 2C interpretation.

Concern: Some endpoints do not support the same direction.

Response: We agree and have made this limitation explicit. Full-summary retrieval MRR was higher in STATE R-L4 than STATE R-L1, and UER@50 was slightly lower in the R-L4 full summary. Because these endpoints are affected by target-set composition, the manuscript leads with the matched-target contrast and states that Phase 2C provides bounded, partial support.

## Caveat Table

{md_table(caveats, ['issue','status','handling'])}

## Reviewer-Facing Boundary

Do not write that STATE fully confirms GEARS. The stronger and defensible sentence is: STATE partially reproduces the Replogle context-transfer degradation on matched targets, supporting an architecture-independent component of the transfer failure while leaving endpoint-specific caveats.
"""
    (REPORTS / "PHASE2C_REVIEWER_RESPONSE_PREP.md").write_text(text, encoding="utf-8")


def write_integrated_manuscript(data: dict[str, pd.DataFrame]) -> None:
    primary = data["state_primary"]
    primary = primary[primary["metric_space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    transfer = data["state_transfer"].copy()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    title = "Auditing Context-Transfer Failure in Perturbation-Response Models"
    text = f"""# {title}

Draft version: v0.3

Generated: {now}

## Abstract

Perturbation-response models are often evaluated by global transcriptomic similarity, but high global agreement can mask failures in perturbation-specific generalization. We built VirtualPerturb-Audit to separate global fit, target retrieval, unsupported-effect behavior, leakage risk, and cross-context transfer. In GEARS analyses, cross-context Replogle transfer showed strong degradation after matched-target restriction. Phase 2C added a full GPU STATE audit as an independent deep-architecture check. STATE partially reproduced the context-transfer phenotype on matched Replogle targets, with a Pearson drop of {fmt(transfer.loc[transfer.metric.eq('pearson_delta'), 'mean_drop_source_minus_cross'].iloc[0])} and endpoint-specific caveats. These results support an audit framing in which perturbation models are evaluated by robustness and failure modes rather than by a single leaderboard metric.

## Introduction

Single-cell perturbation models aim to predict transcriptional responses to genetic or molecular interventions. Their usefulness depends on whether they recover perturbation-specific structure under conditions that were not directly observed during training. Standard aggregate metrics can report strong agreement even when a model fails to identify the correct perturbation, predicts unsupported high-magnitude effects, or transfers poorly across cellular contexts.

VirtualPerturb-Audit was designed as a stress-test framework for these failure modes. The framework combines strict split definitions, perturbation-level evaluation, retrieval-based specificity, unsupported-effect metrics, leakage checks, and cross-context transfer tests. The central claim is not that one model is universally best. The central claim is that model behavior changes when the evaluation target shifts from global expression similarity to perturbation-specific and context-transfer reliability.

This draft reports the current Norman and Replogle GEARS audit together with the Phase 2C STATE confirmatory analysis. GEARS provides the primary audit trajectory, including matched-target Replogle stress tests. STATE provides an independent deep-architecture check of whether the Replogle transfer phenotype is specific to GEARS.

## Methods

### Data Scope and Split Policy

The audit used Norman perturbation splits and GEARS-compatible filtered Replogle essential-screen data. Frozen GEARS split files and Phase 2A/2B primary metrics were treated as immutable inputs during Phase 2C. Replogle analyses used within-context R-L1 tasks and cross-context R-L4 tasks. The K562-to-RPE1 direction was the main Phase 2C transfer direction for STATE.

### Metrics

For each perturbation target, predicted and observed expression profiles were converted to delta vectors by subtracting an appropriate control mean. The audit reported delta-Pearson, Spearman, RMSE, cosine similarity, retrieval Top1/Top5/MRR, UER@20/50/100, and sign-flip rate. Perturbation-level bootstrap intervals used 2,000 resamples. BNS remained unverified, and UER was interpreted as sensitivity-only.

### Matched-Target Transfer Sensitivity

The GEARS matched-target sensitivity analysis restricted each transfer direction to perturbation targets shared between the source-context within split and the cross-context evaluation split. This design separates transfer degradation from target-composition effects. Common-candidate retrieval further restricted the retrieval candidate pool to the same matched target set.

### STATE Phase 2C Audit

STATE was evaluated as a second deep architecture after the local CPU path was classified as not performance-eligible. Full STATE training and prediction were completed on a CUDA-capable Linux GPU server. Four locked tasks were evaluated: Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4. STATE perturbation labels were normalized by collapsing explicit control partners, so `ctrl+X` and `X` were evaluated as target `X`.

## Results

### GEARS Cross-Context Transfer Failed After Matched-Target Restriction

In GEARS, matched-target restriction did not rescue Replogle cross-context transfer. In K562-to-RPE1, matched-source Pearson fell from 0.2812 within context to -0.0070 cross context. The paired drop was 0.2883 with a 95% interval of [0.2559, 0.3206]. UER50 increased from 0.1532 to 0.3877, and sign-flip rate increased from 0.2714 to 0.5718.

The reverse RPE1-to-K562 direction showed the same pattern. Pearson fell from 0.5501 to 0.0021, with a paired drop of 0.5480 and a 95% interval of [0.5146, 0.5802]. UER50 and sign-flip penalties increased in the cross-context setting.

### STATE Partially Reproduced the Transfer Phenotype

The full GPU STATE audit completed all four locked tasks. STATE achieved delta-Pearson values of 0.4445 for Norman L1, 0.4060 for Norman L2, 0.2639 for Replogle K562 R-L1, and 0.1874 for Replogle K562-to-RPE1 R-L4.

Matched-target Replogle analysis gave the clearest Phase 2C signal. Across 15 shared targets, Pearson fell from 0.2955 in K562 R-L1 to 0.1792 in K562-to-RPE1 R-L4, a mean drop of 0.1163 with a 95% bootstrap interval of [0.0684, 0.1599]. Spearman and cosine similarity also decreased. UER50 and sign-flip rate moved in the worse cross-context direction, although UER50 had a bootstrap interval crossing zero.

### Endpoint Heterogeneity Limits the Claim

The Phase 2C result is not a complete confirmation. In the full-summary table, STATE R-L4 had higher retrieval MRR and slightly lower UER50 than STATE R-L1. These mixed endpoints are interpreted in the context of target-set differences, because STATE R-L4 contained 73 normalized targets compared with 216 targets in STATE Replogle K562 R-L1. The strongest defensible result is therefore matched-target, partial cross-architecture support.

## Discussion

The audit shows that perturbation-response model evaluation depends strongly on the endpoint being tested. GEARS showed high raw global agreement in some settings, but Replogle audit-delta and retrieval endpoints exposed weak perturbation-specific transfer. The matched-target analysis strengthened this interpretation by showing that cross-context degradation persisted after target-composition restriction.

STATE adds an important architecture check. Its matched-target Replogle results reproduce the direction of context-transfer degradation, which argues against a GEARS-only artifact. At the same time, STATE does not produce a uniform endpoint-level confirmation. This mixed pattern is useful rather than disappointing, because it identifies which claims are robust and which require narrower wording.

The present evidence supports an audit-framework claim. VirtualPerturb-Audit can reveal discrepancies between global fit, perturbation specificity, unsupported-effect behavior, and context transfer. It should not yet be framed as a final leaderboard or as a complete biological validation system. BNS remains unverified, and UER currently uses an internal sensitivity null.

## Current Figure and Table Package

Main Phase 2C figure: `figures/main/phase2c_state_interpretation.pdf`.

Supplementary Phase 2C figures:

- `figures/supplementary/phase2c_endpoint_heatmap.pdf`
- `figures/supplementary/phase2c_retrieval_rank_distribution.pdf`

Core tables:

{md_table(primary[['setting','split','metric_space','n_test_perturbations','pearson_delta','retrieval_mrr','uer50','sign_flip_rate']], ['setting','split','metric_space','n_test_perturbations','pearson_delta','retrieval_mrr','uer50','sign_flip_rate'])}

## Limitations

The current draft uses GEARS-compatible filtered Replogle data rather than the complete unavailable Figshare+ processed objects. BNS remains unverified. UER is sensitivity-only. STATE and GEARS absolute values should not be interpreted as a direct performance ranking when their metric spaces differ. Phase 2C supports a bounded cross-architecture transfer-degradation claim, not a complete confirmation across all endpoints.
"""
    (MANUSCRIPT / "MANUSCRIPT_v0.3.md").write_text(text, encoding="utf-8")


def main() -> None:
    data = load_data()
    build_supplementary_tables(data)
    plot_endpoint_heatmap(data)
    plot_retrieval_rank_distribution(data)
    write_reviewer_response_prep(data)
    write_integrated_manuscript(data)
    print("phase2c_supplementary_package_ok")


if __name__ == "__main__":
    main()
