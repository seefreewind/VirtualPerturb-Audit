# Phase 2A-RL4 Progress Report

更新时间：2026-08-29 00:30 CST

## Current Status

```text
R-L1 within-context gate:    CONDITIONAL_GO_RL4
R-L4 runner/configs:         COMPLETE
R-L4-K2R smoke:              PASS
R-L4-R2K smoke:              PASS
R-L4-K2R full run:           COMPLETED_GEARS_EVALUATION
R-L4-R2K full run:           COMPLETED_GEARS_EVALUATION
R-L4 postprocess:            COMPLETED
BNS:                         UNVERIFIED
Data scope:                  GEARS-compatible filtered essential-screen data
UER/null status:             sensitivity_only
```

## R-L4 Adapter

GEARS `custom` split support is condition-level. Because K562 and RPE1 share perturbation condition names, a single combined AnnData cannot encode "K562 train, RPE1 test" without either mixing contexts or corrupting perturbation gene names.

The implemented R-L4 adapter therefore uses this explicit workflow:

1. Train GEARS on the source context only.
2. Use target-context controls as basal inputs for GEARS `predict()`.
3. Predict the shared eligible perturbation targets.
4. Compare predictions with target-context perturbation truth in target-control audit-delta space.

This preserves the perturbation graph vocabulary and keeps the target context out of training/model selection. It is a GEARS-compatible cross-context inference adapter, not a claim that official GEARS natively supports cell-line-aware condition splits.

## Full-Run Results

| Direction | Run directory | Status | Eval targets | Pearson delta | Top-1 | Top-5 | MRR | UER@50 | Sign-flip | Elapsed |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K562 -> RPE1 | `results/replogle/gears/rl4_k2r_20260827T020001Z/` | `COMPLETED_GEARS_EVALUATION` | 732 | 0.0063 [0.0005, 0.0123] | 0.0027 | 0.0096 | 0.0126 | 0.3847 | 0.5520 | 52,594.3 s |
| RPE1 -> K562 | `results/replogle/gears/rl4_r2k_20260828T090923Z/` | `COMPLETED_GEARS_EVALUATION` | 732 | 0.0022 [0.0007, 0.0036] | 0.0000 | 0.0068 | 0.0089 | 0.4666 | 0.4962 | 21,641.6 s |

## Completed Outputs

- `results/replogle/gears_rl4_summary.csv`
- `results/tables/replogle_rl4_gears_cross_context.csv`
- `results/tables/replogle_rl4_gears_vs_baselines.csv`
- `results/tables/replogle_rl1_rl4_gears_comparison.csv`
- `figures/main/replogle_rl1_rl4_gears_transfer.{png,svg,pdf}`
- `reports/PHASE2A_RL4_FULL_REPORT.md`

## Smoke Results

| Direction | Run directory | Status | Train batches | Eval targets | Elapsed |
|---|---|---:|---:|---:|---:|
| K562 -> RPE1 | `results/replogle/gears/rl4_k2r_20260825T133904Z/` | `COMPLETED_GEARS_BATCH_SMOKE_NOT_PERFORMANCE` | 1 | 5 | 36.5 s |
| RPE1 -> K562 | `results/replogle/gears/rl4_r2k_20260825T133952Z/` | `COMPLETED_GEARS_BATCH_SMOKE_NOT_PERFORMANCE` | 1 | 5 | 35.0 s |

Smoke outputs are executable-chain evidence only and must not enter performance figures or manuscript claims.

## Interpretation

Both R-L4 full directions completed. Cross-context audit-delta Pearson is near zero, perturbation retrieval is near random, and UER/sign-flip burden is high. This supports the pre-registered expectation that context transfer is substantially harder than within-context R-L1 prediction.

The R-L4 result should be interpreted as stress-test evidence, not as cross-context validation. It strengthens the Phase 2A audit message that within-context/global expression agreement does not imply perturbation-specific transfer across cell-line contexts.

## Interpretation Guardrails

- All outputs remain labeled `GEARS-compatible filtered essential-screen data`.
- `BNS_STATUS = UNVERIFIED` remains unchanged.
- `uer_null_status = sensitivity_only` remains unchanged.
- R-L4 evaluates cross-context transfer behavior, not complete Replogle genome-scale validation.
- The adapter is GEARS-compatible cross-context inference, not native cell-line-aware GEARS splitting.
- Smoke and interrupted runs remain provenance only and are excluded from performance interpretation.
