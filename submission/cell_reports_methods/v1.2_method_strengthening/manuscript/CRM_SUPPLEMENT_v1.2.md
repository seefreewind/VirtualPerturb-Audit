# VirtualPerturb-Audit Supplementary Information

Draft version: CRM_SUPPLEMENT_v1.2

Generated: 2026-08-30 23:38:59 UTC

## Frozen Analysis State

The v1.2 package strengthens method description and reporting. It does not retrain GEARS, rerun STATE, change frozen split assignments, alter the matched-target registry, redefine endpoints, or replace primary result tables.

## Supplementary Methods

### Split Definitions

L0-L3 define Norman discovery and stress-test splits from the GEARS-compatible workflow. R-L1 is a within-cell-line Replogle target holdout. R-L4 is a cross-context inference stress test using source-context training and target-context control/basal input. R-L4 supports context-transfer stress testing with an adapter caveat and should not be described as a native cell-line-aware GEARS training design.

### Baselines and Probes

B0 is no-change prediction. B1 is global perturbed mean. B2 is context-matched perturbed mean. B3-B4 cover simple low-capacity linear/PCA-ridge variants when available. B5 is mean-effect prediction. FP1 removes perturbation-specific information through a perturbation-blind probe. FP2 removes cell-state information when an implementation is available. FP3 uses label shuffling as a diagnostic control and is not a biological model.

### UER and Sign-Flip Details

UER@K orders genes by predicted absolute effect and counts genes whose observed effect falls within the selected null envelope or threshold. UER50 is emphasized because it summarizes unsupported behavior among the 50 largest predicted effects. The current null is an internal sensitivity envelope, not validated biological replicate ground truth. Sign-flip rate is computed among genes with observed support, using the implemented support threshold and comparing predicted versus observed effect direction.

### Retrieval Candidate Universe

Retrieval compares each predicted perturbation delta with candidate true perturbation centroids. Native-candidate retrieval uses the candidate universe of the specific output. Common-candidate retrieval restricts both sides to the shared candidate universe and is used as a sensitivity analysis for matched comparisons.

### Matched-Target Registry

The GEARS K562-to-RPE1 matched registry contains 150 shared targets. The RPE1-to-K562 registry contains 148 shared targets. The STATE K562-to-RPE1 matched analysis contains 15 shared targets. These registries control target-composition differences while preserving the cross-context stress-test design.

### Metric Disagreement

The existing endpoint heatmap and metric divergence table are retained at `figures/supplementary/phase2c_endpoint_heatmap.*` and `results/tables/metric_divergence_profile.csv`. No new exploratory metric-disagreement analysis was added in v1.2.

## STATE Primary Metrics

| setting | split | metric_space | n | pearson_delta | spearman_delta | cosine_delta | MRR | UER50 | sign_flip_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Norman L1 STATE | L1 | audit_delta | 53 | 0.4445 | 0.1974 | 0.4439 | 0.0757 | 0.0015 | 0.2536 |
| Norman L2 STATE | L2 | audit_delta | 28 | 0.4060 | 0.2070 | 0.4059 | 0.1377 | 0.0000 | 0.2517 |
| Replogle K562 R-L1 STATE | R-L1-K562 | audit_delta | 216 | 0.2639 | 0.1927 | 0.2583 | 0.0262 | 0.1577 | 0.2882 |
| Replogle K562 -> RPE1 R-L4 STATE | R-L4-K2R | target_control_audit_delta | 73 | 0.1874 | 0.1669 | 0.2112 | 0.0668 | 0.1403 | 0.2990 |

## STATE Matched Transfer

| metric | n_matched_targets | within | cross_context | within_minus_cross | 95% interval |
| --- | --- | --- | --- | --- | --- |
| pearson_delta | 15 | 0.2955 | 0.1792 | 0.1163 | [0.0684, 0.1599] |
| spearman_delta | 15 | 0.2240 | 0.1531 | 0.0709 | [0.0261, 0.1110] |
| cosine_delta | 15 | 0.3025 | 0.1977 | 0.1048 | [0.0529, 0.1533] |
| uer50 | 15 | 0.1387 | 0.1667 | -0.0280 | [-0.0640, 0.0107] |
| sign_flip_rate | 15 | 0.2581 | 0.3139 | -0.0557 | [-0.1000, -0.0104] |

## GEARS Matched Transfer Sensitivity

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

## Permanent Scope Limitations

- Replogle analyses use GEARS-compatible filtered essential-screen data rather than complete Figshare+ processed objects.
- Biological-null score could not be verified from validated biological replicate metadata.
- UER is an internal sensitivity measure.
- GEARS R-L4 uses a cross-context inference adapter.
- STATE support is partial and endpoint-heterogeneous.
- Absolute GEARS and STATE values are not a universal model leaderboard.
