# Phase 2A Replogle Progress Report

Date: 2026-08-23

## Current Status

Phase 2A has advanced from source audit to a completed baseline-first audit on GEARS-compatible filtered Replogle essential-screen data.

```text
SOURCE_AUDIT_COMPLETE
SRA_RUNINFO_DOWNLOADED
GEARS_FILTERED_H5AD_DOWNLOADED
REPLICATE_AUDIT_COMPLETE
QC_COMPLETE_WITH_WARNINGS
TARGET_OVERLAP_COMPLETE
SPLIT_INTEGRITY_PASS
BASELINE_AND_FALSIFICATION_AUDIT_COMPLETE
PREMODEL_GATE_CONDITIONAL_GO_GEARS_FILTERED
GEARS_REPLOGLE_K562_SMOKE_COMPLETE_NOT_PERFORMANCE
GEARS_REPLOGLE_FULL_TRAINING_NOT_STARTED
```

Norman pilot was frozen before Replogle work at commit `d10d282` (`Freeze Norman pilot before Replogle Phase 2A`).

## Completed

1. Located official/paper-linked Replogle sources: Cell 2022 paper, GWPS browser, Figshare+ processed h5ad deposit, Figshare+ SRA/GEO manifest, Figshare+ MTX files, NCBI BioProject `PRJNA831566`, and GEARS/Dataverse filtered essential files.
2. Downloaded NCBI SRA runinfo to `data/raw/replogle/PRJNA831566_sra_runinfo.csv`.
3. Downloaded GEARS-compatible filtered essential h5ad archives:
   - K562: `data/raw/replogle/replogle_k562_essential.zip`
   - RPE1: `data/raw/replogle/replogle_rpe1_essential.zip`
4. Extracted filtered AnnData files:
   - K562: `data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad`
   - RPE1: `data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad`
5. Recorded checksums in `data/metadata/replogle_checksums.tsv`.
6. Generated source and replicate audits:
   - `reports/REPLOGLE_SOURCE_AUDIT.md`
   - `reports/replogle_replicate_label_audit.md`
   - `reports/replogle_replicate_label_audit.tsv`
7. Generated QC reports:
   - `reports/replogle_k562_qc.md`
   - `reports/replogle_rpe1_qc.md`
8. Generated target/gene vocabulary audits:
   - `results/tables/replogle_context_target_overlap.tsv`
   - `results/tables/replogle_gene_overlap.tsv`
   - `reports/replogle_gene_vocabulary_audit.md`
9. Materialized and audited R-L1/R-L4 splits:
   - `data/metadata/replogle_split_assignments.tsv`
   - `reports/replogle_split_integrity_report.md`
   - `reports/replogle_split_integrity_report.tsv`
10. Completed baseline and falsification audit:
   - `results/replogle/replogle_summary.csv`
   - `results/replogle/replogle_perturbation_retrieval.csv`
   - `reports/REPLOGLE_BASELINE_AUDIT.md`
11. Added reusable Replogle label normalization and split/check tests. Current test suite: 13 passed.
12. Completed a bounded GEARS K562 R-L1 smoke run:
   - `reports/REPLOGLE_GEARS_SMOKE_REPORT.md`
   - `results/replogle/gears/gears_replogle_k562_smoke_20260823T030844Z/metadata.json`

## Data Summary

| Dataset | Cells | Genes | Perturbations incl. ctrl | Perturbed targets | Controls | QC |
|---|---:|---:|---:|---:|---:|---|
| Replogle K562 GEARS-filtered essential | 162,751 | 5,000 | 1,093 | 1,092 | 10,691 | WARNING: min cells/target 15 |
| Replogle RPE1 GEARS-filtered essential | 162,733 | 5,000 | 1,544 | 1,543 | 11,485 | WARNING: min cells/target 13 |

Target overlap:

| Category | Targets |
|---|---:|
| Shared K562/RPE1 targets | 848 |
| K562-only targets | 244 |
| RPE1-only targets | 695 |
| Cross-context eligible targets, >=30 cells in both contexts | 737 |

## Baseline Audit Summary

| Split | Test targets |
|---|---:|
| R-L1-K562 | 218 |
| R-L1-RPE1 | 309 |
| R-L4-K2R | 737 |
| R-L4-R2K | 737 |

All 28 summary rows completed: 20 primary baseline rows and 8 falsification-probe rows. BNS remains `UNVERIFIED`.

Main observation: within-context mean-effect baselines reach moderate delta correlation, while cross-context mean-effect transfer is near zero delta correlation and very low retrieval. This supports using Replogle as a stricter external/context audit rather than treating high global expression similarity as sufficient evidence.

## Replicate Status

```text
REPLICATE_STATUS = NOT_AVAILABLE
BNS_STATUS = UNVERIFIED
```

SRA runinfo and filtered h5ad `obs` fields do not expose a validated biological replicate label. SRA fields are useful for provenance and raw sequencing structure, but not sufficient for BNS.

## Current Blockers

The complete Figshare+ processed h5ad and manifest endpoints still return HTTP 403 by command line. The executable Phase 2A audit therefore uses GEARS-compatible filtered essential-screen files, not the complete Figshare+ deposits.

Full GEARS Replogle model training has not started. It should proceed only under the `CONDITIONAL_GO_GEARS_FILTERED` gate and must keep the filtered-data/BNS-unverified caveat in every result table.

## Next Required Action

Optionally run an RPE1 bounded smoke for symmetry, then decide whether to launch full CPU/GPU filtered-data runs. If complete Figshare+ data become accessible later, repeat QC, split integrity, baselines, and gate on the complete objects before comparing model results.
