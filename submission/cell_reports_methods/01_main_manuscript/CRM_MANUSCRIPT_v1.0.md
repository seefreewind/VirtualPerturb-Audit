# VirtualPerturb-Audit: a falsification framework for perturbation-response model evaluation

Draft version: CRM_MANUSCRIPT_v1.0

Generated: 2026-08-30 07:13:25 UTC

## Author Information

Authors: [To be completed]

Affiliations: [To be completed]

Correspondence: [To be completed]

## Summary

Perturbation-response models are commonly evaluated by aggregate transcriptomic similarity, but this can obscure whether a model identifies the correct perturbation, avoids unsupported effects, and transfers across cellular contexts. We developed VirtualPerturb-Audit as a falsification framework that separates global fit, perturbation-level retrieval, unsupported-effect behavior, sign-flip burden, leakage risk, and matched-target transfer. In frozen GEARS analyses, matched Replogle K562-to-RPE1 transfer fell from Pearson 0.2812 within context to -0.0070 cross context, with a paired drop of 0.2883. A second-architecture STATE audit partially reproduced this transfer phenotype on matched targets, with Pearson decreasing by 0.1163. These results support VirtualPerturb-Audit as a reusable method for stress-testing perturbation-response claims rather than a direct model leaderboard.

## Introduction

Single-cell perturbation screens create a direct setting for testing whether computational models can predict cellular responses to genetic or chemical interventions. A model that performs well in this setting should do more than reproduce the average shape of a transcriptional response. It should preserve perturbation identity, avoid high-confidence unsupported effects, remain robust under split changes, and expose when its predictions stop transferring across cellular contexts.

Many current evaluations still compress model behavior into global similarity metrics. These metrics are useful but incomplete. A prediction can be globally close to the observed expression profile while ranking the wrong perturbation, borrowing strength from mean-effect structure, or degrading sharply when the same perturbation must be inferred in another cellular context. Virtual perturbation models therefore need evaluation frameworks that make failure modes visible before claims move from benchmark performance to biological use.

VirtualPerturb-Audit was designed for this purpose. The framework freezes split definitions and result tables, evaluates perturbation-level outputs across complementary endpoint families, introduces falsification probes, and uses matched-target sensitivity analyses to separate target-composition effects from context-transfer degradation. The method treats evaluation as an audit of claim robustness. It asks which statements survive stricter endpoint definitions and which must be narrowed.

We apply the framework to Norman and GEARS-compatible filtered Replogle perturbation data. GEARS provides the primary worked example across within-context and cross-context settings. STATE provides a second deep-architecture check after full GPU execution became available. The manuscript uses these analyses to demonstrate the framework and its reporting discipline. It does not claim that GEARS and STATE absolute metrics define a universal ranking, because their metric spaces, target universes, and adapter requirements differ.

## Results

### VirtualPerturb-Audit separates model fit into falsifiable endpoint families

VirtualPerturb-Audit organizes perturbation-response evaluation into four linked stages (Figure 1). Frozen inputs define datasets, splits, model outputs, and permitted post-processing. Metric families then separate global transcriptional agreement from perturbation-specific retrieval, unsupported-effect rate, and sign-flip burden. Stress tests ask whether the same conclusion survives matched targets, cross-context inference, and simple probe controls. The final output is a bounded claim with explicit evidence and limitation status.

This structure is intended to prevent a single strong endpoint from carrying claims that it does not support. For example, a high Pearson correlation can support global response similarity, but it does not by itself establish perturbation identity recovery. A low unsupported-effect rate can support one aspect of stability, but it cannot validate biological realism when the null is sensitivity-only. The audit therefore reports endpoint families together and labels unresolved assumptions.

### Norman and Replogle expose divergence between global agreement and target retrieval

In the frozen GEARS comparison, Norman and Replogle showed different behavior when global agreement and perturbation specificity were viewed together (Figure 2). Norman L1 GEARS had raw-space Pearson 0.9887 and MRR 0.3277. Replogle K562 R-L1 retained high raw-space Pearson 0.9851 but had MRR 0.0445. Replogle RPE1 R-L1 had raw-space Pearson 0.9709 and MRR 0.0209.

