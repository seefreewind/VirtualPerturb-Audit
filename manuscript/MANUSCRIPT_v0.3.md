# Auditing Context-Transfer Failure in Perturbation-Response Models

Draft version: v0.3

Generated: 2026-08-30 04:12:12 UTC

## Abstract

Perturbation-response models are often evaluated by global transcriptomic similarity, but high global agreement can mask failures in perturbation-specific generalization. We built VirtualPerturb-Audit to separate global fit, target retrieval, unsupported-effect behavior, leakage risk, and cross-context transfer. In GEARS analyses, cross-context Replogle transfer showed strong degradation after matched-target restriction. Phase 2C added a full GPU STATE audit as an independent deep-architecture check. STATE partially reproduced the context-transfer phenotype on matched Replogle targets, with a Pearson drop of 0.1163 and endpoint-specific caveats. These results support an audit framing in which perturbation models are evaluated by robustness and failure modes rather than by a single leaderboard metric.

## Introduction

Single-cell perturbation models aim to predict transcriptional responses to genetic or molecular interventions. Their usefulness depends on whether they recover perturbation-specific structure under conditions that were not directly observed during training. Standard aggregate metrics can report strong agreement even when a model fails to identify the correct perturbation, predicts unsupported high-magnitude effects, or transfers poorly across cellular contexts.

VirtualPerturb-Audit was designed as a stress-test framework for these failure modes. The framework combines strict split definitions, perturbation-level evaluation, retrieval-based specificity, unsupported-effect metrics, leakage checks, and cross-context transfer tests. The central claim is not that one model is universally best. The central claim is that model behavior changes when the evaluation target shifts from global expression similarity to perturbation-specific and context-transfer reliability.

This draft reports the current Norman and Replogle GEARS audit together with the Phase 2C STATE confirmatory analysis. GEARS provides the primary audit trajectory, including matched-target Replogle stress tests. STATE provides an independent deep-architecture check of whether the Replogle transfer phenotype is specific to GEARS.

## Methods

### Data Scope and Split Policy

The audit used Norman perturbation splits and GEARS-compatible filtered Replogle essential-screen data. Frozen GEARS split files and Phase 2A/2B primary metrics were treated as immutable inputs during Phase 2C. Replogle analyses used within-context R-L1 tasks and cross-context R-L4 tasks. The K562-to-RPE1 direction was the main Phase 2C transfer direction for STATE.

### Metrics

For each perturbation target, predicted and observed expression profiles were converted to delta vectors by subtracting an appropriate control mean. The audit reported delta-Pearson, Spearman, RMSE, cosine similarity, retrieval Top1/Top5/MRR, UER@20/50/100, and sign-flip rate. Perturbation-level bootstrap intervals used 2,000 resamples. BNS remained unverified, and UER was interpreted as sensitivity-only.

### Matched-Target Transfer Sensitivity

The GEARS matched-target sensitivity analysis restricted each transfer direction to perturbation targets shared between the source-context within split and the cross-context evaluation split. This design separates transfer degradation from target-composition effects. Common-candidate retrieval further restricted the retrieval candidate pool to the same matched target set.

### STATE Phase 2C Audit

STATE was evaluated as a second deep architecture after the local CPU path was classified as not performance-eligible. Full STATE training and prediction were completed on a CUDA-capable Linux GPU server. Four locked tasks were evaluated: Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4. STATE perturbation labels were normalized by collapsing explicit control partners, so `ctrl+X` and `X` were evaluated as target `X`.

## Results

### GEARS Cross-Context Transfer Failed After Matched-Target Restriction

In GEARS, matched-target restriction did not rescue Replogle cross-context transfer. In K562-to-RPE1, matched-source Pearson fell from 0.2812 within context to -0.0070 cross context. The paired drop was 0.2883 with a 95% interval of [0.2559, 0.3206]. UER50 increased from 0.1532 to 0.3877, and sign-flip rate increased from 0.2714 to 0.5718.

