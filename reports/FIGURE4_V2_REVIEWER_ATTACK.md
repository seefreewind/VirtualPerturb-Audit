# Figure 4 v2 Reviewer Attack Test

| Criticism | Status | Response |
|---|---:|---|
| Are matched targets truly identical within each comparison? | RESOLVED | Each primary comparison uses the same perturbation targets within its direction; n=150 and n=148 are verified against frozen target-level rows. |
| Is audit-delta Pearson clearly distinguished from raw-space Pearson? | RESOLVED | The metric label is `Audit-delta Pearson`, and the legend describes control-subtracted response agreement. |
| Is the statistical unit perturbation target? | RESOLVED | The legend states perturbation-level bootstrap resampling and matched perturbation targets. |
| Does the plot imply cell-level precision? | RESOLVED | Individual points are target-level values and are visually secondary; CIs are perturbation-level paired bootstrap intervals. |
| Are CIs paired? | RESOLVED | Effect-size axis is within-minus-cross and reports paired bootstrap CIs from the frozen summary table. |
| Does target matching remove all confounding? | PARTIAL | The legend states matching reduces target-composition differences but does not isolate all contributors. |
| Could R-L4 adapter limitations contribute? | LIMITATION | Model-, training-, inference-, and adapter-related contributors remain intertwined. |
| Are negative or near-zero cross-context values shown honestly? | RESOLVED | Distribution axis includes zero and preserves the negative K562-to-RPE1 cross-context mean. |
