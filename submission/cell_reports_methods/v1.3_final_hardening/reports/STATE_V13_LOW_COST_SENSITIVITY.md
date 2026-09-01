# STATE v1.3 Low-Cost Sensitivity Analyses

## Leave-one-target-out

| metric | min | median | max | n_positive | n_negative |
| --- | --- | --- | --- | --- | --- |
| pearson_drop | 0.1080 | 0.1144 | 0.1302 | 15 | 0 |
| spearman_drop | 0.0618 | 0.0708 | 0.0858 | 15 | 0 |
| cosine_drop | 0.0944 | 0.1044 | 0.1197 | 15 | 0 |
| uer50_difference | -0.0386 | -0.0271 | -0.0200 | 0 | 15 |
| sign_flip_difference | -0.0674 | -0.0549 | -0.0457 | 0 | 15 |

Pearson, Spearman, and cosine drops remain positive after omitting any one of the 15 matched STATE targets, indicating that the STATE matched audit-delta transfer signal is not driven by a single target. This is exploratory sensitivity from frozen outputs.

## Common-candidate retrieval

| run_id | n_targets | Top1 | Top5 | MRR |
| --- | --- | --- | --- | --- |
| S3_replogle_k562_rl1 | 15 | 0.1333 | 0.3333 | 0.2594 |
| S4_replogle_k562_to_rpe1_rl4 | 15 | 0.0667 | 0.3333 | 0.2212 |

The common-candidate retrieval calculation uses the same 15 matched targets as candidates for both STATE within-context and cross-context outputs and is exploratory.
