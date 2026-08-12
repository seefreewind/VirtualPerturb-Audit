# Pilot Decision

## Completed

- Project scaffold and pilot code infrastructure are in place.
- Split, leakage, baseline, expression metric, BNS, UER@K, and Sign Flip Rate implementations have unit tests.
- Current unit test status: PASS on toy fixtures.
- Missing-data CLI behavior: PASS; blocked metadata is written and the run fails loudly.

## Key results

No verified Norman/GEARS pilot performance results yet.

## Failed

- Norman acquisition has not completed in the local workspace.
- GEARS reproduction has not completed.
- Official GEARS/Dataverse Norman endpoint returned an AWS WAF challenge to a non-interactive `curl` probe on 2026-08-12.
- `pertpy` is not installed in the current main environment, so it was not used as an alternate data loader.

## Risks

- Pilot cannot be declared GO until real-data split diagnostics pass.
- Any GEARS dependency workaround must be documented as a model-adapter change if it alters official behavior.

## Scientific interpretation

No biological or model-performance interpretation is permitted at this stage.

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

## GO / NO-GO

Decision: BLOCKED_PENDING_DATA_AND_MODEL_REPRODUCTION.

## Next 3 actions

1. Acquire Norman processed data from the official GEARS loader URL.
2. Run real-data QC and split integrity.
3. Attempt GEARS installation in an isolated environment.
