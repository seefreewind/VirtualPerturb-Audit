# Reviewer Attack Audit

## Attack 1: Hallucination is measurement noise.

Response: The planned definition uses replicate-derived or control-derived null envelopes and reports uncertainty.

## Attack 2: A nonsignificant DEG does not mean absence.

Response: Unsupported effects are defined by effect size relative to empirical null envelopes, not by p-value nonsignificance alone.

## Attack 3: Leakage is just legal pretraining.

Response: The audit separates documented overlap, possible contamination, contamination risk, and evaluation leakage.

## Attack 4: Complex models were not tuned fairly.

Response: Official configs and a documented tuning budget are required before comparison.

## Attack 5: Different models use different inputs.

Response: An information access matrix will be generated for every included model.

## Attack 6: Temporal clean is not truly clean.

Response: The manuscript will use "temporally eligible clean candidate" unless exact corpus exclusion is documented.

## Attack 7: Results are metric-dependent.

Response: The framework uses multiple metrics, empirical bounds, perturbation-level bootstrap, and ranking-instability analysis.

