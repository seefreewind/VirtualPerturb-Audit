# Figure 5 Numeric Audit

All hard-freeze values matched the frozen tables before plotting.

| endpoint            | endpoint_family                           | raw_difference_definition                                           |   raw_difference |   display_difference |   ci_low_display |   ci_high_display | primary_or_sensitivity   |
|:--------------------|:------------------------------------------|:--------------------------------------------------------------------|-----------------:|---------------------:|-----------------:|------------------:|:-------------------------|
| Audit-delta Pearson | Response agreement                        | within minus cross                                                  |        0.116287  |            0.116287  |        0.0683662 |          0.159907 | primary                  |
| Spearman agreement  | Response agreement                        | within minus cross                                                  |        0.0708753 |            0.0708753 |        0.0260522 |          0.111028 | primary                  |
| Cosine agreement    | Response agreement                        | within minus cross                                                  |        0.104786  |            0.104786  |        0.0528661 |          0.153293 | primary                  |
| Sign-flip rate      | Directional / unsupported-effect behavior | source minus cross in frozen table; display uses cross minus within |       -0.0557333 |            0.0557333 |        0.0103933 |          0.1      | sensitivity              |
| UER50†              | Directional / unsupported-effect behavior | source minus cross in frozen table; display uses cross minus within |       -0.028     |            0.028     |       -0.0106667 |          0.064    | sensitivity              |

## Common-candidate retrieval

- Within K562 MRR: 0.259417989418
- Cross to RPE1 MRR: 0.221215266215
- Candidate universe: n = 15
- Random-ranking expectation: 0.221215266215
