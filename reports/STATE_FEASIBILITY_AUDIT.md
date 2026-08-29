# STATE Feasibility Audit

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
