# Phase 2B Decision

更新时间：2026-08-29

## Gates

| Gate | Decision | Evidence |
|---|---|---|
| Phase 2A frozen before Phase 2B | pass | commit `6872a97` |
| Matched-target registry | pass | `results/tables/replogle_matched_target_registry.tsv` |
| Matched-target sensitivity | pass | `reports/PHASE2B_MATCHED_TARGET_SENSITIVITY.md` |
| Common-candidate retrieval | pass | included in `results/tables/replogle_matched_rl1_rl4_sensitivity.csv` |
| scGPT feasibility | fail locally | official candidate, but local fair-execution gate failed |
| STATE feasibility | partial | official CLI and smoke pass; full deep matrix compute-blocked |
| Second deep architecture performance | fail locally | no performance-eligible metrics for four tasks |

## Scientific Decision

```text
MATCHED_TARGET_GATE = MATCHED_SUPPORTS_TRANSFER_COLLAPSE
SECOND_DEEP_MODEL_GATE = NO_SECOND_MODEL_FAIRLY_REPRODUCIBLE_LOCALLY
PHASE2B_DECISION = CONDITIONAL_MANUSCRIPT_NOT_PROMOTE_TO_FULL_ARCHITECTURE_GENERAL_CLAIM
```

The matched-target Replogle analysis supports the central transfer-collapse result. K562-to-RPE1 Pearson dropped by 0.2883; RPE1-to-K562 Pearson dropped by 0.5480. These drops persisted after target matching, so the effect is not explained by a different held-out target composition.

The manuscript can move forward as a conditional stress-test paper centered on metric divergence and context-transfer failure in GEARS. It should not claim architecture-general failure until a second deep model is completed in a suitable GPU/Linux environment.

## Strongest Result

The strongest Phase 2B result is that matched-target restriction preserves the cross-context collapse in both directions, especially for delta Pearson, UER50, and sign-flip penalties.

## Main Limitation

The main limitation is not the matched-target analysis; it is the absence of a performance-eligible second deep architecture run. Replogle remains filtered-data scope, and BNS remains unverified.

## Next Recommended Action

Run the second architecture on a GPU/Linux environment using the existing STATE adapter first, then rerun the same four-task matrix without changing frozen GEARS results or matched-target definitions.
