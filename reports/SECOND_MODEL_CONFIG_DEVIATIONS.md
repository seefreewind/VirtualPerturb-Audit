# Second Model Configuration Deviations

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
