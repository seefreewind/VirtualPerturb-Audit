#!/usr/bin/env python3
"""Finalize Phase 2B reports after matched-target and second-model feasibility audits."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def read_metric(direction: str, metric: str) -> pd.Series:
    df = pd.read_csv(ROOT / "results/tables/replogle_matched_rl1_rl4_sensitivity.csv")
    row = df[(df["direction"] == direction) & (df["metric"] == metric)]
    if row.empty:
        raise KeyError((direction, metric))
    return row.iloc[0]


def fmt(x: float) -> str:
    return f"{x:.4f}"


def write_second_model_table() -> None:
    rows = [
        {
            "task": "Norman L1",
            "requested_role": "second deep architecture confirmatory run",
            "candidate": "STATE state_sm/state",
            "local_status": "NOT_PERFORMANCE_ELIGIBLE_COMPUTE_BLOCKED",
            "pearson_delta": pd.NA,
            "mrr": pd.NA,
            "uer50": pd.NA,
            "sign_flip_rate": pd.NA,
            "evidence": "STATE CLI passed; perturb_mean and state_sm smoke passed; state_sm 1-step CPU smoke used 66.3M parameters.",
            "reason": "Official full training is 40k-400k steps; local CPU-only trainer path makes four full tasks multi-week scale.",
        },
        {
            "task": "Norman L2",
            "requested_role": "second deep architecture confirmatory run",
            "candidate": "STATE state_sm/state",
            "local_status": "NOT_PERFORMANCE_ELIGIBLE_COMPUTE_BLOCKED",
            "pearson_delta": pd.NA,
            "mrr": pd.NA,
            "uer50": pd.NA,
            "sign_flip_rate": pd.NA,
            "evidence": "No performance-eligible second deep model run launched after Norman L1 speed smoke.",
            "reason": "Would repeat same CPU-only training bottleneck on a second Norman split.",
        },
        {
            "task": "Replogle K562 R-L1",
            "requested_role": "second deep architecture confirmatory run",
            "candidate": "STATE state_sm/state",
            "local_status": "NOT_PERFORMANCE_ELIGIBLE_COMPUTE_BLOCKED",
            "pearson_delta": pd.NA,
            "mrr": pd.NA,
            "uer50": pd.NA,
            "sign_flip_rate": pd.NA,
            "evidence": "Replogle h5ad is compatible, but full data are 162,751 cells x 5,000 genes.",
            "reason": "Full second-architecture training is not a fair local Phase 2B deliverable on this CPU path.",
        },
        {
            "task": "Replogle K562 -> RPE1 R-L4",
            "requested_role": "second deep architecture confirmatory run",
            "candidate": "STATE state_sm/state",
            "local_status": "NOT_PERFORMANCE_ELIGIBLE_COMPUTE_BLOCKED",
            "pearson_delta": pd.NA,
            "mrr": pd.NA,
            "uer50": pd.NA,
            "sign_flip_rate": pd.NA,
            "evidence": "R-L4 adapter is conceptually compatible, but target-context full evaluation requires a trained source-context model.",
            "reason": "No trained STATE source-context checkpoint exists under fair full-run conditions.",
        },
    ]
    out = ROOT / "results/tables/gears_second_model_confirmatory.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)


def write_cross_architecture_figure() -> None:
    labels = ["GEARS\nPhase 2A", "GEARS\nMatched", "scGPT\nlocal", "STATE\nCLI", "STATE deep\nfull"]
    values = [1.0, 1.0, 0.0, 0.65, 0.15]
    colors = ["#0F4D92", "#0F4D92", "#B64342", "#3A7D44", "#B64342"]
    notes = [
        "complete",
        "supports\ncollapse",
        "not fairly\nexecutable",
        "smoke\npasses",
        "compute\nblocked",
    ]

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    bars = ax.bar(labels, values, color=colors, width=0.62)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Phase 2B gate status")
    ax.set_yticks([0, 0.5, 1.0], ["blocked", "partial", "pass"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    for bar, note in zip(bars, notes):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.04,
            note,
            ha="center",
            va="bottom",
            fontsize=8.5,
        )
    ax.set_title("Phase 2B Cross-Architecture Audit", pad=10)
    fig.tight_layout()
    out = ROOT / "figures/main/model_cross_architecture_audit.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)


def write_state_report() -> None:
    path = ROOT / "reports/STATE_FEASIBILITY_AUDIT.md"
    text = """# STATE Feasibility Audit

更新时间：2026-08-29

## Verdict

