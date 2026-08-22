# Pilot Decision

## Completed

- Project scaffold and pilot code infrastructure are in place.
- Split, leakage, baseline, expression metric, BNS, UER@K, and Sign Flip Rate implementations have unit tests.
- Current unit test status: PASS on toy fixtures.
- Missing-data CLI behavior: PASS; blocked metadata is written and the run fails loudly.
- GEARS package import is verified in `environment/gears-venv` after installing `cell-gears==0.1.2` and `torch-geometric==2.6.1`.
- Norman GEARS-format data have been downloaded from the LUH Seafile mirror, checksumed, and audited locally.
- Real-data QC and L0/L1/L2 split integrity reports pass, with replicate/batch overlap marked unverified because no informative replicate field is present.
- Baseline pilot has completed for B0 no-change, B1 global perturbed mean, B2 context-matched perturbed mean, B3 additive seen-component, B4 PCA/Ridge, and B5 mean-effect baselines.
- GEARS L1 batch-smoke training completed with the official `cell-gears==0.1.2` package and wrote a checkpoint plus strict JSON metadata to `results/pilot/gears_20260812T152223Z/`.
- GEARS bounded smoke export now writes per-perturbation metrics, delta centroids, retrieval/confusion rows, and runtime metadata for software-integration checks.
- Full GEARS execution handoff is available at `reports/GEARS_FULL_RUN_HANDOFF.md`.
- Baseline rows include perturbation-level bootstrap 95% CIs; the bounded GEARS smoke row is marked `INSUFFICIENT_UNITS` because it evaluated only one perturbation.
- FP-1 perturbation-blind, FP-2 cell-state-blind additive, and FP-3 label-shuffled pilot probes have completed for L1/L2.
- Perturbation-centroid retrieval and identity-confusion outputs are generated at `results/pilot/perturbation_retrieval.csv`.
- GEO metadata link audit provides `gemgroup` for 97.4% of GEARS cells, with unordered perturbation concordance 0.9916 among matched cells.
- Gemgroup-aware control-control null-envelope sensitivity is available in `results/pilot/null_envelope_sensitivity.csv`.
- FP-3 label-shuffled pilot has completed the pre-registered 20 permutations for L1/L2.
- Five-seed robustness has completed for B0-B5 non-shuffled baselines and FP-1/FP-2 on L1/L2/L3.
- HGNC gene-group annotation has completed for Norman perturbation genes; family-aware confusion summaries and L3 candidate gene groups are available.
- Formal L3 HGNC gene-family holdout has completed split integrity and baseline/falsification pilot integration.
- Replicate-label audit found no verified biological replicate field; GEO `gemgroup` remains batch-like sensitivity metadata only.
- Full GEARS evaluations completed on this Mac CPU for L1, L2, and L3 (20 epochs each, seed 1, `essential` perturbation graph). Run folders:
  - `results/pilot/gears_20260822T065552Z/` (L1, 55 test perturbations, elapsed 18,284 s)
  - `results/pilot/gears_20260822T122126Z/` (L2, 40 test perturbations, elapsed 17,987 s)
  - `results/pilot/gears_20260822T172146Z/` (L3, 25 test perturbations, elapsed 21,057 s)
- Gemgroup-aware null-envelope sensitivity extended to completed GEARS rows for L1/L2/L3 in `results/pilot/null_envelope_sensitivity.csv` and table 6.
- Figure and table outputs rebuilt with GEARS full rows and smoke rows excluded from performance figures; `pytest` passes (10/10).

## Key results

Baseline and falsification-probe Norman pilot results are present in `results/pilot/pilot_summary.csv`. B3/FP-2 remains a strong shortcut signal under L1, while B4 PCA/Ridge adds a perturbation-to-effect mapping baseline for separating expression correlation from retrieval specificity. HGNC family-confusion summaries now distinguish exact retrieval mistakes from biologically related gene-group mistakes, and L3 directly evaluates held-out gene-family behavior. GEARS full rows (L1/L2/L3, marked `COMPLETED_GEARS_EVALUATION`) are now available: delta-Pearson 0.9887/0.9838/0.9843 with narrow perturbation-level bootstrap CIs, sign-flip rate 0.0 and UER@50 0.0 under the provisional threshold, and retrieval top-1 accuracy 0.20/0.075/0.08. The sharp drop in perturbation retrieval from L1 to L2/L3 is consistent with the audit hypothesis that component-level shortcuts help exact-condition retrieval, and it is the key signal to investigate in the manuscript. Per the guardrails, these rows are model-pilot results with `bns_status: UNVERIFIED` because no true replicate upper bound exists; the gemgroup null-envelope sensitivity (UER 0.17-0.26 across splits) is reported separately as a batch-like sensitivity check, not as a replicate-derived BNS.

