# Phase 0-2 Status

## Completed

- Repository scaffold created under `VirtualPerturb-Audit/`.
- Existing Git repository detected and reused.
- Environment audit started.
- Pre-data `analysis_lock.yaml` created.
- Literature, dataset, and model provenance registries initialized with source-linked entries.
- L0/L1/L2 split implementation and critical split tests added.
- Baseline, perturbation-specific, empirical-bound, and hallucination metric modules added.
- Unit tests passed on toy split/metric fixtures (`4 passed`).
- CLI blocked-run metadata behavior verified for missing Norman data.
- Isolated GEARS environment created at `environment/gears-venv`.
- `cell-gears==0.1.2` and `torch-geometric==2.6.1` installed in the isolated GEARS environment.
- GEARS import verified; first import takes about 35 seconds on this Mac.
- Corrected GEARS Norman official datafile URL to `https://dataverse.harvard.edu/api/access/datafile/6154020`.
- Norman GEARS-format AnnData downloaded from a public LUH Seafile mirror after official Dataverse command-line access returned WAF challenge.
- Norman local checksum recorded: `23ffb0fac6a847ff927cf7509d80d85052bfefbfb97610786a2dafaaefa0b6a0`.
- Real-data QC completed: 91,205 cells, 5,045 genes, 284 perturbations, 7,353 controls.
- L0/L1/L2 split integrity checks completed and passed; replicate/batch group overlap remains unverified because the processed file does not expose an informative replicate field.
- Baseline pilot completed for B0 no-change and B5 mean-effect baselines on L0/L1/L2.
- GEARS L1 batch smoke completed with official package training path, filtered GO tensor injection, strict JSON metadata, and model checkpoint written to `results/pilot/gears_20260812T152223Z/`.
- Pilot summary now reports perturbation-level bootstrap 95% CIs where enough perturbation units are available; single-unit GEARS smoke rows are marked `INSUFFICIENT_UNITS`.
- FP-1 perturbation-blind mean-effect and FP-3 label-shuffled mean-effect pilot probes completed for L1/L2.
- Perturbation-centroid retrieval and identity-confusion rows are generated for baseline and falsification-probe pseudobulk outputs; zero-vector predictions are marked `UNINFORMATIVE_PREDICTION`.
- GEO cell-identity metadata link audit completed: 88,843/91,205 GEARS cells matched, unordered perturbation concordance 0.9916, and `gemgroup` provides a partial batch-like field for sensitivity/null-envelope work.
- Gemgroup-aware control-control null-envelope sensitivity completed for L1/L2 baselines and FP-1/FP-3 probes in `results/pilot/null_envelope_sensitivity.csv`.
- Norman acquisition report created at `reports/NORMAN_ACQUISITION_REPORT.md`.

## Key results

Norman baseline and falsification-probe audit outputs are available in `results/pilot/pilot_summary.csv`. These should not be interpreted as full GEARS model performance. The current UER@50 values use a provisional empirical threshold because replicate/control null envelopes are not yet verified.

## Failed

- `python` executable is missing; `python3` is available.
- Full GEARS training/evaluation reproduction is not complete.
- A full CPU 1-epoch GEARS run was intentionally interrupted after the training loop had progressed beyond 1,600 batches because it was too slow for a smoke test; no performance conclusion was drawn from that interrupted run.
- The GEARS Dataverse datafile endpoint returned an AWS WAF challenge to a command-line HEAD request.
- The default GEARS GO graph tarball endpoint also returned an unusable WAF/empty-file response; the current smoke uses a documented filtered GO tensor generated from local GEARS prior files.
- `pertpy` is unavailable in the current environment.

## Risks

- GEARS/PyG dependencies require the isolated `environment/gears-venv` environment on this Mac.
- GEARS processed Norman data are convenient for pilot but still require preprocessing provenance scrutiny.
- Replicate fields remain missing; GEO-linked `gemgroup` is available for 97.4% of cells as a batch-like sensitivity field, but it is not a full replicate label.
- GEARS full training is expensive on CPU; GPU or bounded smoke settings should be used for development checks.

## Scientific interpretation

No GEARS biological or model-performance interpretation is available yet. Baseline-only metrics are descriptive sanity checks.

## Files generated

See `CHANGELOG.md`. Key generated outputs include `environment/environment_report.md`, `environment/gears_pip_freeze.txt`, real-data QC/split reports, baseline pilot outputs with uncertainty columns, pilot figures, provenance registries, and the GEARS batch-smoke checkpoint metadata.

## GO / NO-GO

Pilot status: PROVISIONAL_GO_FOR_BASELINE_AUDIT; GEARS_FULL_EVALUATION_PENDING.

## Next 3 actions

1. Run GEARS L1/L2 pilot on adequate compute and append comparable rows to `results/pilot/pilot_summary.csv`.
2. Extend gemgroup-aware null-envelope sensitivity to full GEARS prediction summaries after adequate model runs are available.
3. Continue searching for true replicate labels; keep replicate-derived BNS marked unverified unless found.
