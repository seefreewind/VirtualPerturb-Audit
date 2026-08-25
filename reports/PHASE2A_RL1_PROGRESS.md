# Phase 2A-RL1 Progress Report

更新时间：2026-08-25 21:35 CST

## Current Status

```text
Norman pilot:                COMPLETE_AND_FROZEN (commit d10d282; no recomputation)
Replogle Phase 2A data:      GEARS-compatible filtered essential-screen data
BNS:                         UNVERIFIED
RPE1 bounded smoke:          PASS (executable-chain evidence only, not performance)
R-L1-K562 full run:          COMPLETED
R-L1-RPE1 full run:          COMPLETED
RL1 postprocess:             COMPLETED
Norman/Replogle comparison:  COMPLETED
Cross-context gate:          CONDITIONAL_GO_RL4
```

## Completed Outputs

| Output | Status |
|---|---|
| `results/replogle/gears_rl1_summary.csv` | COMPLETE |
| `results/tables/norman_replogle_rl1_comparison.csv` | COMPLETE |
| `results/tables/metric_divergence_profile.csv` | COMPLETE |
| `results/tables/replogle_gears_vs_probes.csv` | COMPLETE |
| `figures/main/norman_replogle_metric_divergence.{pdf,svg,png}` | COMPLETE |
| `figures/main/replogle_gears_vs_probes.{pdf,svg,png}` | COMPLETE |
| `reports/PHASE2A_RL1_FULL_REPORT.md` | COMPLETE |
| `reports/PHASE2A_CROSS_CONTEXT_GATE.md` | COMPLETE |

## Full-Run Records

| Context | Run directory | Status | Test perturbations | Elapsed |
|---|---|---:|---:|---:|
| K562 | `results/replogle/gears/rl1_k562_20260824T074041Z/` | `COMPLETED_GEARS` | 216 | 50,939.4 s |
| RPE1 | `results/replogle/gears/rl1_rpe1_20260825T000548Z/` | `COMPLETED_GEARS` | 308 | 43,319.3 s |

K562 trained all 20 epochs and completed GEARS testing. The original export step hit the known `ctrl_adata=None` issue after training, so `scripts/recover_gears_replogle_rl1_export.py` recovered metrics from the trained checkpoint without retraining.

RPE1 trained all 20 epochs and exported directly. The final GEARS log reported validation overall MSE 0.0156, validation top-20 DE MSE 0.1191, and test top-20 DE MSE 0.1347.

## Core Results

| Context | Metric space | n targets | Pearson delta | Top-1 | Top-5 | MRR | UER@50 | Sign-flip |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| K562 | audit_delta | 216 | 0.2840 [0.2558, 0.3107] | 0.0139 | 0.0556 | 0.0497 [0.0332, 0.0689] | 0.1580 | 0.2691 |
| K562 | gears_raw | 216 | 0.9851 [0.9836, 0.9864] | 0.0139 | 0.0417 | 0.0445 [0.0290, 0.0624] | 0.0000 | 0.0000 |
| RPE1 | audit_delta | 308 | 0.4616 [0.4345, 0.4878] | 0.0097 | 0.0195 | 0.0262 [0.0166, 0.0385] | 0.0940 | 0.1720 |
| RPE1 | gears_raw | 308 | 0.9709 [0.9690, 0.9727] | 0.0000 | 0.0162 | 0.0209 [0.0158, 0.0263] | 0.0000 | 0.0000 |

## Interpretation

Both Replogle contexts support the pre-registered metric-divergence signal: global expression fit remains high in `gears_raw`, while perturbation-specific retrieval is weak. This externally reproduces the key Norman warning pattern under a filtered-data scope.

The audit-delta comparison is more conservative. GEARS does not dominate simple mean-effect baselines on Pearson in either K562 or RPE1, although retrieval is slightly better than the strongest baseline family. This supports `CONDITIONAL_GO_RL4`, not an unconditional claim that GEARS wins.

Within Replogle, K562 and RPE1 differ in audit-delta Pearson and UER@50 with non-overlapping bootstrap confidence intervals, while MRR confidence intervals overlap. Cross-context R-L4 should therefore be treated as a stress test of transfer behavior, not a formality.

## Gate Decision

```text
CONDITIONAL_GO_RL4
```

Proceed to R-L4 cross-context GEARS runs only under these labels:

- `data_scope = GEARS-compatible filtered essential-screen data`
- `BNS_STATUS = UNVERIFIED`
- `uer_null_status = sensitivity_only`
- no complete Figshare+ processed-object claim
- no replicate-derived BNS claim

## Next Tasks

1. Commit the completed R-L1 report package.
2. Launch R-L4-K2R and R-L4-R2K full GEARS runs using the same filtered-data configuration family.
3. Build R-L4 postprocess tables/figures and compare cross-context results against R-L1.
4. Keep complete-data replication blocked until official or paper-linked Figshare+ processed objects are accessible from the command line.

## Provenance Notes

- Complete Figshare+ processed Replogle objects and manifest downloads still returned HTTP 403 by command line on 2026-08-23. This blocks complete-data claims but does not block filtered-data GEARS-compatible auditing.
- No field in SRA runinfo or filtered h5ad `obs` is treated as a biological replicate. `batch`, `library`, `gemgroup`, `run`, and `SRA run` remain technical metadata only.
- Smoke/debug outputs remain executable-chain evidence only and are excluded from performance figures.
- Failed or interrupted run directories are retained as provenance and must not be mixed with completed full-run metrics.

