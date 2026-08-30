# RESULTS v0.2

## Matched-Target Sensitivity

Matched-target restriction did not rescue cross-context transfer in the GEARS audit. In the K562-to-RPE1 direction, matched-source Pearson fell from 0.2812 within context to -0.0070 cross context, a paired drop of 0.2883 with a 95% interval of [0.2559, 0.3206]. UER50 increased from 0.1532 to 0.3877, and the sign-flip rate increased from 0.2714 to 0.5718.

The reverse RPE1-to-K562 direction showed the same pattern. Matched-source Pearson fell from 0.5501 to 0.0021, a paired drop of 0.5480 with a 95% interval of [0.5146, 0.5802]. UER50 increased from 0.0695 to 0.4655, and the sign-flip rate increased from 0.1207 to 0.4951.

Common-candidate retrieval stayed low. Its MRR drop was directionally consistent but did not provide the strongest statistical evidence because the bootstrap interval crossed zero in the source-context matched comparison. The strongest evidence for transfer collapse came from delta correlation, UER50, and sign-flip penalties.

## Phase 2C STATE Cross-Architecture Audit

The full GPU STATE audit completed all four locked tasks and produced performance-eligible outputs. STATE achieved delta-Pearson values of 0.4445 for Norman L1, 0.4060 for Norman L2, 0.2639 for Replogle K562 R-L1, and 0.1874 for Replogle K562-to-RPE1 R-L4. Retrieval MRR was 0.0757, 0.1377, 0.0262, and 0.0668 for the same tasks. UER50 was 0.0015, 0.0000, 0.1577, and 0.1403, respectively.

The Replogle full-summary comparison showed lower cross-context Pearson under STATE. K562 R-L1 had a delta-Pearson of 0.2639, whereas K562-to-RPE1 R-L4 had a delta-Pearson of 0.1874. The full-summary retrieval and UER endpoints were mixed because the R-L4 target set contained 73 normalized targets, compared with 216 targets in the K562 R-L1 task.

The matched-target STATE comparison gave a clearer transfer contrast. Across 15 shared Replogle targets, Pearson fell from 0.2955 in K562 R-L1 to 0.1792 in K562-to-RPE1 R-L4, a mean drop of 0.1163 with a 95% bootstrap interval of [0.0684, 0.1599]. Spearman and cosine similarity also decreased, with mean drops of 0.0709 and 0.1048. Lower-is-better endpoints moved in the opposite direction: UER50 increased from 0.1387 to 0.1667, and the sign-flip rate increased from 0.2581 to 0.3139.

These results partially reproduced the GEARS context-transfer failure phenotype with an independent STATE architecture. The strongest support came from the matched-target Pearson, Spearman, cosine, and sign-flip contrasts. The evidence was not a blanket confirmation because the full-summary MRR and UER50 endpoints were mixed and because BNS remained unverified.

## Second-Model Audit

Phase 2B classified STATE as not performance-eligible on the local CPU path, but Phase 2C replaced that compute-blocked status with full GPU evidence while preserving the original blocked rows. The updated second-model table now contains four retained compute-blocked rows and four performance-eligible STATE rows. The final Phase 2C decision is `PARTIAL_ARCHITECTURE_SUPPORT_TARGET_MATCHED_ENDPOINT_MIXED`.
