# Figure 3 v2 Reviewer Attack Test

| Criticism | Status | Response |
|---|---:|---|
| Is `shuffled` defined clearly? | RESOLVED | Display label is `Label-shuffled`; legend defines it as scrambled perturbation labels. |
| Does mean-effect use target information indirectly? | PARTIAL | It is target-blind at prediction time but estimated from training target deltas; this is stated as a response-structure probe/baseline. |
| Are retrieval candidate universes comparable within context? | LIMITATION | Probe and GEARS rows have nearly identical but not identical normalized target universes; the differences are recorded in the registry. |
| Is random MRR available? | RESOLVED | HN/N is calculated from the frozen candidate counts and displayed as a gray reference marker. |
| Are we claiming superiority without formal tests? | RESOLVED | No significance stars or superiority claims are used. |
| Are probe values interpreted as mechanistic evidence? | RESOLVED | Legend frames probes as diagnostic stress tests, not biological models. |
| Does Panel A accidentally look like raw-space Pearson? | RESOLVED | Panel subtitle and x-axis explicitly state `Audit-delta Pearson`. |