This divergence shows why the framework reports target retrieval alongside aggregate expression agreement. The Replogle analyses used GEARS-compatible filtered essential-screen data, not the complete Figshare+ processed objects, so the result is framed as filtered-data evidence. Within that scope, the audit shows that global similarity can remain high while perturbation-specific retrieval becomes weak.

### Within-context Replogle tests show why probe controls are needed

The within-context Replogle audit compared GEARS against simple probes and baselines (Figure 3). The point of this analysis is not to demote a deep model because a simple mean-effect estimate can be strong on a global endpoint. It is to identify which part of the signal is perturbation-specific. In K562 and RPE1, mean-effect probes achieved strong audit-delta Pearson while retrieval remained low. GEARS improved some retrieval endpoints, but the absolute retrieval values remained modest.

These findings support a methods claim: perturbation-response evaluation should include falsification probes that reveal when a model is capturing shared response structure rather than target-specific signal. Probe controls also make manuscript wording more precise, because they separate a statement about global expression fit from a statement about perturbation identification.

### Matched-target GEARS analysis supports cross-context transfer collapse

The strongest GEARS transfer result comes from matched-target sensitivity analysis (Figure 4). In K562-to-RPE1, matched-source Pearson decreased from 0.2812 within context to -0.0070 cross context. The paired difference was 0.2883, with a 95% interval of [0.2559, 0.3206]. UER50 increased from 0.1532 to 0.3877, and sign-flip rate increased from 0.2714 to 0.5718.

The reverse RPE1-to-K562 direction gave the same conclusion. Matched-source Pearson decreased from 0.5501 to 0.0021, with a paired drop of 0.5480 and a 95% interval of [0.5146, 0.5802]. This matched-target design reduces the possibility that transfer degradation is explained only by different test-target composition. The supported conclusion is `MATCHED_SUPPORTS_TRANSFER_COLLAPSE`.

### STATE provides partial cross-architecture support, with endpoint-level caveats

Phase 2C evaluated STATE as an independent deep architecture on four locked tasks. STATE achieved audit-delta Pearson 0.4445 for Norman L1, 0.4060 for Norman L2, 0.2639 for Replogle K562 R-L1, and 0.1874 for Replogle K562-to-RPE1 R-L4 (Figure 5).

Matched Replogle STATE targets gave the clearest cross-architecture signal. Across 15 shared targets, Pearson decreased from 0.2955 within context to 0.1792 cross context. The mean drop was 0.1163, with a 95% interval of [0.0684, 0.1599]. Spearman and cosine moved in the same direction. UER50 and sign-flip rate also moved toward worse cross-context behavior on matched targets, although the UER50 interval crossed zero.

The STATE result is partial rather than uniform. In full-summary comparisons, STATE R-L4 had higher retrieval MRR and slightly lower UER50 than STATE R-L1, partly reflecting a smaller normalized R-L4 target universe. We therefore state the Phase 2C conclusion as partial cross-architecture support for matched-target transfer degradation, not as a universal claim that all endpoints or all model architectures fail.

## Discussion

VirtualPerturb-Audit reframes perturbation-response evaluation as a claim-stress problem. The framework asks whether a model conclusion remains true when the endpoint changes from global expression agreement to perturbation-specific retrieval, unsupported-effect burden, sign direction, leakage risk, or cross-context transfer. This approach gives editors and reviewers a transparent way to see which claims are supported and which claims depend on a narrow metric choice.

The GEARS worked example illustrates the value of this framing. Raw global agreement remains high in several settings, but target retrieval and matched transfer tell a different story. The matched Replogle analysis is especially informative because it preserves the target set while changing the context-transfer condition. The resulting Pearson drops in both transfer directions are large and have intervals that do not approach zero.

The STATE analysis strengthens but also narrows the interpretation. It shows that the Replogle transfer-drop direction is not confined to one GEARS run, while its mixed endpoint profile prevents a broad architecture-independent failure claim. This is exactly the reporting behavior the audit is meant to enforce: a result can be supportive and still demand narrower language.

