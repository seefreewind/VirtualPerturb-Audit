# Changelog

## 2026-08-23 (Phase 2A-RL1)

- Fixed custom-split vocabulary mismatch in `scripts/run_gears_replogle_smoke.py` (RPE1 smoke `KeyError: 'AC118549.1+ctrl'`). Original behavior: split dict built from raw `obs.condition`; GEARS `PertData.load` drops cells whose condition is not in the perturbation graph (GO gene set), leaving stale dict entries that crash `get_dataloader`. Modified behavior: after `PertData.load`, the split dict is rebuilt from `pert_data.adata.obs` (GEARS-filtered vocabulary) with the same frozen per-cell assignment; a `_gears_vocabulary.tsv` sidecar records final condition counts. Reason: mirror the frozen Norman custom-split convention (`write_gears_custom_split(adata=pert_data.adata)`); official GEARS package stays unmodified. Fairness impact: GEARS test vocabulary may be smaller than audit vocabulary (targets without GO genes are not evaluable); both counts are recorded.
- Verified frozen R-L1 split reproducibility on full data: `scripts/verify_replogle_rl1_split.py` recomputes combined-context labels and reproduces frozen split hashes `e9fcaf7afdb972e4` (R-L1-K562) and `288d45dbeb512ce5` (R-L1-RPE1) exactly; counts match (`results/replogle/rl1_split_reproducibility.csv`).
- Added frozen RL1 full-run configs `configs/replogle/gears_rl1_k562_seed1.yaml` and `configs/replogle/gears_rl1_rpe1_seed1.yaml` mirroring the frozen Norman GEARS pilot (20 epochs, seed 1, batch 16, Adam 1e-3 / 5e-4, hidden 64, essential perturbation graph, filtered GO tensor).
- Added `reports/PHASE2A_RL1_CONFIG_DEVIATIONS.md` documenting the only deviations vs the Norman pilot (split-dict vocabulary rebuild; 200->2000 bootstrap resamples; dual metric spaces `gears_raw` and `audit_delta`) with rationale and comparability impact.
- Added `scripts/run_gears_replogle_rl1.py`: full R-L1 GEARS runs on Replogle filtered data with official `GEARS.train()` untouched, captured training telemetry to `training_log.csv`, dual-space metrics (Norman-comparable `gears_raw`; baseline-comparable `audit_delta`), perturbation-level bootstrap 95% CIs (2000 resamples), strict `metadata.json` with filtered-data/BNS-unverified flags.
- Added `scripts/build_gears_rl1_analysis.py`: builds `results/replogle/gears_rl1_summary.csv`, `results/tables/norman_replogle_rl1_comparison.csv`, `results/tables/metric_divergence_profile.csv`, and main figures `figures/main/norman_replogle_metric_divergence.*` and `figures/main/replogle_gears_vs_probes.*`.
- Fixed full-run co-expression path resolution: `PertData` root now points at `data/raw/replogle` (dataset folder parent) so GEARS writes the co-expression network inside the dataset folder (`gene2go_all.pkl` mirrored there); previously GEARS resolved `<root>/<dataset_name>` to a non-existent nested path and crashed with `OSError` writing the co-expression CSV.
- Fixed Replogle GO-graph density blow-up: the injected filtered GO tensor contained ~12.1M edges for the 9,853-gene Replogle essential node map (~90x denser than the frozen Norman pilot's 133,961 edges), making a 20-epoch CPU run infeasible (~3 s/step, heavy swap). `run_gears_replogle_rl1.py` now applies official-style top-k=20 per-target trimming (`get_similarity_network` convention), restoring Norman-comparable compute (~0.25 s/step) while keeping the identical 9,853 perturbation node set. Original/dismissed/impact documented in `reports/PHASE2A_RL1_CONFIG_DEVIATIONS.md` item 4.

## 2026-08-23

- Froze the completed Norman pilot before Replogle Phase 2A at commit `d10d282`.
- Started Replogle Phase 2A audit-first workflow: located official/paper-linked Replogle sources, downloaded NCBI SRA BioProject `PRJNA831566` runinfo, and recorded checksum/provenance.
- Added `reports/REPLOGLE_SOURCE_AUDIT.md`, `reports/replogle_replicate_label_audit.md`, `reports/replogle_replicate_label_audit.tsv`, and `reports/PHASE2A_REPLOGLE_PROGRESS.md`.
- Added Replogle SRA parsed metadata and summaries in `data/metadata/replogle_sra_runinfo_parsed.tsv` and `data/metadata/replogle_sra_runinfo_summary.tsv`.
- Registered Phase 2A in `analysis_lock.yaml`, updated Replogle entries in `DATASET_PROVENANCE.md` and `data/metadata/dataset_registry.tsv`, and recorded current Replogle BNS status as `UNVERIFIED`.
- Added reusable perturbation-label canonicalization plus R-L1/R-L4 split foundations and cross-context integrity tests; test suite now passes 13/13.
- Recorded complete-data blocker: command-line Figshare+ access to complete processed Replogle h5ad/manifest endpoints returned HTTP 403, so complete-data claims remain blocked.
- Downloaded GEARS-compatible filtered Replogle essential-screen files from Harvard Dataverse/GEARS source entries, extracted K562/RPE1 `perturb_processed.h5ad`, and recorded zip/h5ad checksums.
- Completed Replogle filtered-data h5ad QC, target overlap, gene vocabulary audit, split materialization, and split integrity checks for R-L1-K562, R-L1-RPE1, R-L4-K2R, and R-L4-R2K.
- Completed Replogle filtered-data baseline/falsification audit for B0/B1/B2/B4/B5 and FP1/FP3, writing `reports/REPLOGLE_BASELINE_AUDIT.md`, `results/replogle/replogle_summary.csv`, and `results/replogle/replogle_perturbation_retrieval.csv`.
- Added `reports/PHASE2A_PREMODEL_GATE.md`, `reports/GEARS_REPLOGLE_COMPATIBILITY.md`, and `reports/CURRENT_OVERALL_STATUS_AND_PROGRESS.md`; current gate is `CONDITIONAL_GO_GEARS_FILTERED` with BNS `UNVERIFIED`.
- Added `scripts/run_gears_replogle_smoke.py` and completed bounded GEARS Replogle K562 R-L1 smoke run `results/replogle/gears/gears_replogle_k562_smoke_20260823T030844Z/`; earlier failed smoke attempts are preserved with explicit metadata.
- Completed full GEARS evaluations on this Mac CPU for L1, L2, and L3 (20 epochs, seed 1, `essential` perturbation graph), with per-run `gears_metrics.csv`, `gears_delta_centroids.pt`, `gears_perturbation_retrieval.csv`, and strict `metadata.json`:
  - L1: `results/pilot/gears_20260822T065552Z/` (55 test perturbations, 18,284 s)
  - L2: `results/pilot/gears_20260822T122126Z/` (40 test perturbations, 17,987 s)
  - L3: `results/pilot/gears_20260822T172146Z/` (25 test perturbations, 21,057 s)
- Preserved the failed first L2 attempt as explicit provenance: `results/pilot/gears_20260822T120129Z/` has `status: FAILED_GEARS` with `BrokenPipeError` traceback.
- Extended gemgroup-aware control-control null-envelope sensitivity (`scripts/run_null_envelope_sensitivity.py`) to completed GEARS rows by canonicalizing condition names and converting GEARS raw predictions to audit-delta space; GEARS rows now appear in `results/pilot/null_envelope_sensitivity.csv` and table 6.
- Rebuilt tables and figures (`scripts/build_tables.py`, `scripts/build_figures.py`): table 2 GEARS status updated to full evaluation, GEARS full rows in table 5, smoke rows excluded from performance figures.
- Updated `reports/PILOT_DECISION.md`, `PROJECT_STATUS.md`, `NEXT_ACTIONS.md`, and this changelog to reflect the completed GEARS full runs while keeping BNS `UNVERIFIED`.
- Added `reports/FINAL_PILOT_RESULT_REPORT.md`.

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
- Added B3 additive seen-component baseline and FP-2 cell-state-blind additive probe.

## 2026-08-14

- Integrated B1 global perturbed mean, B2 context-matched perturbed mean, and B4 PCA/Ridge into the Norman baseline pilot outputs.
- Added five-seed robustness outputs for B0-B5 non-shuffled baselines and FP-1/FP-2.
- Added table 8 exports for seed robustness summaries.
- Added HGNC gene-group mapping for Norman perturbation genes, family-aware retrieval-confusion summaries, and L3 gene-family holdout candidate tables.
- Implemented formal L3 HGNC gene-family holdout and integrated it into split integrity, baseline, falsification, FP3 permutation, null-envelope sensitivity, retrieval, and primary metric outputs.
- Extended five-seed robustness summaries to L3.
- Added a replicate-label audit report documenting that no verified biological replicate field is available in the local GEARS AnnData or GEO identities file.
- Added GEARS bounded-smoke export for delta centroids and perturbation retrieval/confusion rows, and verified it with a one-batch CPU smoke run.
- Added runtime and evaluated-perturbation metadata to GEARS bounded-smoke runs and verified a 5-train-batch/3-eval-batch CPU smoke.
- Added `scripts/run_gears_full_audit.sh` and `reports/GEARS_FULL_RUN_HANDOFF.md` for GPU/CPU full-run handoff.
