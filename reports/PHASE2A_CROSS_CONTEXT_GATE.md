# Phase 2A Cross-Context Gate

Generated: 2026-08-25 21:25:17 local time

## Decision

```text
CONDITIONAL_GO_RL4
```

The within-context Replogle R-L1 full GEARS audit is complete for both K562 and RPE1. Cross-context R-L4 can proceed as a filtered-data external audit, with explicit `BNS_STATUS = UNVERIFIED` and no complete-data claims.

## Gate checks

| Check | Status | Evidence |
|---|---|---|
| K562 R-L1 GEARS full run | PASS | `run_status = COMPLETED_GEARS`; gears_raw Pearson 0.9851 [0.9836, 0.9864]; MRR 0.0445 [0.0290, 0.0624]. |
| RPE1 R-L1 GEARS full run | PASS | `run_status = COMPLETED_GEARS`; gears_raw Pearson 0.9709 [0.9690, 0.9727]; MRR 0.0209 [0.0158, 0.0263]. |
| External metric-divergence signal | PASS | K562 `SUPPORTS_DIVERGENCE`; RPE1 `SUPPORTS_DIVERGENCE`. |
| Filtered-data scope | PASS_WITH_SCOPE_LIMIT | Outputs use `Replogle_GEARS_filtered`; complete Figshare+ processed objects remain unavailable by command-line access. |
| BNS/replicate status | FAIL_FOR_BNS_ONLY | No validated biological replicate label; keep `BNS_STATUS = UNVERIFIED`. |
| Downstream tables and figures | PASS | `results/replogle/gears_rl1_summary.csv`, `results/tables/norman_replogle_rl1_comparison.csv`, `results/tables/metric_divergence_profile.csv`, `results/tables/replogle_gears_vs_probes.csv`, and main figures are generated. |

## Required R-L4 constraints

- Run `R-L4-K2R` and `R-L4-R2K` only on GEARS-compatible filtered essential-screen data.
- Preserve the same GEARS configuration family used for R-L1 unless a deviation is documented before execution.
- Keep `bns_status = UNVERIFIED` and `uer_null_status = sensitivity_only`.
- Compare R-L4 against R-L1 in both global-fit and perturbation-specific metrics.
- Treat cross-context performance as external generalization evidence, not complete Replogle genome-scale validation.

## Immediate next action

Launch the two R-L4 full GEARS runs after committing the completed R-L1 report package.
