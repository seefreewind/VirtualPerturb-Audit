# RESULTS v0.1

## Matched-Target Sensitivity

Matched-target restriction did not rescue cross-context transfer. In the K562-to-RPE1 direction, matched-source Pearson fell from 0.2812 within context to -0.0070 cross context, a paired drop of 0.2883 with a 95% interval of [0.2559, 0.3206]. UER50 increased from 0.1532 to 0.3877, and the sign-flip rate increased from 0.2714 to 0.5718.

The reverse RPE1-to-K562 direction showed the same pattern. Matched-source Pearson fell from 0.5501 to 0.0021, a paired drop of 0.5480 with a 95% interval of [0.5146, 0.5802]. UER50 increased from 0.0695 to 0.4655, and the sign-flip rate increased from 0.1207 to 0.4951.

Common-candidate retrieval stayed low. Its MRR drop was directionally consistent but did not provide the strongest statistical evidence because the bootstrap interval crossed zero in the source-context matched comparison. The strongest evidence for transfer collapse came from delta correlation, UER50, and sign-flip penalties.

## Second-Model Audit

No performance-eligible second deep architecture was completed locally. scGPT failed the local fair-execution gate. STATE passed official CLI and one-step smoke tests, including a `state_sm` deep-model smoke, but full deep runs were blocked by CPU-only execution and expected multi-week runtime for the four-task matrix. Phase 2B therefore supports a conditional manuscript path based on the matched-target GEARS stress test, with second-architecture confirmation deferred to a GPU/Linux execution environment.
