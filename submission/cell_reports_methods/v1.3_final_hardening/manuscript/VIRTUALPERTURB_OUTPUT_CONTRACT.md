# VirtualPerturb-Audit Output Contract v1.3

| output | required | contents |
| --- | --- | --- |
| global_fit_metrics.tsv | yes | raw-space and audit-delta Pearson/Spearman/RMSE/MAE/cosine summaries |
| retrieval_metrics.tsv | recommended | Top1, Top5, MRR, rank, candidate universe, top match |
| unsupported_effect_metrics.tsv | recommended | UER@K values, K, null threshold, null provenance |
| sign_flip_metrics.tsv | recommended | sign-flip rate, support threshold, supported-gene count |
| split_integrity_report | yes | split rules, hash, forbidden-overlap checks, excluded labels |
| matched_transfer_summary | conditional | within/cross matched target estimates and intervals |
| probe_comparison | recommended | B0-B5 and FP1-FP3 endpoint table |
| audit_claim_profile | yes | endpoint-to-supported-interpretation assignment |
