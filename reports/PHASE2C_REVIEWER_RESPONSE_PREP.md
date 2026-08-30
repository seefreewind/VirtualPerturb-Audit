# Phase 2C Reviewer-Response Preparation

Generated: 2026-08-30 04:12:12 UTC

Task mode: triage-only pre-submission response preparation. Decision type: not applicable because no journal decision letter has been supplied.

## Response Strategy Summary

- Overall posture: evidence-first and bounded. Lead with matched-target STATE evidence, then name endpoint limitations plainly.
- Main risk: overclaiming Phase 2C as full cross-architecture confirmation.
- Best response anchor: matched-target Replogle Pearson drop, supported by Spearman, cosine, and sign-flip direction.
- Package readiness: draft-ready for anticipated reviewer concerns; final response letters require actual reviewer comments and manuscript line numbers.

## Internal Master Tracker (Not Reviewer-Facing)

| ID | Anticipated concern | Type | Severity | Proposed action | Work status | Expected output | Blocks finalization? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P2C.1 | STATE and GEARS are not directly comparable because metric spaces differ. | metric compatibility | major | State that Phase 2C tests directionality within STATE and does not claim absolute GEARS-vs-STATE performance equivalence. | VERIFIED_DONE | `STATE_GEARS_METRIC_COMPATIBILITY.md`; caveat table | no |
| P2C.2 | The R-L4 STATE target set is smaller than R-L1. | target-set composition | major | Lead with matched-target analysis and report full-summary endpoints as mixed. | VERIFIED_DONE | `state_transfer_drop.csv`; `phase2c_state_interpretation` Panel E | no |
| P2C.3 | Retrieval and UER do not uniformly support transfer degradation. | endpoint heterogeneity | major | Describe partial architecture support, not complete confirmation. | VERIFIED_DONE | `PHASE2C_DECISION.md`; interpretation report | no |
| P2C.4 | BNS and UER nulls are not externally verified. | biological-null validity | major | Keep BNS unverified and UER sensitivity-only. | VERIFIED_DONE | endpoint caveat table | no |
| P2C.5 | The second model was previously compute-blocked. | reproducibility | moderate | Preserve compute-blocked Phase 2B rows and append full-GPU performance-eligible Phase 2C rows. | VERIFIED_DONE | `gears_second_model_confirmatory.csv` | no |
| P2C.6 | Large STATE output files are not versioned in git. | reproducibility logistics | moderate | Track manifests, scripts, reports, and figures; keep large h5ad outputs local under ignored `results/state/`. | VERIFIED_DONE | analysis manifest and file manifest | no |

## Draft Response Language

Concern: The cross-context failure may be specific to GEARS.

Response: We addressed this concern by adding an independent STATE audit under the same locked Phase 2C task definitions. The STATE run completed Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4 on a CUDA-capable Linux GPU server. In the Replogle matched-target subset, within-context K562 R-L1 had higher agreement than K562-to-RPE1 R-L4, with a Pearson drop of 0.1163 and a 95% bootstrap interval of [0.0684, 0.1599]. Spearman and cosine showed the same direction, and the sign-flip endpoint worsened in cross-context transfer. We therefore describe the result as partial cross-architecture support rather than complete confirmation.

Concern: STATE uses a different target set from GEARS.

Response: We audited split alignment against the frozen GEARS split files before STATE execution. STATE perturbation labels were normalized by the project convention that collapses explicit control partners, so `ctrl+X` and `X` are evaluated as the same target. The manuscript now reports normalized target counts and uses matched-target Replogle contrasts for the main Phase 2C interpretation.

Concern: Some endpoints do not support the same direction.

Response: We agree and have made this limitation explicit. Full-summary retrieval MRR was higher in STATE R-L4 than STATE R-L1, and UER@50 was slightly lower in the R-L4 full summary. Because these endpoints are affected by target-set composition, the manuscript leads with the matched-target contrast and states that Phase 2C provides bounded, partial support.

## Caveat Table

| issue | status | handling |
| --- | --- | --- |
| Metric space | GEARS Norman frozen rows are raw GEARS-space; STATE primary rows are audit-delta. | Do not make absolute GEARS-vs-STATE performance claims from raw side-by-side values. |
| Normalized targets | STATE collapses explicit control partners, e.g. ctrl+X and X. | Report both frozen condition counts and normalized target counts. |
| R-L4 target set | STATE R-L4 has 73 normalized targets; Replogle K562 R-L1 has 216. | Use matched-target contrast for the strongest context-transfer interpretation. |
| BNS | Bound-normalized score remains unverified. | Keep BNS out of confirmatory claims until replicate-bound nulls are verified. |
| UER null | UER uses median absolute observed delta as an internal null. | Label UER as sensitivity-only. |

## Reviewer-Facing Boundary

Do not write that STATE fully confirms GEARS. The stronger and defensible sentence is: STATE partially reproduces the Replogle context-transfer degradation on matched targets, supporting an architecture-independent component of the transfer failure while leaving endpoint-specific caveats.