```yaml
official_feasibility: FAIRLY_EVALUABLE_IN_PRINCIPLE
local_cli_smoke: PASS
local_perturb_mean_smoke: PASS
local_state_sm_smoke: PASS_1_STEP_ONLY
local_full_confirmatory_verdict: NOT_FAIRLY_EVALUABLE_ON_THIS_CPU_WORKSTATION
candidate_role: fallback_second_model_after_scGPT_local_failure
license_risk: NONCOMMERCIAL_RESEARCH_ONLY
package_route: uv_tool_install_arc-state
installed_version: arc-state==0.11.1
```

STATE is a plausible official perturbation-response framework, and it installed successfully through the documented `uv tool install arc-state` route. The command-line interface started cleanly and exposed `state tx train`, `state tx predict`, `state tx infer`, and `state tx preprocess_train`. A small Norman L1 adapter smoke passed through both an official mean baseline and the `state_sm` deep model for one training step.

The full second-deep-architecture confirmatory matrix was not launched because the only local trainer path selected CPU despite MPS availability. The `state_sm` smoke instantiated a 66.3M-parameter model; official full training settings are 40,000 to 400,000 steps. Four full Phase 2B tasks on this path would be a multi-week local run, not a fair in-turn replication deliverable.

## Official Source Audit

```yaml
repository: https://github.com/ArcInstitute/state
repository_status: official Arc Institute implementation
commit_checked: 9bbfe78a434a55205e4de834e1ea99f85f7a3add
official_news: https://arcinstitute.org/news/virtual-cell-model-state
preprint: https://www.biorxiv.org/content/10.1101/2025.06.26.661135v1.full-text
code_license: CC BY-NC-SA 4.0
model_weight_license: Arc State Model Non-Commercial License plus Acceptable Use Policy
perturbation_prediction_supported: true
genetic_perturbation_supported: true
custom_dataset_supported: true
cross_context_supported: adapter_required_for_this_project
```

## Local Smoke Evidence

| Check | Result |
|---|---|
| `state --help` | pass |
| `state tx --help` | pass |
| `state tx train --help` | pass |
| `state tx infer --help` | pass |
| Norman L1 STATE-compatible h5ad/TOML creation | pass |
| `model=perturb_mean` 1-step train | pass |
| `model=perturb_mean` `predict --profile anndata` | pass |
| `model=state_sm` 1-step train | pass |

Smoke files were written under `data/processed/state_phase2b/smoke/` and `results/state/smoke/`. These are execution-chain evidence only and are not performance-eligible.

## Compatibility Boundary

The adapter can map existing GEARS-compatible h5ad files to STATE by adding:

- `gene`: normalized perturbation label derived from `condition`;
- `cell_type`: fixed context label for Norman, K562, or RPE1;
- `gem_group`: batch label required by the STATE data module;
- TOML few-shot lists derived from frozen GEARS split dictionaries.

For R-L4, the fair design remains source-context K562 training plus target-context RPE1 control-basal prediction and RPE1 truth evaluation. A full result requires a performance-eligible trained STATE source checkpoint.

## Decision

```text
STATE_DEEP_LOCAL_VERDICT = NOT_FAIRLY_EVALUABLE_ON_THIS_CPU_WORKSTATION
SECOND_DEEP_MODEL_GATE = NO_SECOND_MODEL_FAIRLY_REPRODUCIBLE_LOCALLY
```
"""
    path.write_text(text, encoding="utf-8")


def write_split_compatibility() -> None:
    path = ROOT / "reports/SECOND_MODEL_SPLIT_COMPATIBILITY.md"
    text = """# Second Model Split Compatibility

更新时间：2026-08-29

## Scope

Second-model first round was restricted to four tasks:

| Task | Dataset | Split | Compatibility |
|---|---|---|---|
| M1 | Norman | L1 | compatible with frozen split after STATE perturbation-label adapter |
| M2 | Norman | L2 | compatible with frozen split after STATE perturbation-label adapter |
| M3 | Replogle K562 | R-L1-K562 | compatible with frozen split after `GENE+ctrl` to `GENE` mapping |
| M4 | Replogle K562 -> RPE1 | R-L4-K2R | conceptually compatible, but requires trained source-context checkpoint |

No new random splits were created.

## Frozen Split Sources

| Task | Split source |
|---|---|
| Norman L1 | `data/raw/norman/splits/virtualperturb_audit_L1_seed1.pkl` |
| Norman L2 | `data/raw/norman/splits/virtualperturb_audit_L2_seed1.pkl` |
| Replogle K562 R-L1 | `data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L1-K562_seed1_rl1.pkl` |
| Replogle K562 -> RPE1 R-L4 | `data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L4-K2R_seed1_rl4.pkl` |

## Adapter Result

