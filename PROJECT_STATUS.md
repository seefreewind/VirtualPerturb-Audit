# Phase 0-2 Status

## Completed

- Phase 2A Replogle audit started after freezing the Norman pilot at commit `d10d282`.
- Replogle official/paper-linked sources identified: Cell 2022 publication, GWPS browser, Figshare+ processed h5ad deposit, Figshare+ SRA/GEO manifest, Figshare+ MTX files, and NCBI SRA BioProject `PRJNA831566`.
- NCBI SRA runinfo downloaded to `data/raw/replogle/PRJNA831566_sra_runinfo.csv` with checksum recorded in `data/metadata/replogle_checksums.tsv`.
- Replogle source audit generated at `reports/REPLOGLE_SOURCE_AUDIT.md`.
- Replogle SRA-level replicate audit generated at `reports/replogle_replicate_label_audit.md` and `reports/replogle_replicate_label_audit.tsv`; current status is `REPLICATE_STATUS = NOT_AVAILABLE`, `BNS_STATUS = UNVERIFIED`.
- Replogle SRA runinfo parsed and summarized in `data/metadata/replogle_sra_runinfo_parsed.tsv` and `data/metadata/replogle_sra_runinfo_summary.tsv`.
- Replogle entries in `DATASET_PROVENANCE.md`, `data/metadata/dataset_registry.tsv`, and `analysis_lock.yaml` updated.
- Replogle perturbation-label normalization and R-L1/R-L4 split foundations added; test suite expanded to 13 passing tests.
- GEARS-compatible filtered Replogle essential h5ad archives downloaded from Harvard Dataverse/GEARS source entries, extracted, and checksum-registered.
- Replogle K562/RPE1 h5ad schema audit, QC reports, perturbation label map, gene vocabulary audit, target overlap, and cross-context eligibility tables completed.
- R-L1-K562, R-L1-RPE1, R-L4-K2R, and R-L4-R2K split materialization completed; split integrity report passes 14/14 checks.
- Replogle baseline-first audit completed for B0/B1/B2/B4/B5 and FP1/FP3 across all four splits, writing `results/replogle/replogle_summary.csv`, `results/replogle/replogle_perturbation_retrieval.csv`, and `reports/REPLOGLE_BASELINE_AUDIT.md`.
- Phase 2A premodel gate generated at `reports/PHASE2A_PREMODEL_GATE.md` with decision `CONDITIONAL_GO_GEARS_FILTERED`.
- Current overall progress report generated at `reports/CURRENT_OVERALL_STATUS_AND_PROGRESS.md`.
- Bounded GEARS Replogle K562 R-L1 smoke completed with 1 train batch, 1 eval batch, checkpoint/metadata export, and report `reports/REPLOGLE_GEARS_SMOKE_REPORT.md`. This is executable-chain evidence only, not performance.
- Repository scaffold created under `VirtualPerturb-Audit/`.
- Existing Git repository detected and reused.
- Environment audit started.
- Pre-data `analysis_lock.yaml` created.
- Literature, dataset, and model provenance registries initialized with source-linked entries.
- L0/L1/L2 split implementation and critical split tests added.
- Baseline, perturbation-specific, empirical-bound, and hallucination metric modules added.
- Unit tests passed on toy split/metric fixtures (`9 passed`).
- CLI blocked-run metadata behavior verified for missing Norman data.
- Isolated GEARS environment created at `environment/gears-venv`.
- `cell-gears==0.1.2` and `torch-geometric==2.6.1` installed in the isolated GEARS environment.
- GEARS import verified; first import takes about 35 seconds on this Mac.
- Corrected GEARS Norman official datafile URL to `https://dataverse.harvard.edu/api/access/datafile/6154020`.
- Norman GEARS-format AnnData downloaded from a public LUH Seafile mirror after official Dataverse command-line access returned WAF challenge.
- Norman local checksum recorded: `23ffb0fac6a847ff927cf7509d80d85052bfefbfb97610786a2dafaaefa0b6a0`.
- Real-data QC completed: 91,205 cells, 5,045 genes, 284 perturbations, 7,353 controls.
- L0/L1/L2 split integrity checks completed and passed; replicate/batch group overlap remains unverified because the processed file does not expose an informative replicate field.
- Baseline pilot completed for B0 no-change, B1 global perturbed mean, B2 context-matched perturbed mean, B3 additive seen-component, B4 PCA/Ridge, and B5 mean-effect baselines on L0/L1/L2.
- GEARS L1 batch smoke completed with official package training path, filtered GO tensor injection, strict JSON metadata, and model checkpoint written to `results/pilot/gears_20260812T152223Z/`.
- GEARS bounded smoke export path verified: per-perturbation metrics, delta centroids, retrieval/confusion rows, and runtime metadata are written for development-smoke runs.
- Full GEARS execution handoff created at `reports/GEARS_FULL_RUN_HANDOFF.md` with GPU/CPU commands and interpretation guardrails.
- Pilot summary now reports perturbation-level bootstrap 95% CIs where enough perturbation units are available; single-unit GEARS smoke rows are marked `INSUFFICIENT_UNITS`.
- FP-1 perturbation-blind mean-effect, FP-2 cell-state-blind additive, and FP-3 label-shuffled mean-effect pilot probes completed for L1/L2.
- Perturbation-centroid retrieval and identity-confusion rows are generated for baseline and falsification-probe pseudobulk outputs; zero-vector predictions are marked `UNINFORMATIVE_PREDICTION`.
- GEO cell-identity metadata link audit completed: 88,843/91,205 GEARS cells matched, unordered perturbation concordance 0.9916, and `gemgroup` provides a partial batch-like field for sensitivity/null-envelope work.
- Gemgroup-aware control-control null-envelope sensitivity completed for L1/L2 baselines and FP-1/FP-3 probes in `results/pilot/null_envelope_sensitivity.csv`.
- FP-3 label-shuffled pilot now runs the pre-registered 20 permutations and writes `results/pilot/fp3_label_shuffle_permutation_summary.csv`.
- Five-seed robustness summary completed for B0-B5 non-shuffled baselines and FP-1/FP-2 on L1/L2/L3 in `results/pilot/seed_robustness_summary.csv`.
- HGNC gene-group annotation completed for Norman perturbation genes, with family-aware retrieval-confusion summaries in `results/pilot/gene_family_confusion_summary.csv` and L3 gene-family holdout candidates in `results/pilot/l3_gene_family_holdout_candidates.csv`.
- Formal L3 HGNC gene-family holdout implemented and integrated into split integrity, baseline, falsification, FP3 permutation, null-envelope sensitivity, retrieval, and primary metric tables.
- Replicate-label audit completed in `reports/replicate_label_audit.md`; no true biological replicate label was found, and GEO `gemgroup` remains batch-like sensitivity metadata only.
- Norman acquisition report created at `reports/NORMAN_ACQUISITION_REPORT.md`.
- Full GEARS evaluations completed on this Mac CPU for L1, L2, and L3 (20 epochs, seed 1, `essential` perturbation graph), writing `gears_metrics.csv`, `gears_delta_centroids.pt`, `gears_perturbation_retrieval.csv`, and strict `metadata.json` per run:
  - `results/pilot/gears_20260822T065552Z/` (L1, 55 test perturbations, 18,284 s)
  - `results/pilot/gears_20260822T122126Z/` (L2, 40 test perturbations, 17,987 s)
  - `results/pilot/gears_20260822T172146Z/` (L3, 25 test perturbations, 21,057 s)
