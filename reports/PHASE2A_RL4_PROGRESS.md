# Phase 2A-RL4 Progress Report

更新时间：2026-08-25 21:45 CST

## Current Status

```text
R-L1 within-context gate:    CONDITIONAL_GO_RL4
R-L4 runner/configs:         READY
R-L4-K2R smoke:              PASS
R-L4-R2K smoke:              PASS
R-L4 full runs:              READY_TO_LAUNCH
BNS:                         UNVERIFIED
Data scope:                  GEARS-compatible filtered essential-screen data
```

## R-L4 Adapter

GEARS `custom` split support is condition-level. Because K562 and RPE1 share perturbation condition names, a single combined AnnData cannot encode "K562 train, RPE1 test" without either mixing contexts or corrupting perturbation gene names.

The implemented R-L4 adapter therefore uses this explicit workflow:

1. Train GEARS on the source context only.
2. Use target-context controls as basal inputs for GEARS `predict()`.
3. Predict the shared eligible perturbation targets.
4. Compare predictions with target-context perturbation truth in target-control audit-delta space.

This preserves the perturbation graph vocabulary and keeps the target context out of training/model selection. It is a GEARS-compatible cross-context inference adapter, not a claim that official GEARS natively supports cell-line-aware condition splits.

## Files Added

- `scripts/run_gears_replogle_rl4.py`
- `configs/replogle/gears_rl4_k2r_seed1.yaml`
- `configs/replogle/gears_rl4_r2k_seed1.yaml`

## Smoke Results

| Direction | Run directory | Status | Train batches | Eval targets | Elapsed |
|---|---|---:|---:|---:|---:|
| K562 -> RPE1 | `results/replogle/gears/rl4_k2r_20260825T133904Z/` | `COMPLETED_GEARS_BATCH_SMOKE_NOT_PERFORMANCE` | 1 | 5 | 36.5 s |
| RPE1 -> K562 | `results/replogle/gears/rl4_r2k_20260825T133952Z/` | `COMPLETED_GEARS_BATCH_SMOKE_NOT_PERFORMANCE` | 1 | 5 | 35.0 s |

Smoke outputs are executable-chain evidence only and must not enter performance figures or manuscript claims.

## Launch Commands

```bash
PYTHONPATH=. environment/gears-venv/bin/python scripts/run_gears_replogle_rl4.py --direction k2r
PYTHONPATH=. environment/gears-venv/bin/python scripts/run_gears_replogle_rl4.py --direction r2k
```

## Interpretation Guardrails

- All outputs must remain labeled `GEARS-compatible filtered essential-screen data`.
- `BNS_STATUS = UNVERIFIED` remains unchanged.
- `uer_null_status = sensitivity_only` remains unchanged.
- R-L4 evaluates cross-context transfer behavior, not complete Replogle genome-scale validation.
- R-L4 should be compared against completed R-L1 K562/RPE1 references and against R-L4 baseline/probe rows already present in `results/replogle/replogle_summary.csv`.

