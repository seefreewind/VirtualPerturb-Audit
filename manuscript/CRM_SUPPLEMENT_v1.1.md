# VirtualPerturb-Audit Supplementary Information

Draft version: CRM_SUPPLEMENT_v1.1

Generated: 2026-08-30 14:00:36 UTC

## Frozen Analysis State

Phase 2A-2C primary outputs are frozen. CRM v1.1 finalization did not rerun GEARS, rerun STATE, add datasets, redefine endpoints, or change matched-target registries.

## Permanent Limitations

- Replogle analyses use GEARS-compatible filtered essential-screen data, not complete Figshare+ processed objects.
- Validated biological replicate metadata were unavailable.
- BNS remains `UNVERIFIED`.
- UER remains `sensitivity_only` because its null envelope is not validated biological replicate ground truth.
- GEARS R-L4 is a GEARS-compatible cross-context inference adapter.
- STATE support is partial and endpoint-heterogeneous.
- GEARS and STATE absolute values are not direct universal leaderboard values.

## STATE Primary Metrics

| setting | split | metric_space | n_test_perturbations | pearson_delta | spearman_delta | cosine_delta | retrieval_mrr | uer50 | sign_flip_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Norman L1 STATE | L1 | audit_delta | 53.0000 | 0.4445 | 0.1974 | 0.4439 | 0.0757 | 0.0015 | 0.2536 |
| Norman L2 STATE | L2 | audit_delta | 28.0000 | 0.4060 | 0.2070 | 0.4059 | 0.1377 | 0.0000 | 0.2517 |
| Replogle K562 R-L1 STATE | R-L1-K562 | audit_delta | 216.0000 | 0.2639 | 0.1927 | 0.2583 | 0.0262 | 0.1577 | 0.2882 |
| Replogle K562 -> RPE1 R-L4 STATE | R-L4-K2R | target_control_audit_delta | 73.0000 | 0.1874 | 0.1669 | 0.2112 | 0.0668 | 0.1403 | 0.2990 |

## STATE Matched Transfer

| comparison | metric | n_matched_targets | source_mean | cross_context_mean | mean_drop_source_minus_cross | ci95_low | ci95_high | uncertainty_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| STATE Replogle matched targets: K562 R-L1 minus K562->RPE1 R-L4 | pearson_delta | 15.0000 | 0.2955 | 0.1792 | 0.1163 | 0.0684 | 0.1599 | BOOTSTRAP_PERTURBATION_LEVEL |
| STATE Replogle matched targets: K562 R-L1 minus K562->RPE1 R-L4 | spearman_delta | 15.0000 | 0.2240 | 0.1531 | 0.0709 | 0.0261 | 0.1110 | BOOTSTRAP_PERTURBATION_LEVEL |
| STATE Replogle matched targets: K562 R-L1 minus K562->RPE1 R-L4 | cosine_delta | 15.0000 | 0.3025 | 0.1977 | 0.1048 | 0.0529 | 0.1533 | BOOTSTRAP_PERTURBATION_LEVEL |
| STATE Replogle matched targets: K562 R-L1 minus K562->RPE1 R-L4 | uer50 | 15.0000 | 0.1387 | 0.1667 | -0.0280 | -0.0640 | 0.0107 | BOOTSTRAP_PERTURBATION_LEVEL |
| STATE Replogle matched targets: K562 R-L1 minus K562->RPE1 R-L4 | sign_flip_rate | 15.0000 | 0.2581 | 0.3139 | -0.0557 | -0.1000 | -0.0104 | BOOTSTRAP_PERTURBATION_LEVEL |

## GEARS Matched Transfer Sensitivity

