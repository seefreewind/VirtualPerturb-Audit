# VirtualPerturb-Audit Supplementary Information

Draft version: CRM_SUPPLEMENT_v1.3

Generated: 2026-09-01 12:05:52 UTC

## Frozen Analysis State

The v1.3 package strengthens operational definitions, software contracts, reference verification, deposition readiness, and reviewer-facing sensitivity checks. It does not retrain GEARS, rerun STATE inference, change frozen split assignments, alter the matched-target registry, redefine endpoints, or replace primary result tables.

## Supplementary Table 1. Reporting Checklist

See `manuscript/VIRTUALPERTURB_AUDIT_REPORTING_CHECKLIST_v1.0.md`.

## Supplementary Table 2. Baseline Registry

See `results/tables/baseline_definition_registry.tsv`.

## Supplementary Table 3. Falsification Probe Registry

See `results/tables/falsification_probe_registry.tsv`.

## Supplementary Table 4. STATE Primary Metrics

| setting | split | metric_space | n | pearson_delta | spearman_delta | cosine_delta | MRR | UER50 | sign_flip_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Norman L1 STATE | L1 | audit_delta | 53 | 0.4445 | 0.1974 | 0.4439 | 0.0757 | 0.0015 | 0.2536 |
| Norman L2 STATE | L2 | audit_delta | 28 | 0.4060 | 0.2070 | 0.4059 | 0.1377 | 0.0000 | 0.2517 |
| Replogle K562 R-L1 STATE | R-L1-K562 | audit_delta | 216 | 0.2639 | 0.1927 | 0.2583 | 0.0262 | 0.1577 | 0.2882 |
| Replogle K562 -> RPE1 R-L4 STATE | R-L4-K2R | target_control_audit_delta | 73 | 0.1874 | 0.1669 | 0.2112 | 0.0668 | 0.1403 | 0.2990 |

## Supplementary Table 5. STATE Matched Transfer

| metric | n_matched_targets | within | cross_context | within_minus_cross | 95% interval |
| --- | --- | --- | --- | --- | --- |
| pearson_delta | 15 | 0.2955 | 0.1792 | 0.1163 | [0.0684, 0.1599] |
| spearman_delta | 15 | 0.2240 | 0.1531 | 0.0709 | [0.0261, 0.1110] |
| cosine_delta | 15 | 0.3025 | 0.1977 | 0.1048 | [0.0529, 0.1533] |
| uer50 | 15 | 0.1387 | 0.1667 | -0.0280 | [-0.0640, 0.0107] |
| sign_flip_rate | 15 | 0.2581 | 0.3139 | -0.0557 | [-0.1000, -0.0104] |

## Supplementary Table 6. STATE Leave-One-Target-Out Sensitivity

| metric | min | median | max | n_positive | n_negative |
| --- | --- | --- | --- | --- | --- |
| pearson_drop | 0.1080 | 0.1144 | 0.1302 | 15 | 0 |
| spearman_drop | 0.0618 | 0.0708 | 0.0858 | 15 | 0 |
| cosine_drop | 0.0944 | 0.1044 | 0.1197 | 15 | 0 |
| uer50_difference | -0.0386 | -0.0271 | -0.0200 | 0 | 15 |
| sign_flip_difference | -0.0674 | -0.0549 | -0.0457 | 0 | 15 |

The leave-one-target-out analysis is exploratory and uses frozen STATE matched target metrics. Pearson, Spearman, and cosine drops remain positive for all 15 omissions.

## Supplementary Table 7. STATE Common-Candidate Retrieval

| run_id | n_targets | Top1 | Top5 | MRR |
| --- | --- | --- | --- | --- |
| S3_replogle_k562_rl1 | 15 | 0.1333 | 0.3333 | 0.2594 |
| S4_replogle_k562_to_rpe1_rl4 | 15 | 0.0667 | 0.3333 | 0.2212 |

This sensitivity uses the same 15 matched targets as the retrieval candidate universe for both STATE runs and is exploratory.

## Supplementary Table 8. GEARS Matched Transfer Sensitivity

