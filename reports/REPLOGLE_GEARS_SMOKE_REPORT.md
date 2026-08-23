# Replogle GEARS Smoke Report

Date: 2026-08-23

## Status

```text
K562_R-L1_BOUNDED_SMOKE_COMPLETE_NOT_PERFORMANCE
```

The first Replogle GEARS compatibility smoke completed on the locally downloaded GEARS-compatible filtered K562 essential-screen data. This is an executable-chain test only, not a model-performance result.

## Successful Run

| Field | Value |
|---|---|
| Run directory | `results/replogle/gears/gears_replogle_k562_smoke_20260823T030844Z/` |
| Dataset | `Replogle_K562_GEARS_filtered` |
| Split | `R-L1-K562` |
| Scope | `bounded_smoke_not_performance` |
| Device | CPU |
| Train batches | 1 |
| Eval batches | 1 |
| Evaluated non-control perturbations | 1 |
| Train loss | 0.5232884883880615 |
| Filtered GO nodes | 9,853 |
| Filtered GO edges | 12,107,865 |
| Elapsed seconds | 31.738 |
| BNS status | `UNVERIFIED` |

Outputs:

- `metadata.json`
- `model/model.pt`
- `model/config.pkl`
- `gears_smoke_evaluated_perturbations.csv`

## Failed Attempts Preserved

Two failed smoke attempts are preserved as provenance:

| Run directory | Status | Error |
|---|---|---|
| `results/replogle/gears/gears_replogle_k562_smoke_20260823T024533Z/` | `FAILED_GEARS_REPLOGLE_SMOKE` | Missing control cells in first sampled smoke h5ad because `ctrl` was truncated from the train condition list. |
| `results/replogle/gears/gears_replogle_k562_smoke_20260823T024712Z/` | `FAILED_GEARS_REPLOGLE_SMOKE` | GEARS attempted to write a co-expression edge list under `data/raw/replogle_k562_gears_smoke`, which did not exist. |

Both issues were fixed in `scripts/run_gears_replogle_smoke.py`.

## Interpretation

The GEARS executable chain now works for a bounded Replogle K562 filtered-data smoke path: sampled h5ad creation, custom R-L1 split dictionary, PyG graph creation/loading, filtered GO graph construction, model initialization, one training batch, checkpoint save, one evaluation batch, and metadata export.

This does not validate full Replogle performance. Full filtered-data runs should still be launched under `CONDITIONAL_GO_GEARS_FILTERED`, with `BNS_STATUS = UNVERIFIED`.