| direction | metric | n_targets | within_estimate | cross_estimate | paired_difference | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| K562_within_vs_K562_to_RPE1 | pearson_delta | 150.0000 | 0.2812 | -0.0070 | 0.2883 | 0.2559 | 0.3206 |
| K562_within_vs_K562_to_RPE1 | spearman_delta | 150.0000 | 0.2004 | -0.0049 | 0.2053 | 0.1798 | 0.2309 |
| K562_within_vs_K562_to_RPE1 | rmse_delta | 150.0000 | 0.0856 | 0.1633 | 0.0777 | 0.0692 | 0.0856 |
| K562_within_vs_K562_to_RPE1 | cosine_delta | 150.0000 | 0.2756 | -0.0417 | -0.3173 | -0.3497 | -0.2840 |
| K562_within_vs_K562_to_RPE1 | retrieval_top1_native | 150.0000 | 0.0200 | 0.0067 | 0.0133 | -0.0133 | 0.0400 |
| K562_within_vs_K562_to_RPE1 | retrieval_top5_native | 150.0000 | 0.0733 | 0.0200 | 0.0533 | 0.0067 | 0.1000 |
| K562_within_vs_K562_to_RPE1 | retrieval_mrr_native | 150.0000 | 0.0574 | 0.0162 | 0.0413 | 0.0135 | 0.0700 |
| K562_within_vs_K562_to_RPE1 | retrieval_top1_common_candidate | 150.0000 | 0.0200 | 0.0133 | 0.0067 | -0.0267 | 0.0333 |
| K562_within_vs_K562_to_RPE1 | retrieval_top5_common_candidate | 150.0000 | 0.0800 | 0.0400 | 0.0400 | -0.0133 | 0.0933 |
| K562_within_vs_K562_to_RPE1 | retrieval_mrr_common_candidate | 150.0000 | 0.0657 | 0.0447 | 0.0209 | -0.0130 | 0.0536 |
| K562_within_vs_K562_to_RPE1 | uer20 | 150.0000 | 0.1370 | 0.3670 | 0.2300 | 0.2037 | 0.2550 |
| K562_within_vs_K562_to_RPE1 | uer50 | 150.0000 | 0.1532 | 0.3877 | 0.2345 | 0.2128 | 0.2547 |
| K562_within_vs_K562_to_RPE1 | uer100 | 150.0000 | 0.1846 | 0.4103 | 0.2257 | 0.2062 | 0.2453 |
| K562_within_vs_K562_to_RPE1 | sign_flip_rate | 150.0000 | 0.2714 | 0.5718 | 0.3005 | 0.2715 | 0.3291 |
| RPE1_within_vs_RPE1_to_K562 | pearson_delta | 148.0000 | 0.5501 | 0.0021 | 0.5480 | 0.5146 | 0.5802 |
| RPE1_within_vs_RPE1_to_K562 | spearman_delta | 148.0000 | 0.4419 | 0.0007 | 0.4412 | 0.4111 | 0.4698 |
| RPE1_within_vs_RPE1_to_K562 | rmse_delta | 148.0000 | 0.1191 | 0.1623 | 0.0431 | 0.0350 | 0.0512 |
| RPE1_within_vs_RPE1_to_K562 | cosine_delta | 148.0000 | 0.5478 | -0.0001 | -0.5479 | -0.5810 | -0.5140 |
| RPE1_within_vs_RPE1_to_K562 | retrieval_top1_native | 148.0000 | 0.0203 | 0.0000 | 0.0203 | 0.0000 | 0.0473 |
| RPE1_within_vs_RPE1_to_K562 | retrieval_top5_native | 148.0000 | 0.0405 | 0.0068 | 0.0338 | 0.0000 | 0.0676 |
| RPE1_within_vs_RPE1_to_K562 | retrieval_mrr_native | 148.0000 | 0.0435 | 0.0096 | 0.0340 | 0.0123 | 0.0593 |
| RPE1_within_vs_RPE1_to_K562 | retrieval_top1_common_candidate | 148.0000 | 0.0203 | 0.0068 | 0.0135 | -0.0135 | 0.0405 |
| RPE1_within_vs_RPE1_to_K562 | retrieval_top5_common_candidate | 148.0000 | 0.0473 | 0.0338 | 0.0135 | -0.0338 | 0.0608 |
| RPE1_within_vs_RPE1_to_K562 | retrieval_mrr_common_candidate | 148.0000 | 0.0506 | 0.0395 | 0.0111 | -0.0174 | 0.0400 |
| RPE1_within_vs_RPE1_to_K562 | uer20 | 148.0000 | 0.0551 | 0.4213 | 0.3662 | 0.3446 | 0.3872 |
| RPE1_within_vs_RPE1_to_K562 | uer50 | 148.0000 | 0.0695 | 0.4655 | 0.3961 | 0.3765 | 0.4147 |
| RPE1_within_vs_RPE1_to_K562 | uer100 | 148.0000 | 0.0819 | 0.4677 | 0.3858 | 0.3698 | 0.4011 |
| RPE1_within_vs_RPE1_to_K562 | sign_flip_rate | 148.0000 | 0.1207 | 0.4951 | 0.3744 | 0.3542 | 0.3933 |

## Additional Retrieval Metrics

Common-candidate retrieval rows in `results/tables/replogle_matched_rl1_rl4_sensitivity.csv` remain low in both transfer directions and should be interpreted as perturbation-specific retrieval stress tests, not as global expression-fit endpoints.

## Probe Controls

Probe-control rows are stored in `results/tables/replogle_gears_vs_probes.csv`. They show that mean-effect structure can support audit-delta Pearson while retrieval remains weak.

## QC, Split Integrity, Null Sensitivity, and Adapter Details

Primary provenance and audit depth are retained in `reports/replogle_split_integrity_report.md`, `reports/replicate_label_audit.md`, `reports/STATE_GEARS_METRIC_COMPATIBILITY.md`, `reports/STATE_RL4_ADAPTER_REPORT.md`, and `reports/PHASE2C_RESULT_INTERPRETATION.md`.

## Gene-Family L3, Seed Sensitivity, and Vocabulary Compatibility

Norman L3 gene-family holdout and seed-sensitivity outputs are retained in `results/tables/table8_seed_robustness_summary.*`, `results/tables/table9_gene_family_confusion_summary.*`, and `results/tables/table10_l3_gene_family_holdout_candidates.*`.
