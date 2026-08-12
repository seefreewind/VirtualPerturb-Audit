# Changelog

## 2026-08-12

- Created project scaffold.
- Added pre-data analysis lock.
- Added dataset and model provenance registries.
- Implemented L0/L1/L2 split builders and integrity checks.
- Implemented baseline adapters and core pilot metrics.
- Implemented UER@K and Sign Flip Rate.
- Added CLI entry point, Norman acquisition script, table and figure builders, and tests.
- Created isolated GEARS environment and verified package import after adding PyG.
- Corrected Norman GEARS processed data URL and started mirror-based acquisition because Dataverse command-line access is WAF-challenged.
- Added real-data audit and baseline pilot scripts.
- Completed Norman mirror acquisition, checksum, schema audit, and split integrity checks.
- Completed baseline-only pilot for B0 no-change and B5 mean-effect baselines.
- Added GEARS L1 batch-smoke runner with custom split export from GEARS-filtered AnnData, filtered GO tensor injection for non-default perturbation graphs, bounded training batches, model checkpoint save, and failure traceback metadata.
- Added perturbation-level bootstrap CI columns to pilot summaries and strict JSON sanitization for GEARS run metadata.
- Added FP-1 perturbation-blind and FP-3 label-shuffled falsification probe pilot outputs for L1/L2.
- Added perturbation-centroid retrieval and identity-confusion export for baseline and falsification-probe pilot rows.
- Added Norman GEO cell-identity metadata link audit with `gemgroup` batch-like coverage and condition concordance checks.
- Added gemgroup-aware control-control null-envelope sensitivity table for baseline and falsification-probe pilot rows.
- Added pre-registered 20-permutation FP-3 label-shuffle pilot summary.
