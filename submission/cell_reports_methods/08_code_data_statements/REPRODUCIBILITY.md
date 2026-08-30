# Reproducibility

This file summarizes how to inspect and reproduce the frozen VirtualPerturb-Audit evidence package.

## Frozen Status

CRM preparation did not run new GEARS/STATE benchmarks, alter split files, download complete Replogle Figshare+ objects, or improve model results. It generated manuscript, audit, figure, and submission-organization artifacts from existing Phase 1/2A/2B/2C outputs.

## Core Evidence Files

- `reports/PHASE2A_RL1_FULL_REPORT.md`
- `reports/PHASE2A_RL4_FULL_REPORT.md`
- `reports/PHASE2B_MATCHED_TARGET_SENSITIVITY.md`
- `reports/PHASE2C_DECISION.md`
- `reports/PHASE2C_RESULT_INTERPRETATION.md`
- `results/tables/replogle_matched_rl1_rl4_sensitivity.csv`
- `results/tables/replogle_rl1_rl4_gears_comparison.csv`
- `results/tables/state_phase2c_primary_metrics.csv`
- `results/tables/state_transfer_drop.csv`
- `results/tables/gears_state_primary_comparison.csv`

## CRM Build Command

```bash
environment/state-postprocess-venv/bin/python scripts/build_crm_submission_package.py
```

## Required Cautions

- Replogle data scope: GEARS-compatible filtered essential-screen data.
- BNS: unverified.
- UER: sensitivity-only.
- GEARS R-L4: cross-context inference adapter.
- STATE: partial endpoint-mixed support.
- GEARS/STATE absolute values: not a direct leaderboard.
