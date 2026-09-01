# Figure 5 CI Source Audit

| Endpoint | Estimate source | CI source | n targets | Bootstrap resamples | Paired? |
|---|---|---|---:|---|---|
| Audit-delta Pearson | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| Spearman agreement | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| Cosine agreement | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| Sign-flip rate | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| UER50† | `state_transfer_drop.csv` | perturbation-target-level bootstrap | 15 | frozen STATE bootstrap output | yes |
| Common-candidate MRR | `state_matched_common_candidate_retrieval_summary.tsv` | no frozen valid CI; points only | 15 | not applied | no |