The reverse RPE1-to-K562 direction showed the same pattern. Pearson fell from 0.5501 to 0.0021, with a paired drop of 0.5480 and a 95% interval of [0.5146, 0.5802]. UER50 and sign-flip penalties increased in the cross-context setting.

### STATE Partially Reproduced the Transfer Phenotype

The full GPU STATE audit completed all four locked tasks. STATE achieved delta-Pearson values of 0.4445 for Norman L1, 0.4060 for Norman L2, 0.2639 for Replogle K562 R-L1, and 0.1874 for Replogle K562-to-RPE1 R-L4.

Matched-target Replogle analysis gave the clearest Phase 2C signal. Across 15 shared targets, Pearson fell from 0.2955 in K562 R-L1 to 0.1792 in K562-to-RPE1 R-L4, a mean drop of 0.1163 with a 95% bootstrap interval of [0.0684, 0.1599]. Spearman and cosine similarity also decreased. UER50 and sign-flip rate moved in the worse cross-context direction, although UER50 had a bootstrap interval crossing zero.

### Endpoint Heterogeneity Limits the Claim

The Phase 2C result is not a complete confirmation. In the full-summary table, STATE R-L4 had higher retrieval MRR and slightly lower UER50 than STATE R-L1. These mixed endpoints are interpreted in the context of target-set differences, because STATE R-L4 contained 73 normalized targets compared with 216 targets in STATE Replogle K562 R-L1. The strongest defensible result is therefore matched-target, partial cross-architecture support.

## Discussion

The audit shows that perturbation-response model evaluation depends strongly on the endpoint being tested. GEARS showed high raw global agreement in some settings, but Replogle audit-delta and retrieval endpoints exposed weak perturbation-specific transfer. The matched-target analysis strengthened this interpretation by showing that cross-context degradation persisted after target-composition restriction.

STATE adds an important architecture check. Its matched-target Replogle results reproduce the direction of context-transfer degradation, which argues against a GEARS-only artifact. At the same time, STATE does not produce a uniform endpoint-level confirmation. This mixed pattern is useful rather than disappointing, because it identifies which claims are robust and which require narrower wording.

The present evidence supports an audit-framework claim. VirtualPerturb-Audit can reveal discrepancies between global fit, perturbation specificity, unsupported-effect behavior, and context transfer. It should not yet be framed as a final leaderboard or as a complete biological validation system. BNS remains unverified, and UER currently uses an internal sensitivity null.

## Current Figure and Table Package

Main Phase 2C figure: `figures/main/phase2c_state_interpretation.pdf`.

Supplementary Phase 2C figures:

- `figures/supplementary/phase2c_endpoint_heatmap.pdf`
- `figures/supplementary/phase2c_retrieval_rank_distribution.pdf`

Core tables:

| setting | split | metric_space | n_test_perturbations | pearson_delta | retrieval_mrr | uer50 | sign_flip_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Norman L1 STATE | L1 | audit_delta | 53 | 0.4445 | 0.0757 | 0.0015 | 0.2536 |
| Norman L2 STATE | L2 | audit_delta | 28 | 0.4060 | 0.1377 | 0.0000 | 0.2517 |
| Replogle K562 R-L1 STATE | R-L1-K562 | audit_delta | 216 | 0.2639 | 0.0262 | 0.1577 | 0.2882 |
| Replogle K562 -> RPE1 R-L4 STATE | R-L4-K2R | target_control_audit_delta | 73 | 0.1874 | 0.0668 | 0.1403 | 0.2990 |

## Limitations

The current draft uses GEARS-compatible filtered Replogle data rather than the complete unavailable Figshare+ processed objects. BNS remains unverified. UER is sensitivity-only. STATE and GEARS absolute values should not be interpreted as a direct performance ranking when their metric spaces differ. Phase 2C supports a bounded cross-architecture transfer-degradation claim, not a complete confirmation across all endpoints.
