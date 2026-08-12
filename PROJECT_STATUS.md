# Phase 0-1 Status

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

## Key results

No verified Norman/GEARS biological pilot results yet. Current outputs are framework and reproducibility infrastructure.

## Failed

- `python` executable is missing; `python3` is available.
- Norman data not yet downloaded into `data/raw/norman/perturb_processed.h5ad`.
- GEARS official reproduction not yet executed.
- The GEARS Dataverse datafile endpoint returned an AWS WAF challenge to a command-line HEAD request.
- `pertpy` is unavailable in the current environment.

## Risks

- GEARS/PyG dependencies may need an isolated environment on Apple Silicon.
- GEARS processed Norman data are convenient for pilot but require preprocessing provenance scrutiny.
- Batch/replicate fields may be missing or incomplete in the processed file.

## Scientific interpretation

None. No empirical model-performance conclusion is available yet.

## Files generated

See `CHANGELOG.md`. Key generated outputs include `environment/environment_report.md`, pilot figure placeholders in `figures/main/`, manuscript skeletons, provenance registries, and table exports in `results/tables/`.

## GO / NO-GO

Pilot status: BLOCKED_PENDING_DATA_AND_GEARS_REPRODUCTION.

## Next 3 actions

1. Download and checksum the official GEARS Norman processed data.
2. Create an isolated GEARS environment or document installation blocker.
3. Run L0/L1/L2 split integrity checks on the real Norman AnnData.