- A first L2 attempt failed with `BrokenPipeError` after 825 s and is preserved as `results/pilot/gears_20260822T120129Z/` with explicit `FAILED_GEARS` status; the rerun completed.
- Gemgroup-aware null-envelope sensitivity extended with `COMPLETED_GEARS_EVALUATION` rows for L1/L2/L3 in `results/pilot/null_envelope_sensitivity.csv` and table 6.
- Figure and table outputs rebuilt with GEARS full rows; smoke rows are excluded from performance figures; `pytest` passes 10/10.
- Added `reports/FINAL_PILOT_RESULT_REPORT.md` summarizing the executed GEARS full evaluation and rebuilt downstream outputs.

## Key results

Norman baseline and falsification-probe audit outputs are available in `results/pilot/pilot_summary.csv`. B3/FP-2 shows how much signal can be recovered from perturbation identity and seen single-component deltas without individual cell-state modeling. B4 PCA/Ridge is now included as a perturbation-to-effect mapping baseline. B1/B2 match B5 in this pilot when no stronger biological context is available beyond the current metadata. HGNC family-confusion outputs show whether retrieval mistakes remain within related gene groups, and L3 now tests gene-family holdout behavior directly. Completed GEARS full rows (L1/L2/L3) show delta-Pearson 0.9887/0.9838/0.9843 with perturbation-level bootstrap CIs, UER@50 and sign-flip rate at 0 under the provisional threshold, and retrieval top-1 accuracy 0.20/0.075/0.08 and MRR 0.328/0.147/0.207. The retrieval collapse under stricter holdouts with stable correlation is the key shortcut/leakage signal from the GEARS pilot rows. All GEARS rows keep `bns_status: UNVERIFIED` because replicate/control null envelopes are not yet verified; the gemgroup null-envelope sensitivity (UER 0.172/0.262/0.235 for L1/L2/L3) is a batch-like sensitivity check only.

