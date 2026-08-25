# Current Overall Status and Progress

Date: 2026-08-25

## Executive Status

The Norman pilot is frozen and complete. Replogle Phase 2A has completed the within-context R-L1 GEARS audit for K562 and RPE1 on GEARS-compatible filtered essential-screen data.

Current decision:

```text
Norman pilot: COMPLETE_AND_FROZEN
Replogle Phase 2A R-L1: COMPLETED_FILTERED_DATA_RL1
Cross-context gate: CONDITIONAL_GO_RL4
BNS status: UNVERIFIED for Norman and Replogle
Next work: R-L4-K2R and R-L4-R2K full GEARS runs
```

## Norman Pilot

Completed:

- Real-data QC, split integrity, baseline/falsification probes, retrieval outputs, null-envelope sensitivity, seed robustness, HGNC family L3, and figures/tables.
- Full GEARS evaluations on this Mac CPU for L1, L2, and L3.
- Final report: `reports/FINAL_PILOT_RESULT_REPORT.md`.
- Freeze commit: `d10d282` (`Freeze Norman pilot before Replogle Phase 2A`).

Main result:

GEARS kept high delta-Pearson across stricter holdouts but retrieval top-1 collapsed under L1/L2/L3. This remains the strongest shortcut/leakage-audit signal from the Norman pilot.

## Replogle Phase 2A

Completed:

- Source audit, SRA metadata download, checksum registry, replicate audit.
- GEARS-filtered K562/RPE1 essential h5ad download and extraction.
- h5ad schema audit, QC, gene vocabulary audit, target overlap, cross-context eligibility.
- R-L1-K562, R-L1-RPE1, R-L4-K2R, and R-L4-R2K split materialization.
- Split integrity report: PASS.
- Baseline and falsification audit: completed for B0/B1/B2/B4/B5 and FP1/FP3.
- Premodel gate: `CONDITIONAL_GO_GEARS_FILTERED`.
- GEARS bounded K562 and RPE1 R-L1 smoke tests: executable-chain evidence only, not performance.
- R-L1-K562 full GEARS run: `COMPLETED_GEARS`, 216 evaluated test perturbations.
- R-L1-RPE1 full GEARS run: `COMPLETED_GEARS`, 308 evaluated test perturbations.
- R-L1 postprocess tables and figures completed.
- R-L1 full report and cross-context gate completed.

Key R-L1 results:

| Context | Metric space | Pearson delta | Top-1 | Top-5 | MRR | UER@50 |
|---|---|---:|---:|---:|---:|---:|
| K562 | gears_raw | 0.9851 [0.9836, 0.9864] | 0.0139 | 0.0417 | 0.0445 [0.0290, 0.0624] | 0.0000 |
| RPE1 | gears_raw | 0.9709 [0.9690, 0.9727] | 0.0000 | 0.0162 | 0.0209 [0.0158, 0.0263] | 0.0000 |
| K562 | audit_delta | 0.2840 [0.2558, 0.3107] | 0.0139 | 0.0556 | 0.0497 [0.0332, 0.0689] | 0.1580 |
| RPE1 | audit_delta | 0.4616 [0.4345, 0.4878] | 0.0097 | 0.0195 | 0.0262 [0.0166, 0.0385] | 0.0940 |

Interpretation:

Replogle externally reproduces the metric-divergence pattern under filtered-data scope: global `gears_raw` fit remains high, while perturbation-specific retrieval is weak. The audit-delta baseline comparison is conservative and does not support an unconditional GEARS-wins claim. The correct downstream decision is `CONDITIONAL_GO_RL4`.

## Current Caveats

- Complete Figshare+ processed Replogle objects and manifests still return HTTP 403 via command-line access.
- The current Replogle audit uses GEARS-compatible filtered essential-screen data, not the complete Figshare+ data.
- No biological replicate label is available in SRA runinfo or filtered h5ad `obs`; BNS remains `UNVERIFIED`.
- UER uses a per-perturbation median absolute audit-delta null and remains `sensitivity_only`.
- K562 and RPE1 QC are WARNING because at least one perturbation has fewer than 30 cells.

## Current Deliverables

- `reports/PHASE2A_RL1_PROGRESS.md`
- `reports/PHASE2A_RL1_FULL_REPORT.md`
- `reports/PHASE2A_CROSS_CONTEXT_GATE.md`
- `reports/PHASE2A_PREMODEL_GATE.md`
- `reports/GEARS_REPLOGLE_COMPATIBILITY.md`
- `reports/REPLOGLE_GEARS_SMOKE_REPORT.md`
- `reports/REPLOGLE_RPE1_SMOKE_REPORT.md`
- `reports/REPLOGLE_BASELINE_AUDIT.md`
- `results/replogle/gears_rl1_summary.csv`
- `results/tables/norman_replogle_rl1_comparison.csv`
- `results/tables/metric_divergence_profile.csv`
- `results/tables/replogle_gears_vs_probes.csv`
- `figures/main/norman_replogle_metric_divergence.{pdf,svg,png}`
- `figures/main/replogle_gears_vs_probes.{pdf,svg,png}`

## Next Tasks

1. Commit the completed R-L1 package.
2. Launch R-L4-K2R and R-L4-R2K full GEARS runs under the filtered-data conditional gate.
3. Rebuild R-L4 downstream tables/figures and compare cross-context results against R-L1.
4. If complete Figshare+ data become accessible, repeat the Replogle audit chain on the complete objects before making complete-data claims.

