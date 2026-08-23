# Phase 2A Premodel Gate

Date: 2026-08-23

## Decision

```text
CONDITIONAL_GO_GEARS_FILTERED
```

GEARS Replogle training may proceed only on the locally downloaded GEARS-compatible filtered essential-screen datasets, with explicit reporting that these are not the complete Figshare+ processed objects and that BNS is unavailable.

## Gate Checks

| Check | Status | Evidence |
|---|---|---|
| Source provenance | PASS_WITH_SCOPE_LIMIT | Official Replogle paper-linked sources identified; NCBI BioProject runinfo downloaded; GEARS/Dataverse filtered essential files downloaded. Complete Figshare+ command-line access remains HTTP 403. |
| Local checksums | PASS | `data/metadata/replogle_checksums.tsv` records SRA runinfo, filtered zip files, and extracted h5ad SHA256 values. |
| Metadata schema | PASS_WITH_LIMIT | Filtered h5ad files expose `condition`, `cell_type`, `control`, and `gene_name`; guide, batch, and replicate fields are absent. |
| Replicate audit | FAIL_FOR_BNS_ONLY | No validated biological replicate label found in SRA runinfo or filtered h5ad `obs`; BNS must remain `UNVERIFIED`. |
| QC | WARNING | Both contexts have >160k cells and 5,000 genes, but some targets have <30 cells. |
| Target overlap | PASS | 848 shared targets; 737 cross-context eligible targets with >=30 cells in both contexts. |
| Gene vocabulary | PASS_WITH_SCOPE_LIMIT | Both filtered files expose GEARS-supported 5,000-gene vocabularies; K562 has one duplicated gene symbol. |
| Split integrity | PASS | R-L1-K562, R-L1-RPE1, R-L4-K2R, and R-L4-R2K integrity checks pass. |
| Baseline audit | PASS | B0/B1/B2/B4/B5 and FP1/FP3 completed for all four splits. |
| Falsification probes | PARTIAL_PASS | FP1 and FP3 completed. FP2/B3-style cell-state/combinatorial probes are not applicable to these single-gene essential-screen files. |
| Model training readiness | CONDITIONAL_PASS | GEARS supports these filtered dataset names; full model runs should be labeled filtered-data exploratory/external audit. |

## Required Reporting Constraints

- Use dataset label `Replogle_GEARS_filtered`.
- Mark every model result with `bns_status = UNVERIFIED`.
- Do not claim complete Replogle genome-scale coverage.
- Do not compare filtered-data GEARS results against a complete Figshare+ object as if the source scope were identical.
- Preserve R-L1 and R-L4 split hashes from `reports/replogle_split_integrity_report.md`.
- Report QC warnings for low-count targets in K562 and RPE1.

## Immediate Next Step

Run GEARS compatibility smoke on one Replogle filtered essential dataset before any full training launch.
