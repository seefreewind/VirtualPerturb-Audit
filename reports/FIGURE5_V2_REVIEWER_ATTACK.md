# Figure 5 v2 Reviewer Attack Test

| Risk | Assessment | Status |
|---|---|---|
| A. Does sign harmonization alter underlying statistics? | The frozen table is unmodified; harmonization is exported only in `figure5_direction_aligned_effects.tsv`. | RESOLVED |
| B. Are burden endpoints correctly sign-flipped only for display? | UER50 and sign-flip use cross-minus-within for display, while the raw source-minus-cross values remain recorded. | RESOLVED |
| C. Is UER overinterpreted? | UER50 is marked as an internal sensitivity endpoint and its interval crossing zero is visible. | RESOLVED |
| D. Does n=15 support architecture-general claims? | The figure and legend state partial support, not architecture-level generality. | LIMITATION |
| E. Could one target drive results? | LOO agreement endpoints are 15/15 positive; this mitigates but does not replace larger validation. | PARTIAL |
| F. Is common-candidate MRR appropriately labeled exploratory? | Panel B and legend label it exploratory. | RESOLVED |
| G. Are candidate universes identical in Panel B? | Both rows use the same 15 perturbation candidates. | RESOLVED |
| H. Is MRR being compared fairly? | Panel B avoids CIs and p-values because no frozen valid MRR CI exists. | RESOLVED |
| I. Does Figure 5 overstate consistency across endpoints? | The figure keeps UER uncertainty and weaker MRR visible. | RESOLVED |

Overall: MINOR_RISK
