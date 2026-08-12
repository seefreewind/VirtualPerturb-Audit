# Pilot Decision

## Completed

- Project scaffold and pilot code infrastructure are in place.
- Split, leakage, baseline, expression metric, BNS, UER@K, and Sign Flip Rate implementations have unit tests.
- Current unit test status: PASS on toy fixtures.
- Missing-data CLI behavior: PASS; blocked metadata is written and the run fails loudly.
- GEARS package import is verified in `environment/gears-venv` after installing `cell-gears==0.1.2` and `torch-geometric==2.6.1`.
- Norman GEARS-format data have been downloaded from the LUH Seafile mirror, checksumed, and audited locally.
- Real-data QC and L0/L1/L2 split integrity reports pass, with replicate/batch overlap marked unverified because no informative replicate field is present.
- Baseline pilot has completed for B0 no-change and B5 mean-effect baselines.
- GEARS L1 batch-smoke training completed with the official `cell-gears==0.1.2` package and wrote a checkpoint plus strict JSON metadata to `results/pilot/gears_20260812T152223Z/`.
- Baseline rows include perturbation-level bootstrap 95% CIs; the bounded GEARS smoke row is marked `INSUFFICIENT_UNITS` because it evaluated only one perturbation.

## Key results

Baseline-only Norman pilot results are present in `results/pilot/pilot_summary.csv`. No full GEARS performance result is verified yet.

## Failed

- Full GEARS training/evaluation reproduction has not completed.
- A full CPU 1-epoch GEARS run was intentionally interrupted after more than 1,600 batches because it was too slow for smoke validation.
- First GEARS L1 smoke run created official PyG cell graphs but failed because custom splits included perturbations filtered out by the GEARS GO graph. The runner was updated to export custom splits from GEARS-filtered AnnData.
- GEARS dynamic perturbation graph construction completed but training failed with perturbation-index mismatch against cached cell graphs. The runner now defaults to the official `gene_set_path` route using `essential_all_data_pert_genes.pkl`.
- GEARS `essential` perturbation graph initialization initially failed because the cached dynamic GO CSV contained genes outside the current perturbation node map. The runner now injects a filtered GO tensor for non-default graph modes and records the filtered edge/node counts.
- Official GEARS/Dataverse Norman endpoint returned an AWS WAF challenge to a non-interactive `curl` probe on 2026-08-12.
- `pertpy` is not installed in the current main environment, so it was not used as an alternate data loader.

## Risks

- Pilot cannot be declared GO for GEARS until full training/evaluation or a documented prediction-only benchmark is complete.
- Any GEARS dependency workaround must be documented as a model-adapter change if it alters official behavior.
- Current UER@50 uses a provisional empirical threshold; replicate/control null envelopes remain unverified.

## Scientific interpretation

No GEARS biological or model-performance interpretation is permitted at this stage. Baseline-only outputs can be used to debug metrics and figures.

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

## GO / NO-GO

Decision: PROVISIONAL_GO_FOR_BASELINE_AUDIT; NO_GO_FOR_GEARS_PERFORMANCE_CLAIMS.

## Next 3 actions

1. Add GEARS prediction export and metric integration.
2. Run GEARS L1/L2 on adequate compute or bounded development settings.
3. Replace provisional UER/BNS thresholds with verified replicate/control null envelopes when source metadata permit.