The script `scripts/prepare_state_phase2b_inputs.py` converts each task into a STATE-compatible h5ad directory plus TOML file. For smoke testing, Norman L1 produced 180 cells, 9 conditions, and 5,045 genes and was accepted by the STATE data module.

## Final Compatibility Decision

```text
SPLITS_COMPATIBLE_WITH_STATE_ADAPTER = TRUE
PERFORMANCE_ELIGIBLE_SECOND_DEEP_MODEL_RUNS = FALSE
```

The blocker is compute/runtime fairness, not split incompatibility.
"""
    path.write_text(text, encoding="utf-8")


def write_config_deviations() -> None:
    path = ROOT / "reports/SECOND_MODEL_CONFIG_DEVIATIONS.md"
    text = """# Second Model Configuration Deviations

更新时间：2026-08-29

## scGPT

No performance run was launched. scGPT was rejected after local environment audit because a reproducible import/smoke environment could not be established without replacing the frozen GEARS dependency stack.

## STATE

| Item | Official/default | Phase 2B local action | Performance eligible |
|---|---|---|---|
| Installation | `uv tool install arc-state` | followed exactly; installed `arc-state==0.11.1` | yes for smoke |
| CLI smoke | not a performance run | `state --help`, `state tx --help`, train/infer help | no |
| h5ad/TOML adapter | custom datasets allowed | generated from frozen GEARS h5ad and split dictionaries | no |
| `perturb_mean` smoke | official built-in model, training forced to 1 step | Norman L1 smoke train and predict | no |
| `state_sm` smoke | official small STATE model | Norman L1 1-step train only | no |
| Full `state`/`state_sm` matrix | 40k-400k steps in official examples/defaults | not launched on CPU workstation | not available |

## Decision

No second-model metric in `results/tables/gears_second_model_confirmatory.csv` is performance-eligible. The table records the blocked status for the four requested tasks.
"""
    path.write_text(text, encoding="utf-8")


def write_manuscript_files() -> None:
    k_p = read_metric("K562_within_vs_K562_to_RPE1", "pearson_delta")
    k_u = read_metric("K562_within_vs_K562_to_RPE1", "uer50")
    k_s = read_metric("K562_within_vs_K562_to_RPE1", "sign_flip_rate")
    r_p = read_metric("RPE1_within_vs_RPE1_to_K562", "pearson_delta")
    r_u = read_metric("RPE1_within_vs_RPE1_to_K562", "uer50")
    r_s = read_metric("RPE1_within_vs_RPE1_to_K562", "sign_flip_rate")
    methods = f"""# METHODS v0.1

## Phase 2B Matched-Target Sensitivity

The matched-target sensitivity analysis reused frozen GEARS outputs from the Replogle Phase 2A within-context and cross-context runs. No completed GEARS run was retrained. For each transfer direction, perturbation targets were restricted to the intersection of the source-context within split and the corresponding cross-context evaluation split. Metrics were recomputed on this matched target set to separate target-composition effects from context-transfer effects.

For K562-to-RPE1, the source-context matched set contained {int(k_p['n_targets'])} perturbation targets. For RPE1-to-K562, the source-context matched set contained {int(r_p['n_targets'])} perturbation targets. The analysis reported paired within-minus-cross differences for correlation and retrieval metrics, and cross-minus-within penalties for error and uncertainty/error-rate metrics. Bootstrap intervals used target-level resampling.

Common-candidate retrieval was recomputed by restricting the candidate pool to the same matched target set before ranking. This analysis tests whether retrieval deterioration is driven by a larger or different candidate universe.

## Phase 2B Second-Model Feasibility

scGPT and STATE were audited as candidate second models. scGPT was rejected for local Phase 2B execution because a reproducible import and smoke environment could not be established without replacing the frozen GEARS dependency stack. STATE installed successfully through the official `uv tool install arc-state` route and passed command-line and one-step smoke tests. The full deep STATE confirmatory matrix was not launched because the local trainer used CPU and official full-run settings require tens to hundreds of thousands of steps. Smoke outputs were retained as executable-chain evidence only and were excluded from performance tables.

## Data Scope

All Replogle analyses use GEARS-compatible filtered essential-screen data. Complete Figshare+ processed Replogle objects were not available through the command-line route used in this project, and replicate-bounded negative sampling remains unverified.
"""
    results = f"""# RESULTS v0.1

## Matched-Target Sensitivity

Matched-target restriction did not rescue cross-context transfer. In the K562-to-RPE1 direction, matched-source Pearson fell from {fmt(k_p['within_estimate'])} within context to {fmt(k_p['cross_estimate'])} cross context, a paired drop of {fmt(k_p['paired_difference'])} with a 95% interval of [{fmt(k_p['ci_low'])}, {fmt(k_p['ci_high'])}]. UER50 increased from {fmt(k_u['within_estimate'])} to {fmt(k_u['cross_estimate'])}, and the sign-flip rate increased from {fmt(k_s['within_estimate'])} to {fmt(k_s['cross_estimate'])}.