## Failed

- Figshare+ command-line article/API downloads for complete Replogle processed h5ad and manifest endpoints returned HTTP 403 on 2026-08-23. This blocks complete-data claims, but GEARS-compatible filtered essential h5ad files are now local and audited.
- `python` executable is missing; `python3` is available.
- The GEARS Dataverse datafile endpoint returned an AWS WAF challenge to a command-line HEAD request.
- The default GEARS GO graph tarball endpoint also returned an unusable WAF/empty-file response; the current runs use a documented filtered GO tensor generated from local GEARS prior files.
- `pertpy` is unavailable in the current environment.
- A second L2 full-run attempt failed with `BrokenPipeError` (stdout pipe interruption) after 825 s; a subsequent foreground rerun completed successfully. The failure is documented in `results/pilot/gears_20260822T120129Z/` and must not be mistaken for a completed result.

## Risks

- Replogle Phase 2A can proceed to GEARS smoke/full runs only under the `CONDITIONAL_GO_GEARS_FILTERED` gate. The current executable dataset is GEARS-compatible filtered essential-screen data, not the complete Figshare+ processed object.
- Replogle SRA runinfo exposes technical library/lane/run metadata but no validated biological replicate field; BNS remains `UNVERIFIED` at the current audit stage.
- Replogle filtered h5ad `obs` also lacks biological replicate, batch, and guide-level fields; BNS remains `UNVERIFIED`.
- Replogle K562/RPE1 QC is WARNING because some perturbations have fewer than 30 cells.
- GEARS/PyG dependencies require the isolated `environment/gears-venv` environment on this Mac.
- GEARS processed Norman data are convenient for pilot but still require preprocessing provenance scrutiny.
- True replicate fields remain missing; GEO-linked `gemgroup` is available for 97.4% of cells as a batch-like sensitivity field, but it is not a full replicate label. All BNS values remain `UNVERIFIED`.
- GEARS full training is expensive on CPU (about 5-6 hours per split on this Mac) and terminal-lifetime sensitive; background pipe failures are a known risk.
- GEARS evaluation uses a GEARS-internal condition vocabulary whose test set composition overlaps but does not exactly match the audit splitter's test sets (e.g., `ctrl+X` vs `X+ctrl` orderings); metrics are computed inside the GEARS-run vocabulary.

## Scientific interpretation

GEARS rows marked `COMPLETED_GEARS_EVALUATION` are eligible for model-pilot interpretation inside the GEARS-run vocabulary, always alongside `bns_status: UNVERIFIED`. Bounded smoke rows verify software integration only; baseline and falsification metrics are descriptive audit checks. The dissociation between stable delta-Pearson (≈0.98 across splits) and collapsing retrieval (0.20/0.075/0.08 top-1) is the main shortcut/leakage signal to carry into the manuscript.

## Files generated

See `CHANGELOG.md`. Key generated outputs include `environment/environment_report.md`, `environment/gears_pip_freeze.txt`, real-data QC/split reports, baseline pilot outputs with uncertainty columns, pilot figures, provenance registries, and the GEARS batch-smoke checkpoint metadata.

## GO / NO-GO

Pilot status: PROVISIONAL_GO_FOR_BASELINE_AUDIT; GEARS_FULL_EVALUATION_COMPLETED_PILOT (BNS unverified). Replogle Phase 2A status: `CONDITIONAL_GO_GEARS_FILTERED`; K562 bounded smoke complete; full runs allowed only on filtered essential data with BNS unverified.

## Next 3 actions

1. Optionally run an RPE1 bounded GEARS Replogle smoke test to mirror the completed K562 smoke.
2. If smoke coverage is sufficient, launch full GEARS filtered-data evaluations for R-L1-K562, R-L1-RPE1, R-L4-K2R, and R-L4-R2K.
3. Rebuild downstream tables/figures with Replogle filtered-data rows and keep every result marked `BNS_STATUS = UNVERIFIED`.