| direction | metric | n_targets | within | cross_context | difference | 95% interval |
| --- | --- | --- | --- | --- | --- | --- |
| K562_within_vs_K562_to_RPE1 | pearson_delta | 150 | 0.2812 | -0.0070 | 0.2883 | [0.2559, 0.3206] |
| K562_within_vs_K562_to_RPE1 | retrieval_mrr_native | 150 | 0.0574 | 0.0162 | 0.0413 | [0.0135, 0.0700] |
| K562_within_vs_K562_to_RPE1 | retrieval_mrr_common_candidate | 150 | 0.0657 | 0.0447 | 0.0209 | [-0.0130, 0.0536] |
| K562_within_vs_K562_to_RPE1 | uer50 | 150 | 0.1532 | 0.3877 | 0.2345 | [0.2128, 0.2547] |
| K562_within_vs_K562_to_RPE1 | sign_flip_rate | 150 | 0.2714 | 0.5718 | 0.3005 | [0.2715, 0.3291] |
| RPE1_within_vs_RPE1_to_K562 | pearson_delta | 148 | 0.5501 | 0.0021 | 0.5480 | [0.5146, 0.5802] |
| RPE1_within_vs_RPE1_to_K562 | retrieval_mrr_native | 148 | 0.0435 | 0.0096 | 0.0340 | [0.0123, 0.0593] |
| RPE1_within_vs_RPE1_to_K562 | retrieval_mrr_common_candidate | 148 | 0.0506 | 0.0395 | 0.0111 | [-0.0174, 0.0400] |
| RPE1_within_vs_RPE1_to_K562 | uer50 | 148 | 0.0695 | 0.4655 | 0.3961 | [0.3765, 0.4147] |
| RPE1_within_vs_RPE1_to_K562 | sign_flip_rate | 148 | 0.1207 | 0.4951 | 0.3744 | [0.3542, 0.3933] |
| RPE1_within_vs_K562_to_RPE1 | pearson_delta | 148 | 0.5501 | 0.0092 | 0.5409 | [0.5068, 0.5745] |
| RPE1_within_vs_K562_to_RPE1 | retrieval_mrr_native | 148 | 0.0435 | 0.0097 | 0.0339 | [0.0138, 0.0582] |
| RPE1_within_vs_K562_to_RPE1 | retrieval_mrr_common_candidate | 148 | 0.0506 | 0.0463 | 0.0043 | [-0.0231, 0.0339] |
| RPE1_within_vs_K562_to_RPE1 | uer50 | 148 | 0.0695 | 0.3808 | 0.3114 | [0.2955, 0.3265] |
| RPE1_within_vs_K562_to_RPE1 | sign_flip_rate | 148 | 0.1207 | 0.5494 | 0.4287 | [0.4001, 0.4570] |
| K562_within_vs_RPE1_to_K562 | pearson_delta | 150 | 0.2812 | 0.0023 | 0.2789 | [0.2489, 0.3102] |
| K562_within_vs_RPE1_to_K562 | retrieval_mrr_native | 150 | 0.0574 | 0.0116 | 0.0459 | [0.0223, 0.0723] |
| K562_within_vs_RPE1_to_K562 | retrieval_mrr_common_candidate | 150 | 0.0657 | 0.0315 | 0.0342 | [0.0088, 0.0624] |
| K562_within_vs_RPE1_to_K562 | uer50 | 150 | 0.1532 | 0.4697 | 0.3165 | [0.2953, 0.3383] |
| K562_within_vs_RPE1_to_K562 | sign_flip_rate | 150 | 0.2714 | 0.4979 | 0.2266 | [0.2045, 0.2491] |

## Supplementary Methods: UER and Sign Flip

UER@K orders genes by predicted absolute effect and counts genes whose observed effect falls within the internal null threshold. The current null threshold is the median absolute observed delta in the evaluated vector. UER is not validated biological replicate ground truth. Sign-flip rate is computed among genes above the 95th percentile of absolute observed delta and compares predicted versus observed direction.

## Supplementary Methods: Contracts

The input and output contracts are provided as `manuscript/VIRTUALPERTURB_INPUT_CONTRACT.md` and `manuscript/VIRTUALPERTURB_OUTPUT_CONTRACT.md`.

## Permanent Scope Limitations

- Replogle analyses use GEARS-compatible filtered essential-screen data rather than complete Figshare+ processed objects.
- A replicate-derived empirical performance bound could not be established because validated biological replicate metadata were unavailable.
- UER is an internal sensitivity measure.
- GEARS R-L4 uses a cross-context inference adapter.
- STATE support is partial and endpoint-heterogeneous.
- Absolute GEARS and STATE values are not a universal model leaderboard.