Several limitations are permanent in the current submission package. Replogle analyses use GEARS-compatible filtered essential-screen data rather than the complete Figshare+ processed objects. BNS remains unverified, so UER is sensitivity-only. The GEARS R-L4 workflow is a GEARS-compatible cross-context inference adapter using source-context training, target-context control basal inputs, and target-context evaluation; it is not a native cell-line-aware GEARS split. STATE support is partial and not uniform across endpoints. GEARS and STATE absolute metric values should not be treated as a direct leaderboard where metric spaces and target universes differ.

The resulting manuscript is therefore a methods submission, not a model competition. The contribution is a reusable audit structure, a transparent evidence matrix, and a disciplined way to report perturbation-model robustness. Future work should apply the framework to complete Replogle processed objects, verified replicate-derived nulls, additional architectures, and prospective perturbation settings.

## STAR Methods

### Resource availability

#### Lead contact

Lead contact information will be supplied by the corresponding author before submission.

#### Materials availability

This computational study did not generate new physical reagents.

#### Data and code availability

The audit used public Norman perturbation data and GEARS-compatible filtered Replogle essential-screen data. The complete Figshare+ processed Replogle objects were not used in the current frozen analyses. Code-release status, environment gaps, and deposit requirements are audited in `reports/CRM_CODE_RELEASE_AUDIT.md` and `reports/CODE_RELEASE_GATE.md`.

### Method details

#### Audit design

VirtualPerturb-Audit begins by freezing datasets, split definitions, model outputs, and post-processing rules. All subsequent analyses operate on saved result objects or tabular summaries. The framework reports complementary endpoint families rather than optimizing a single scalar score.

#### Datasets and task levels

Norman analyses used frozen GEARS-compatible Norman perturbation splits. Replogle analyses used GEARS-compatible filtered essential-screen data for K562 and RPE1. R-L1 denotes within-context training and evaluation. R-L4 denotes source-context training with target-context control basal inputs and target-context evaluation through a GEARS-compatible cross-context inference adapter.

#### Endpoint definitions

Delta-expression metrics were computed after subtracting the appropriate control mean. The audit reports Pearson, Spearman, RMSE, cosine similarity, retrieval Top1/Top5/MRR, UER@20/50/100, and sign-flip rate where available. UER remains a sensitivity-only endpoint because BNS is unverified.

#### Matched-target sensitivity

Matched-target sensitivity restricts paired comparisons to perturbation targets shared between within-context and cross-context outputs. This analysis separates transfer degradation from target-composition changes. Bootstrap intervals use perturbation-level resampling as reported in frozen result tables.

#### STATE Phase 2C audit

STATE was evaluated after GPU/Linux execution became available. Four locked tasks were run: Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4. STATE perturbation labels were normalized by collapsing explicit control partners before target-level evaluation.

### Quantification and statistical analysis

Perturbation-level bootstrap intervals are taken from frozen result tables. Matched GEARS transfer uses paired target-level differences. STATE matched-target transfer uses perturbation-level bootstrap intervals over shared targets. No additional model training or new benchmark reruns were performed during CRM manuscript preparation.

## References

Reference metadata and verification status are listed in `reports/REFERENCE_AUDIT.md`. The working reference set includes Norman et al. Science 2019, Replogle et al. Cell 2022, Roohani et al. Nature Biotechnology 2024, PerturBench, Systema, scArchon, VCBench, and related virtual-cell benchmarking work. Items without fully verified bibliographic metadata are flagged for manual reference-manager confirmation before journal upload.

## Figure Legends

**Figure 1. VirtualPerturb-Audit framework.** Frozen inputs are evaluated through complementary metric families, stress-tested under matched targets and cross-context conditions, and translated into bounded claims.

**Figure 2. Global agreement and perturbation-specific retrieval can diverge.** Frozen GEARS results show high raw-space Pearson across Norman and Replogle settings, while retrieval MRR drops in Replogle.

**Figure 3. Within-context Replogle probe controls.** Mean-effect and shuffled probes help distinguish global response structure from perturbation-specific retrieval.

**Figure 4. Matched-target GEARS cross-context transfer.** Shared-target restriction preserves large Pearson drops in both K562-to-RPE1 and RPE1-to-K562 transfer directions.

**Figure 5. STATE partial cross-architecture confirmation.** Matched Replogle STATE targets show lower cross-context agreement, while endpoint-level caveats remain visible.
