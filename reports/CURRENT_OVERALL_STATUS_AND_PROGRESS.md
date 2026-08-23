# Current Overall Status and Progress

Date: 2026-08-23

## Executive Status

The Norman pilot is frozen and complete. Replogle Phase 2A has completed the audit-first premodel gate on GEARS-compatible filtered essential-screen data.

Current decision:

```text
Norman pilot: COMPLETE_AND_FROZEN
Replogle Phase 2A: CONDITIONAL_GO_GEARS_FILTERED
BNS status: UNVERIFIED for Norman and Replogle
Next work: optional RPE1 smoke, then possible full filtered-data runs
```

## Norman Pilot

Completed:

- Real-data QC, split integrity, baseline/falsification probes, retrieval outputs, null-envelope sensitivity, seed robustness, HGNC family L3, and figures/tables.
- Full GEARS evaluations on this Mac CPU for L1, L2, and L3.
- Final report: `reports/FINAL_PILOT_RESULT_REPORT.md`.
- Freeze commit: `d10d282` (`Freeze Norman pilot before Replogle Phase 2A`).

Main result:

GEARS kept high delta-Pearson across stricter holdouts but retrieval top-1 collapsed under L1/L2/L3. This remains the strongest shortcut/leakage-audit signal from the pilot.

## Replogle Phase 2A

Completed:

- Source audit, SRA metadata download, checksum registry, replicate audit.
- GEARS-filtered K562/RPE1 essential h5ad download and extraction.
- h5ad schema audit, QC, gene vocabulary audit, target overlap, cross-context eligibility.
- R-L1-K562, R-L1-RPE1, R-L4-K2R, and R-L4-R2K split materialization.
- Split integrity report: PASS.
- Baseline and falsification audit: completed for 28 summary rows.
- Premodel gate: `CONDITIONAL_GO_GEARS_FILTERED`.
- GEARS bounded K562 R-L1 smoke: completed as executable-chain evidence, not performance.

Key Replogle numbers:

| Item | K562 | RPE1 |
|---|---:|---:|
| Cells | 162,751 | 162,733 |
| Genes | 5,000 | 5,000 |
| Perturbed targets | 1,092 | 1,543 |
| Controls | 10,691 | 11,485 |
| QC status | WARNING | WARNING |

Cross-context:

- Shared targets: 848.
- Eligible R-L4 targets with >=30 cells in both contexts: 737.
- Split integrity checks: 14/14 PASS.

## Current Caveats

- Complete Figshare+ processed Replogle objects and manifests still return HTTP 403 via command-line access.
- The current Replogle audit uses GEARS-compatible filtered essential-screen data, not the complete Figshare+ data.
- No biological replicate label is available in SRA runinfo or filtered h5ad `obs`; BNS remains `UNVERIFIED`.
- K562 and RPE1 QC are WARNING because at least one perturbation has fewer than 30 cells.

## Current Deliverables

- `reports/PHASE2A_REPLOGLE_PROGRESS.md`
- `reports/PHASE2A_PREMODEL_GATE.md`
- `reports/GEARS_REPLOGLE_COMPATIBILITY.md`
- `reports/REPLOGLE_GEARS_SMOKE_REPORT.md`
- `reports/REPLOGLE_BASELINE_AUDIT.md`
- `reports/replogle_split_integrity_report.md`
- `reports/replogle_k562_qc.md`
- `reports/replogle_rpe1_qc.md`
- `reports/replogle_gene_vocabulary_audit.md`
- `results/replogle/replogle_summary.csv`
- `results/replogle/replogle_perturbation_retrieval.csv`
- `data/metadata/replogle_checksums.tsv`
- `data/metadata/replogle_split_assignments.tsv`

## Next Tasks

1. Optionally run a bounded RPE1 GEARS Replogle smoke test to mirror the completed K562 smoke.
2. If smoke coverage is sufficient, run full GEARS Replogle filtered-data evaluations for R-L1 and R-L4 under the conditional gate.
3. Rebuild downstream tables/figures with Replogle rows clearly labeled as filtered-data and BNS-unverified.
4. If complete Figshare+ data become accessible, repeat the Replogle audit chain on the complete objects before making complete-data claims.
