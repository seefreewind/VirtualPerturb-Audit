# Replogle RPE1 GEARS Smoke Report

Date: 2026-08-23

## Status

```text
RPE1_R-L1_BOUNDED_SMOKE_COMPLETE_NOT_PERFORMANCE
Verdict: PASS
```

The bounded GEARS RPE1 smoke completed end to end on the locally downloaded GEARS-compatible filtered RPE1 essential-screen data. This is executable-chain evidence only, not a model-performance result.

## Successful Run

| Field | Value |
|---|---|
| Run directory | `results/replogle/gears/gears_replogle_rpe1_smoke_20260823T072300Z/` |
| Dataset | `Replogle_RPE1_GEARS_filtered` |
| Data completeness caveat | GEARS-compatible filtered essential-screen data; NOT the complete Figshare+ processed objects |
| Split | `R-L1-RPE1` (frozen, hash `288d45dbeb512ce5`) |
| Scope | `bounded_smoke_not_performance` |
| Purpose | `executable_chain_smoke` |
| performance_eligible | `false` |
| Device | CPU |
| Seed | 1 |
| Epochs | 1 train batch (batch smoke; no full epoch) |
| Train batches completed | 1 |
| Evaluated non-control perturbations | 2 (ABCB10+ctrl, ABCE1+ctrl) |
| Train loss (first/last) | 0.7931 / 0.7931 |
| Filtered GO nodes | 9,853 |
| Filtered GO edges | 12,107,865 |
| Smoke h5ad | `data/processed/replogle_rpe1_gears_smoke/perturb_processed.h5ad` |
| Elapsed seconds | 1,177.2 (dominated by one-time GO graph construction) |
| BNS status | `UNVERIFIED` |
| Git commit | `032c4a5` |
| GEARS version | `cell-gears 0.1.2` |
| prior_hash | `46c3dfe354d8ad5c` (SHA-256 of `data/raw/essential_all_data_pert_genes.pkl`) |

Outputs:

- `metadata.json`
- `gears_smoke_evaluated_perturbations.csv`
- `model/model.pt`, `model/config.pkl`

## Failed Attempt Preserved

| Run directory | Status | Error |
|---|---|---|
| `results/replogle/gears/gears_replogle_rpe1_smoke_20260823T072149Z/` | `FAILED_GEARS_REPLOGLE_SMOKE` | `KeyError: 'AC118549.1+ctrl'` in `get_dataloader`: the raw-obs split dict contained conditions dropped by GEARS `PertData.load` (`filter_pert_in_go` GO-gene filter). |

Fix recorded in `CHANGELOG.md` (2026-08-23 Phase 2A-RL1 entry): after `PertData.load`, the custom split dict is rebuilt from the GEARS-filtered adata using the same frozen per-cell R-L1 assignment (`_gears_vocabulary.tsv` sidecar records condition counts). This mirrors the frozen Norman custom-split convention; the official GEARS package is not modified.

## Gate Checks (PASS criteria)

| Check | Status | Evidence |
|---|---|---|
| Model loads | PASS | `GEARS` init + `model_initialize` completed with filtered GO tensor |
| Training completes | PASS | 1 train batch completed, loss finite (0.7931) |
| Prediction completes | PASS | 1 eval batch completed; predicted/truth means returned |
| Metric pipeline completes | PASS | smoke summary CSV + metadata export written |
| Condition labels remain valid | PASS | split dict rebuilt inside GEARS vocabulary; frozen per-cell assignment unchanged |
| No split contamination | PASS | frozen R-L1 assignment verified at full-data level (`results/replogle/rl1_split_reproducibility.csv`: hashes match) |
| No fatal vocabulary mismatch | PASS | all split-dict conditions exist in GEARS-filtered obs after rebuild |

## Interpretation

The complete GEARS executable chain works for a bounded Replogle RPE1 filtered-data smoke: sample h5ad creation, frozen R-L1 split injection, PyG graph creation/loading, filtered GO graph construction, model initialization, one training batch, checkpoint save, one evaluation batch, and metadata export.

This does not validate full Replogle RPE1 performance. The GO graph construction took about 15 minutes once (not cached for this dataset name); it will be cached for the full run.

## Decision

```text
PASS
```

Proceed to STEP 2 (frozen full-run configs) and STEP 3 (R-L1-K562 full run) under `CONDITIONAL_GO_GEARS_FILTERED`, with `BNS_STATUS = UNVERIFIED` and the filtered-data caveat on every output.