The reverse RPE1-to-K562 direction showed the same pattern. Matched-source Pearson fell from {fmt(r_p['within_estimate'])} to {fmt(r_p['cross_estimate'])}, a paired drop of {fmt(r_p['paired_difference'])} with a 95% interval of [{fmt(r_p['ci_low'])}, {fmt(r_p['ci_high'])}]. UER50 increased from {fmt(r_u['within_estimate'])} to {fmt(r_u['cross_estimate'])}, and the sign-flip rate increased from {fmt(r_s['within_estimate'])} to {fmt(r_s['cross_estimate'])}.

Common-candidate retrieval stayed low. Its MRR drop was directionally consistent but did not provide the strongest statistical evidence because the bootstrap interval crossed zero in the source-context matched comparison. The strongest evidence for transfer collapse came from delta correlation, UER50, and sign-flip penalties.

## Second-Model Audit

No performance-eligible second deep architecture was completed locally. scGPT failed the local fair-execution gate. STATE passed official CLI and one-step smoke tests, including a `state_sm` deep-model smoke, but full deep runs were blocked by CPU-only execution and expected multi-week runtime for the four-task matrix. Phase 2B therefore supports a conditional manuscript path based on the matched-target GEARS stress test, with second-architecture confirmation deferred to a GPU/Linux execution environment.
"""
    manuscript = ROOT / "manuscript"
    manuscript.mkdir(parents=True, exist_ok=True)
    (manuscript / "METHODS_v0.1.md").write_text(methods, encoding="utf-8")
    (manuscript / "RESULTS_v0.1.md").write_text(results, encoding="utf-8")


def write_decision() -> None:
    k_p = read_metric("K562_within_vs_K562_to_RPE1", "pearson_delta")
    r_p = read_metric("RPE1_within_vs_RPE1_to_K562", "pearson_delta")
    path = ROOT / "reports/PHASE2B_DECISION.md"
    text = f"""# Phase 2B Decision

更新时间：2026-08-29

## Gates

| Gate | Decision | Evidence |
|---|---|---|
| Phase 2A frozen before Phase 2B | pass | commit `6872a97` |
| Matched-target registry | pass | `results/tables/replogle_matched_target_registry.tsv` |
| Matched-target sensitivity | pass | `reports/PHASE2B_MATCHED_TARGET_SENSITIVITY.md` |
| Common-candidate retrieval | pass | included in `results/tables/replogle_matched_rl1_rl4_sensitivity.csv` |
| scGPT feasibility | fail locally | official candidate, but local fair-execution gate failed |
| STATE feasibility | partial | official CLI and smoke pass; full deep matrix compute-blocked |
| Second deep architecture performance | fail locally | no performance-eligible metrics for four tasks |

## Scientific Decision

```text
MATCHED_TARGET_GATE = MATCHED_SUPPORTS_TRANSFER_COLLAPSE
SECOND_DEEP_MODEL_GATE = NO_SECOND_MODEL_FAIRLY_REPRODUCIBLE_LOCALLY
PHASE2B_DECISION = CONDITIONAL_MANUSCRIPT_NOT_PROMOTE_TO_FULL_ARCHITECTURE_GENERAL_CLAIM
```

The matched-target Replogle analysis supports the central transfer-collapse result. K562-to-RPE1 Pearson dropped by {fmt(k_p['paired_difference'])}; RPE1-to-K562 Pearson dropped by {fmt(r_p['paired_difference'])}. These drops persisted after target matching, so the effect is not explained by a different held-out target composition.

The manuscript can move forward as a conditional stress-test paper centered on metric divergence and context-transfer failure in GEARS. It should not claim architecture-general failure until a second deep model is completed in a suitable GPU/Linux environment.

## Strongest Result

The strongest Phase 2B result is that matched-target restriction preserves the cross-context collapse in both directions, especially for delta Pearson, UER50, and sign-flip penalties.

## Main Limitation

The main limitation is not the matched-target analysis; it is the absence of a performance-eligible second deep architecture run. Replogle remains filtered-data scope, and BNS remains unverified.

## Next Recommended Action

Run the second architecture on a GPU/Linux environment using the existing STATE adapter first, then rerun the same four-task matrix without changing frozen GEARS results or matched-target definitions.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    write_second_model_table()
    write_cross_architecture_figure()
    write_state_report()
    write_split_compatibility()
    write_config_deviations()
    write_manuscript_files()
    write_decision()


if __name__ == "__main__":
    main()
