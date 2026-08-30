# STATE R-L4 Adapter Report

Generated: 2026-08-30 00:24:12 UTC

The R-L4 STATE adapter trained on K562 and predicted in the RPE1 target context. Evaluation used target-context controls from the synchronized STATE prediction pair and did not modify frozen GEARS splits, registries, or Phase 2A/2B metrics.

R-L4 STATE primary metrics:

| setting | split | train_cell_line | test_cell_line | metric_space | n_test_perturbations | pearson_delta | retrieval_mrr | uer50 | sign_flip_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Replogle K562 -> RPE1 R-L4 STATE | R-L4-K2R | K562 | RPE1 | target_control_audit_delta | 73 | 0.1874 | 0.0668 | 0.1403 | 0.2990 |

Adapter status: `PERFORMANCE_ELIGIBLE_FULL_GPU`; BNS `UNVERIFIED`; UER `sensitivity_only`.
