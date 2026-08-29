# Phase 2A-RL4 Full Report

更新时间：2026-08-29 00:29 CST

## Current Status

```text
R-L4-K2R full run:       COMPLETED_GEARS_EVALUATION
R-L4-R2K full run:       COMPLETED_GEARS_EVALUATION
R-L4 postprocess:        COMPLETED
BNS:                     UNVERIFIED
Data scope:              GEARS-compatible filtered essential-screen data
UER/null status:         sensitivity_only
```

## Full-Run Summary

| direction | train_cell_line | test_cell_line | n_test_targets | pearson_delta | retrieval_top1 | retrieval_top5 | retrieval_mrr | uer50 | sign_flip_rate | elapsed_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| k2r | K562 | RPE1 | 732 | 0.0063 | 0.0027 | 0.0096 | 0.0126 | 0.3847 | 0.5520 | 52594.3120 |
| r2k | RPE1 | K562 | 732 | 0.0022 | 0.0000 | 0.0068 | 0.0089 | 0.4666 | 0.4962 | 21641.6380 |

## R-L1 vs R-L4 GEARS Comparison

| level | split | train_cell_line | test_cell_line | n_test_targets | pearson_delta | retrieval_mrr | uer50 | sign_flip_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-L1 within-context | R-L1-K562 | K562 | K562 | 216 | 0.2840 | 0.0497 | 0.1580 | 0.2691 |
| R-L1 within-context | R-L1-RPE1 | RPE1 | RPE1 | 308 | 0.4616 | 0.0262 | 0.0940 | 0.1720 |
| R-L4 cross-context | R-L4-K2R | K562 | RPE1 | 732 | 0.0063 | 0.0126 | 0.3847 | 0.5520 |
| R-L4 cross-context | R-L4-R2K | RPE1 | K562 | 732 | 0.0022 | 0.0089 | 0.4666 | 0.4962 |

## Interpretation

Both R-L4 directions completed on the filtered essential-screen data. Cross-context audit-delta Pearson is near zero in both directions, and perturbation retrieval remains near random: K2R top-1 is 0.0027 and R2K top-1 is 0.0000. This is substantially weaker than the completed R-L1 within-context GEARS runs.

The result supports the pre-registered stress-test expectation that cross-context transfer is much harder than within-context prediction. It also strengthens the core audit interpretation: global or within-context expression fit does not guarantee perturbation-specific, context-transferable signal.

GEARS does not clearly exceed the R-L4 mean-effect baseline/probe family in retrieval or audit-delta Pearson. The small positive Pearson values for GEARS are numerically above most R-L4 baseline rows but remain close to zero, while UER@50 and sign-flip rates are high. These rows should therefore be reported as cross-context failure/stress-test evidence, not as cross-context validation.

## Guardrails

- All R-L4 results are restricted to `GEARS-compatible filtered essential-screen data`.
- `BNS_STATUS = UNVERIFIED` remains unchanged because no validated biological replicate field is available.
- UER is a sensitivity-only control-null audit, not a replicate-derived biological upper bound.
- The R-L4 adapter is `source_context_train_target_context_control_basal_prediction`; it is not native GEARS cell-line-aware condition splitting.
- Smoke and interrupted runs remain provenance only and are excluded from performance interpretation.

## Outputs

- `results/replogle/gears_rl4_summary.csv`
- `results/tables/replogle_rl4_gears_cross_context.csv`
- `results/tables/replogle_rl4_gears_vs_baselines.csv`
- `results/tables/replogle_rl1_rl4_gears_comparison.csv`
- `figures/main/replogle_rl1_rl4_gears_transfer.{png,svg,pdf}`

## Gate Decision

```text
PHASE2A_RL4_COMPLETE_FILTERED_DATA
```

Next executable step: carry the R-L4 result into manuscript/result synthesis, while keeping complete-data replication blocked until the official Figshare+ processed objects become command-line accessible.
