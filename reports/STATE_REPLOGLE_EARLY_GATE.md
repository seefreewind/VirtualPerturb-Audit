# STATE Replogle Early Gate

Generated: 2026-08-30 00:24:12 UTC

Both Replogle STATE tasks are performance-eligible full GPU outputs and passed local metric extraction.

| setting | split | metric_space | n_test_perturbations | pearson_delta | pearson_ci_low | pearson_ci_high | retrieval_mrr | uer50 | sign_flip_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Replogle K562 R-L1 STATE | R-L1-K562 | audit_delta | 216 | 0.2639 | 0.2436 | 0.2834 | 0.0262 | 0.1577 | 0.2882 |
| Replogle K562 -> RPE1 R-L4 STATE | R-L4-K2R | target_control_audit_delta | 73 | 0.1874 | 0.1699 | 0.2029 | 0.0668 | 0.1403 | 0.2990 |

Matched-target transfer summary:

| metric | n_matched_targets | source_mean | cross_context_mean | mean_drop_source_minus_cross | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| pearson_delta | 15 | 0.2955 | 0.1792 | 0.1163 | 0.0684 | 0.1599 |
| spearman_delta | 15 | 0.2240 | 0.1531 | 0.0709 | 0.0261 | 0.1110 |
| cosine_delta | 15 | 0.3025 | 0.1977 | 0.1048 | 0.0529 | 0.1533 |
| uer50 | 15 | 0.1387 | 0.1667 | -0.0280 | -0.0640 | 0.0107 |
| sign_flip_rate | 15 | 0.2581 | 0.3139 | -0.0557 | -0.1000 | -0.0104 |
