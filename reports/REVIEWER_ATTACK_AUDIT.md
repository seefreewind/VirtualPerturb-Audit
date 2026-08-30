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

## Attack 8: The context-transfer phenotype is specific to GEARS.

Response: Phase 2C adds a performance-eligible STATE GPU audit over Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4. STATE partially reproduces the context-transfer drop on matched Replogle targets, supporting an architecture-independent signal. The response should remain bounded because full-summary retrieval and UER endpoints are mixed, BNS remains unverified, and the R-L4 target set is smaller than the R-L1 target set.

## Attack 9: STATE and GEARS used incompatible target definitions.

Response: Split alignment was audited against frozen GEARS split files before STATE execution. STATE target labels were normalized with the project convention that collapses explicit control partners, so `ctrl+X` and `X` are evaluated as the same perturbation target. Reports therefore state both frozen-condition counts and normalized target counts, and the Norman GEARS rows are clearly marked as raw GEARS-space rather than audit-delta equivalents.