## Failed

- First GEARS L1 smoke run created official PyG cell graphs but failed because custom splits included perturbations filtered out by the GEARS GO graph. The runner was updated to export custom splits from GEARS-filtered AnnData.
- GEARS dynamic perturbation graph construction completed but training failed with perturbation-index mismatch against cached cell graphs. The runner now defaults to the official `gene_set_path` route using `essential_all_data_pert_genes.pkl`.
- GEARS `essential` perturbation graph initialization initially failed because the cached dynamic GO CSV contained genes outside the current perturbation node map. The runner now injects a filtered GO tensor for non-default graph modes and records the filtered edge/node counts.
- An initial L2 full run on 2026-08-22 failed after 825 s with `BrokenPipeError` (stdout pipe interruption during GEARS progress printing). This was a run-management failure, not a model/data failure; the rerun completed. Provenance: `results/pilot/gears_20260822T120129Z/` (status `FAILED_GEARS`).
- Official GEARS/Dataverse Norman endpoint returned an AWS WAF challenge to a non-interactive `curl` probe on 2026-08-12.
- `pertpy` is not installed in the current main environment, so it was not used as an alternate data loader.

## Risks

- BNS upper bounds remain unverified for all rows; no true replicate label exists. Do not report replicate-derived uncertainty for GEARS rows.
- GEARS L1/L2/L3 cells were evaluated on a GEARS-internal condition vocabulary whose test set composition overlaps but does not exactly match the audit splitter's test set (e.g., L1: 55 GEARS test perturbations vs 57 audit-split test perturbations, differing in `ctrl+X`/`X+ctrl` ordering). Metrics are computed inside the GEARS-run vocabulary; cross-split comparisons should treat vocabulary orderings carefully.
- CPU runs are long (about 5-6 hours each) and terminal-lifetime sensitive; background pipe failures are a known risk on this setup.
- Any GEARS dependency workaround must be documented as a model-adapter change if it alters official behavior.
- Current UER@50 uses a provisional empirical threshold; replicate/control null envelopes remain unverified. GEO-linked `gemgroup` can support a batch-like sensitivity null but not a true replicate upper bound.

## Scientific interpretation

GEARS rows marked `COMPLETED_GEARS_EVALUATION` are eligible for model-pilot interpretation inside the GEARS-run vocabulary, with `bns_status: UNVERIFIED` always stated. Bounded smoke rows remain integration checks only. Retrieval metrics below baselines (e.g., B3/FP-2) indicate the perturbation-shortcut question is live: exact-condition retrieval is easy under leakage-vulnerable splits and collapses under stricter holdouts, while delta-Pearson stays high — a dissociation pattern consistent with shortcut usage. GEO `gemgroup` sensitivity is batch-like metadata, not a replicate upper bound.

## Files generated

- `analysis_lock.yaml`
- `DATASET_PROVENANCE.md`
- `MODEL_PROVENANCE.md`
- `src/`
- `tests/`
- `configs/`
- `environment/environment_report.md`
- `figures/main/pilot_leakage_ladder.{pdf,svg,png}`
- `figures/main/pilot_truthfulness.{pdf,svg,png}`
- `figures/main/pilot_hallucination.{pdf,svg,png}`
- `results/pilot/pilot_summary.csv`
- `results/pilot/gears_20260812T152223Z/metadata.json`
- `results/pilot/gears_20260812T152223Z/model/`
- `results/pilot/gears_20260822T065552Z/` (GEARS L1 full: `gears_metrics.csv`, `gears_delta_centroids.pt`, `gears_perturbation_retrieval.csv`, `metadata.json`)
- `results/pilot/gears_20260822T122126Z/` (GEARS L2 full)
- `results/pilot/gears_20260822T172146Z/` (GEARS L3 full)
- `results/pilot/null_envelope_sensitivity.csv` (GEARS rows added)
- `results/tables/table5_primary_pilot_metrics.csv` and `results/tables/table6_null_envelope_sensitivity.csv` (rebuilt)

## GO / NO-GO

Decision: PROVISIONAL_GO_FOR_BASELINE_AUDIT; GEARS_FULL_EVALUATION_COMPLETED_PILOT (BNS unverified).

## Next 3 actions

1. Verify what the perturb-shortcut pattern means for the manuscript: L1-retrievable, L2/L3-collapsing retrieval with stable delta-Pearson is the headline audit signal from the completed GEARS rows.
2. Extend gemgroup-aware null-envelope sensitivity reporting and retrieval analysis to the manuscript draft; keep BNS `UNVERIFIED` until a true replicate label source is found.
3. Decide on dependency-free replication paths (e.g., prediction-only evaluation of candidate held-out settings) before any GO on GEARS-derived performance claims.
