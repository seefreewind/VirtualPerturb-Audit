# STATE-GEARS Metric Compatibility

Generated: 2026-08-30 00:24:12 UTC

STATE Phase 2C was evaluated with the same perturbation-level endpoint family used by the frozen GEARS audit: delta-Pearson, retrieval Top1/Top5/MRR, UER@20/50/100, sign-flip rate, RMSE, Spearman, and cosine similarity. The primary STATE interpretation uses audit-delta space, subtracting the real control mean from both predicted and observed target means. The Replogle R-L4 cross-context task is labeled `target_control_audit_delta`, matching the prior GEARS adapter convention.

Perturbation labels were normalized with the project convention that drops explicit control partners, so labels such as `ctrl+X` and `X` are evaluated as the same target `X`. This leaves 53 normalized Norman L1 STATE targets from 55 frozen test conditions and 28 normalized Norman L2 STATE targets from 40 frozen test conditions. The split-alignment audit remains fully aligned at the frozen-condition level.

BNS remains `UNVERIFIED`; UER is retained as `sensitivity_only` because the null is the median absolute observed delta rather than an externally verified biological null.

Primary comparison table:

| setting | model_type | split | metric_space | n_test_perturbations | pearson_delta | retrieval_mrr | uer50 | sign_flip_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Norman L1 GEARS | GEARS | L1 | gears_raw | 55 | 0.9887 | 0.3277 | 0.0000 | 0.0000 |
| Norman L2 GEARS | GEARS | L2 | gears_raw | 40 | 0.9838 | 0.1471 | 0.0000 | 0.0000 |
| Replogle K562 R-L1 GEARS | GEARS | R-L1-K562 | gears_raw | 216 | 0.9851 | 0.0445 | 0.0000 | 0.0000 |
| Replogle K562 -> RPE1 R-L4 GEARS | GEARS | R-L4-K2R | target_control_audit_delta | 732 | 0.0063 | 0.0126 | 0.3847 | 0.5520 |
| Norman L1 STATE | STATE | L1 | audit_delta | 53 | 0.4445 | 0.0757 | 0.0015 | 0.2536 |
| Norman L2 STATE | STATE | L2 | audit_delta | 28 | 0.4060 | 0.1377 | 0.0000 | 0.2517 |
| Replogle K562 R-L1 STATE | STATE | R-L1-K562 | audit_delta | 216 | 0.2639 | 0.0262 | 0.1577 | 0.2882 |
| Replogle K562 -> RPE1 R-L4 STATE | STATE | R-L4-K2R | target_control_audit_delta | 73 | 0.1874 | 0.0668 | 0.1403 | 0.2990 |
