# Phase 2B Matched-Target Sensitivity

## Current Status

```text
Phase 2A freeze commit: 6872a97
GEARS retraining:       NOT_PERFORMED
Matched registry:       COMPLETE
Native retrieval:       COMPLETE
Common-candidate retrieval: COMPLETE
Gate decision:          MATCHED_SUPPORTS_TRANSFER_COLLAPSE
```

## Matched Target Counts

- `n_matched_K2R_source = 150`
- `n_matched_R2K_source = 148`
- `n_matched_K2R_target_context = 148`
- `n_matched_R2K_target_context = 150`

## Primary Source-Context Matched Results

| Direction | Metric | Within | Cross | Paired difference | 95% CI | p value |
|---|---:|---:|---:|---:|---:|---:|
| K562_within_vs_K562_to_RPE1 | pearson_delta | 0.2812 | -0.0070 | 0.2883 | [0.2559, 0.3206] | 0.0005 |
| K562_within_vs_K562_to_RPE1 | retrieval_mrr_common_candidate | 0.0657 | 0.0447 | 0.0209 | [-0.0130, 0.0536] | 0.2329 |
| K562_within_vs_K562_to_RPE1 | uer50 | 0.1532 | 0.3877 | 0.2345 | [0.2128, 0.2547] | 0.0005 |
| K562_within_vs_K562_to_RPE1 | sign_flip_rate | 0.2714 | 0.5718 | 0.3005 | [0.2715, 0.3291] | 0.0005 |
| RPE1_within_vs_RPE1_to_K562 | pearson_delta | 0.5501 | 0.0021 | 0.5480 | [0.5146, 0.5802] | 0.0005 |
| RPE1_within_vs_RPE1_to_K562 | retrieval_mrr_common_candidate | 0.0506 | 0.0395 | 0.0111 | [-0.0174, 0.0400] | 0.4698 |
| RPE1_within_vs_RPE1_to_K562 | uer50 | 0.0695 | 0.4655 | 0.3961 | [0.3765, 0.4147] | 0.0005 |
| RPE1_within_vs_RPE1_to_K562 | sign_flip_rate | 0.1207 | 0.4951 | 0.3744 | [0.3542, 0.3933] | 0.0005 |

## Interpretation

Matched-target sensitivity preserves the Phase 2A direction of effect. Within-context GEARS has substantially higher target-level Pearson than the matched cross-context adapter, while common-candidate MRR remains very low in cross-context analysis. UER@50 and sign-flip burden are higher under R-L4 in both primary source-context comparisons.

This means the R-L4 collapse is not explained away by comparing different test-target compositions. Target composition may affect exact magnitudes, but the matched analysis keeps the central conclusion intact.

## Retrieval Candidate Universe

Native retrieval uses each run's original candidate universe. Common-candidate retrieval was recomputed from saved prediction/truth centroids using the exact same matched target set within each paired comparison. The main matched retrieval statement uses common-candidate MRR.

## Guardrails

- No GEARS model was retrained for this analysis.
- All estimates use existing per-target outputs from completed R-L1 and R-L4 runs.
- Source-context comparisons are primary; target-context comparisons are exploratory.
- All Replogle claims remain `GEARS-compatible filtered essential-screen data`.
- `BNS_STATUS = UNVERIFIED`; UER remains `sensitivity_only`.

## Outputs

- `results/tables/replogle_matched_target_registry.tsv`
- `results/tables/replogle_matched_rl1_rl4_target_level.csv`
- `results/tables/replogle_matched_rl1_rl4_sensitivity.csv`
- `figures/main/replogle_matched_transfer_sensitivity.{pdf,svg,png}`
