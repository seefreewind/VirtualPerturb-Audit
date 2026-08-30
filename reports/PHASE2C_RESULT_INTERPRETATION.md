# Phase 2C Result Interpretation and Figure Notes

Generated: 2026-08-30 04:02:54 UTC

## Interpretation

The Phase 2C STATE run changes the second-model status from compute-blocked to performance-eligible. The four locked tasks completed, and the synchronized outputs support perturbation-level evaluation with the same endpoint family used in the GEARS audit.

The main scientific reading is partial cross-architecture support. STATE shows a lower Replogle cross-context Pearson than within-context K562 in the full summary, and the matched-target subset strengthens this direction: Pearson drops by 0.1163 with a 95% interval of [0.0684, 0.1599]. Spearman and cosine show the same direction. The sign-flip rate is also worse in cross-context transfer, with source-minus-cross difference -0.0557.

The result should not be described as a complete confirmation. Full-summary retrieval MRR is higher in STATE R-L4 than STATE R-L1, and UER@50 is slightly lower in the R-L4 full summary. These mixed endpoints are plausibly influenced by the smaller normalized R-L4 target set. The manuscript should therefore lead with matched-target transfer degradation and state the endpoint-level caveat explicitly.

## Primary STATE Metrics

| setting | split | metric_space | n_test_perturbations | pearson_delta | pearson_ci_low | pearson_ci_high | retrieval_mrr | uer50 | sign_flip_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Norman L1 STATE | L1 | audit_delta | 53 | 0.4445 | 0.3712 | 0.5190 | 0.0757 | 0.0015 | 0.2536 |
| Norman L2 STATE | L2 | audit_delta | 28 | 0.4060 | 0.3268 | 0.4851 | 0.1377 | 0.0000 | 0.2517 |
| Replogle K562 R-L1 STATE | R-L1-K562 | audit_delta | 216 | 0.2639 | 0.2436 | 0.2834 | 0.0262 | 0.1577 | 0.2882 |
| Replogle K562 -> RPE1 R-L4 STATE | R-L4-K2R | target_control_audit_delta | 73 | 0.1874 | 0.1699 | 0.2029 | 0.0668 | 0.1403 | 0.2990 |

## Matched-Target Transfer Contrast

Positive values for Pearson, Spearman, and cosine mean within-context R-L1 is higher. Negative values for UER@50 and sign flip mean the lower-is-better endpoint is worse in cross-context R-L4.

| metric | n_matched_targets | source_mean | cross_context_mean | mean_drop_source_minus_cross | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| pearson_delta | 15 | 0.2955 | 0.1792 | 0.1163 | 0.0684 | 0.1599 |
| spearman_delta | 15 | 0.2240 | 0.1531 | 0.0709 | 0.0261 | 0.1110 |
| cosine_delta | 15 | 0.3025 | 0.1977 | 0.1048 | 0.0529 | 0.1533 |
| uer50 | 15 | 0.1387 | 0.1667 | -0.0280 | -0.0640 | 0.0107 |
| sign_flip_rate | 15 | 0.2581 | 0.3139 | -0.0557 | -0.1000 | -0.0104 |

## Figure Decisions

- `phase2c_state_interpretation` is the preferred main Phase 2C explanatory figure. It separates STATE-only performance, matched-target contrast, and target-level distribution.
- Panel E in `phase2c_state_interpretation` pairs the 15 shared Replogle targets, so it is the cleanest visual evidence for the STATE context-transfer Pearson drop.
- `phase2c_gears_state_directionality` is a supplementary or reviewer-response figure. It shows that GEARS and STATE both have lower R-L4 Pearson than R-L1, while preserving the mixed endpoint picture.
- `gears_state_confirmatory_audit` is retained as the original compact comparison, but it should not be the main narrative figure because it places GEARS raw-space and STATE audit-delta values side by side.

## Suggested Caption

Phase 2C STATE cross-architecture audit. STATE was evaluated on the locked Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4 tasks using audit-delta endpoints. In Replogle, cross-context transfer showed lower target-level agreement than within-context K562, and the matched-target contrast confirmed a Pearson drop with perturbation-level bootstrap uncertainty. Retrieval and UER endpoints were mixed in the full-summary table, so the result supports a bounded, partial architecture-independent transfer-degradation claim.
