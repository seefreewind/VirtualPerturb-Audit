# VirtualPerturb-Audit: a falsification framework for perturbation-response model evaluation

Draft version: CRM_MANUSCRIPT_v1.1

Generated: 2026-08-30 14:05:25 UTC

## Author Information

Authors: Da Lin1, Ying Chen2, Yue Liu2, Yu Zhang1

Affiliations: 1 Department of Ophthalmology, The Second Affiliated Hospital of Wenzhou Medical University, No. 109 Xueyuan West Road, Lucheng District, Wenzhou, Zhejiang Province, China

2 Wenzhou Medical University, Wenzhou, Zhejiang Province, China

Correspondence: Yu Zhang, zhangyu1@wzhealth.com; ORCID: 0000-0001-8579-3692

## Summary

Perturbation-response models are often judged by aggregate transcriptomic similarity, but this endpoint can miss perturbation-specific and context-shifted failures. VirtualPerturb-Audit is a falsification framework that freezes analysis inputs and evaluates global fit, target retrieval, unsupported-effect behavior, sign-flip rate, leakage risk, and matched-target transfer. In GEARS applied to GEARS-compatible filtered Replogle data, matched K562-to-RPE1 audit-delta Pearson decreased by 0.2883. In STATE, a second deep architecture, the matched K562-to-RPE1 audit-delta Pearson drop was 0.1163. The central contribution is not a new perturbation predictor, but a reusable framework for testing which aspects of apparent predictive performance survive perturbation-specific and context-shifted stress testing.

## Introduction

Single-cell perturbation screens connect experimental intervention with transcriptome-scale phenotypes, making them a natural testbed for perturbation-response prediction. Norman et al. established rich single-cell genetic-interaction phenotypes, and Replogle et al. extended Perturb-seq to genome-scale CRISPRi maps across millions of cells [1,2]. Models such as GEARS use these data to predict responses to unseen perturbations [3].

Aggregate similarity is useful but incomplete. A model can achieve high raw-space transcriptomic similarity while recovering little perturbation identity, especially when shared mean-response structure dominates the signal. Recent benchmarks have sharpened this concern by showing that model rankings and conclusions depend on metric choice, task design, and systematic variation [4-8].

Existing benchmark resources help standardize datasets, baselines, and model comparisons [4-8]. What remains fragmented is the link between a reported number and the claim it is allowed to support. Raw-space transcriptomic similarity and control-subtracted audit-delta agreement quantify different properties and should not be interpreted as numerically interchangeable endpoints.

VirtualPerturb-Audit addresses this gap by treating evaluation as falsification. It freezes inputs, separates endpoint families, adds probe controls, runs matched-target context-transfer stress tests, and records claim boundaries. We demonstrate the framework with frozen GEARS and STATE analyses on Norman and GEARS-compatible filtered Replogle data.

## Results

### VirtualPerturb-Audit separates model fit into falsifiable endpoint families

VirtualPerturb-Audit organizes perturbation-response evaluation into frozen inputs, metric families, stress tests, and bounded claims (Figure 1). Frozen inputs define datasets, split assignments, model outputs, and permitted post-processing. Metric families separate raw-space global transcriptomic similarity, audit-delta agreement, perturbation-specific retrieval, unsupported-effect rate, and sign-flip rate. Stress tests then ask whether a claim survives probe controls, matched targets, and cross-context transfer.

This design prevents one strong endpoint from carrying unsupported claims. Raw-space Pearson can support global expression agreement, but it does not establish perturbation identity recovery. Unsupported-effect rate can support sensitivity to large unsupported predictions, but it is not a validated biological endpoint unless its null envelope is derived from validated biological replicate ground truth.

### Norman and Replogle expose divergence between global agreement and target retrieval

Frozen GEARS results showed that raw-space global similarity and perturbation-specific retrieval can diverge (Figure 2). Norman L1 GEARS had raw-space Pearson 0.9887 and MRR 0.3277. Replogle K562 R-L1 retained raw-space Pearson 0.9851 but had MRR 0.0445. Replogle RPE1 R-L1 had raw-space Pearson 0.9709 and MRR 0.0209.

These values are not directly comparable to audit-delta Pearson values used in later transfer sections. Raw-space Pearson measures agreement in the expression space used by the GEARS evaluation row. Audit-delta Pearson measures agreement after control subtraction and is used to compare perturbation-specific response patterns.

### Within-context Replogle tests show why probe controls are needed

The within-context Replogle audit compared GEARS with simple probes and baselines (Figure 3). Mean-effect probes achieved strong audit-delta Pearson in K562 and RPE1, while retrieval remained low. GEARS improved some retrieval endpoints, but absolute retrieval values stayed modest.

Probe controls clarify what kind of signal drives an apparent success. In this setting, they separate global response structure from perturbation-specific target recovery. The result supports an audit-framework claim rather than a broad claim about model superiority or failure.

### Matched-target GEARS analysis supports cross-context transfer collapse

Matched-target GEARS analysis provides the strongest quantitative result (Figure 4). In K562-to-RPE1 transfer, audit-delta Pearson decreased from 0.2812 within context to -0.0070 cross context. The paired drop was 0.2883, with a 95% interval of [0.2559, 0.3206]. UER50 increased from 0.1532 to 0.3877, and sign-flip rate increased from 0.2714 to 0.5718.

The reverse RPE1-to-K562 direction showed the same pattern. Audit-delta Pearson decreased from 0.5501 to 0.0021, with a paired drop of 0.5480 and a 95% interval of [0.5146, 0.5802]. The matched-target design reduces target-composition confounding, but it does not eliminate every possible confounder. The supported conclusion is `MATCHED_SUPPORTS_TRANSFER_COLLAPSE`.

### STATE provides partial cross-architecture support, with endpoint-level caveats

Phase 2C evaluated STATE as a second deep architecture on four locked tasks. STATE achieved audit-delta Pearson 0.4445 for Norman L1, 0.4060 for Norman L2, 0.2639 for Replogle K562 R-L1, and 0.1874 for Replogle K562-to-RPE1 R-L4.

Matched STATE targets gave partial cross-architecture support for the transfer-degradation signal (Figure 5). Across 15 shared targets, audit-delta Pearson decreased from 0.2955 within context to 0.1792 cross context. The mean drop was 0.1163, with a 95% interval of [0.0684, 0.1599]. Spearman and cosine moved in the same direction, and sign-flip rate was worse cross context. UER50 had a worse point estimate, but its interval crossed zero.

STATE did not provide a uniform endpoint-level confirmation. In full-summary comparisons, STATE R-L4 had higher retrieval MRR and slightly lower UER50 than STATE R-L1, in a smaller normalized R-L4 target universe. STATE therefore provided partial cross-architecture support for matched-target transfer degradation, with endpoint-level heterogeneity that limits broader generalization.

## Discussion

VirtualPerturb-Audit contributes a reusable audit grammar for perturbation-response model evaluation. It links each reported endpoint to the claim it can support, then records where the claim narrows under stricter stress tests.

The GEARS worked example shows why this grammar matters. Raw-space global similarity remained high in several settings, while perturbation-specific retrieval and matched transfer revealed weaker behavior. The matched Replogle analysis is the clearest stress test because it compares the same target set across within-context and cross-context conditions.

The STATE analysis adds a second-architecture check without overstating the evidence. It supports the matched-target transfer-drop direction but also shows endpoint heterogeneity. This mixed result strengthens the methods argument because the framework exposes both supportive and limiting evidence.

Practically, perturbation-response studies should report raw-space similarity, audit-delta agreement, retrieval, unsupported-effect rate, sign-flip rate, and context-transfer analyses as distinct endpoints. They should also state the target universe and metric space for every comparison.

The current package stops at a bounded methods claim. It does not establish a universal model ranking, validated biological UER endpoint, or architecture-independent failure. Future work should apply the same audit protocol to complete Replogle processed objects, validated replicate-derived nulls, more architectures, and prospective perturbation settings.

## Limitations of the study

Replogle analyses use GEARS-compatible filtered essential-screen data, not the complete Figshare+ processed objects. Validated biological replicate metadata were unavailable, so BNS remains unverified. UER is interpreted as sensitivity-only because its null envelope is not derived from validated biological replicate ground truth. GEARS R-L4 uses a GEARS-compatible cross-context inference adapter, not a native cell-line-aware GEARS split. The worked example includes two architectures, and STATE matched transfer has 15 shared targets. STATE support is endpoint-heterogeneous. The manuscript does not make a direct universal model-ranking claim.

## STAR Methods

### Resource availability

#### Lead contact

Lead contact information will be supplied by the corresponding author before submission.

#### Materials availability

This computational study did not generate new physical reagents.

#### Data and code availability

Original datasets: Norman perturbation data were used through a GEARS-compatible processed mirror [1,3]. Replogle data were used as GEARS-compatible filtered essential-screen K562 and RPE1 objects; complete Figshare+ processed objects were not part of the frozen analyses [2,9,10].

Processed and derived audit files: frozen result tables are stored under `results/tables/`. Split assignments are stored under the project split and metadata outputs listed in `REPRODUCIBILITY.md`. Predictions and target-level outputs are stored in local frozen result directories and require repository/archive deposition before journal upload (`TODO_DEPOSIT`).

Source code and environment: source code is in the VirtualPerturb-Audit repository. Public repository URL, archive DOI, and final environment export remain `TODO_DEPOSIT`. The repository uses an MIT license in this finalization package.

### Method details

#### Audit design

VirtualPerturb-Audit freezes datasets, split definitions, model outputs, and post-processing rules before manuscript interpretation. All CRM v1.1 materials were generated from saved result tables and reports. No new GEARS training, STATE training, primary endpoint redefinition, or matched-target registry change was performed.

#### Datasets and task levels

Norman analyses used frozen GEARS-compatible Norman perturbation splits. Replogle analyses used GEARS-compatible filtered essential-screen data for K562 and RPE1. R-L1 denotes within-context perturbation holdout. R-L4 denotes source-context training with target-context control basal inputs and target-context evaluation through a GEARS-compatible cross-context inference adapter.

#### Endpoint definitions

Raw-space Pearson measures global transcriptomic similarity in the expression space of the relevant model output. Audit-delta Pearson measures control-subtracted perturbation-response agreement. Retrieval endpoints include Top1, Top5, and MRR. Unsupported-effect rate is reported as UER@K. BNS remains unverified because validated biological replicate metadata were unavailable.

#### Matched-target sensitivity

Matched-target analysis restricts paired comparisons to perturbation targets shared between within-context and cross-context outputs. GEARS matched transfer uses paired perturbation-level differences. STATE matched transfer uses bootstrap intervals over shared targets.

#### STATE Phase 2C audit

STATE was evaluated on a CUDA-capable Linux GPU server after local CPU execution was classified as not performance-eligible. Locked tasks were Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4. STATE perturbation labels were normalized by collapsing explicit control partners before target-level evaluation.

### Quantification and statistical analysis

Bootstrap confidence intervals use perturbation-level resampling as reported in frozen result tables. GEARS K562-to-RPE1 and RPE1-to-K562 transfer analyses use matched-target paired differences. STATE K562-to-RPE1 transfer uses 15 matched targets. No new primary analyses were computed during manuscript finalization.

## References

1. Norman, T. M., Horlbeck, M. A., Replogle, J. M., Ge, A. Y., Xu, A., Jost, M., Gilbert, L. A., and Weissman, J. S. Exploring genetic interaction manifolds constructed from rich single-cell phenotypes. *Science* 365, 786-793 (2019). https://doi.org/10.1126/science.aax4438. PubMed: 31395745.
2. Replogle, J. M. et al. Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq. *Cell* 185, 2559-2575.e28 (2022). https://doi.org/10.1016/j.cell.2022.05.013. PubMed: 35688146.
3. Roohani, Y., Huang, K., and Leskovec, J. Predicting transcriptional outcomes of novel multigene perturbations with GEARS. *Nature Biotechnology* 42, 927-935 (2024). https://doi.org/10.1038/s41587-023-01905-6. PubMed: 37592036.
4. Wu, Y., Wershof, E., Schmon, S. M., Nassar, M., Osinski, B., Eksi, R., Yan, Z., Stark, R., Zhang, K., and Graepel, T. PerturBench: Benchmarking Machine Learning Models for Cellular Perturbation Analysis. *Advances in Neural Information Processing Systems 38*, 106937-106977 (2025). https://doi.org/10.52202/085713-3225. Preprint: https://arxiv.org/abs/2408.10609.
5. Vinas Torne, R. et al. Systema: a framework for evaluating genetic perturbation response prediction beyond systematic variation. *Nature Biotechnology* (2025). https://doi.org/10.1038/s41587-025-02777-8.
6. Radig, J. et al. scArchon: a scalable benchmarking framework for assessing single-cell perturbation models. *Genome Biology* 27, 162 (2026). https://doi.org/10.1186/s13059-026-04104-z. PubMed: 42121287.
7. Mao, X. et al. Benchmarking virtual cell models for in-the-wild perturbation response. *arXiv* 2604.27646 (2026). https://arxiv.org/abs/2604.27646.
8. Vollenweider, M. et al. Signal, Bounds, and Baselines: Principles for Rigorous Single-Cell Perturbation Prediction Benchmarking. *bioRxiv* (2026). https://doi.org/10.64898/2026.04.20.719650.
9. Replogle, J. M. et al. Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq: SRA and GEO file manifest. Figshare+ (2022). https://doi.org/10.25452/figshare.plus.20022944.
10. Replogle, J. M. et al. Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq: processed datasets. Figshare+ (2022). https://doi.org/10.25452/figshare.plus.20029387.


## Figure Legends

**Figure 1. VirtualPerturb-Audit framework.** Frozen perturbation-response datasets and model outputs enter a four-stage audit: input freeze, endpoint-family evaluation, stress testing, and bounded claim assignment. The figure depicts the method workflow, not a model-ranking result.

**Figure 2. Raw-space global agreement and perturbation-specific retrieval can diverge.** GEARS raw-space Pearson and retrieval MRR are shown for frozen Norman and GEARS-compatible filtered Replogle within-context tasks. Pearson is raw expression Pearson, whereas MRR measures perturbation-specific retrieval. Replogle panels use filtered essential-screen data.

**Figure 3. Within-context Replogle probe controls.** GEARS, mean-effect probes, and label-shuffled probes are compared on GEARS-compatible filtered Replogle K562 and RPE1 R-L1 tasks. Bars report audit-delta Pearson and retrieval MRR from frozen result tables.

**Figure 4. Matched-target GEARS cross-context transfer.** Shared-target analysis compares within-context and cross-context audit-delta Pearson for K562-to-RPE1 (n=150 matched targets) and RPE1-to-K562 (n=148 matched targets). Labels show paired drops and perturbation-level bootstrap 95% intervals. UER values discussed in text are sensitivity-only.

**Figure 5. STATE partial cross-architecture support.** STATE K562-to-RPE1 matched targets (n=15) show lower cross-context audit-delta Pearson, Spearman, and cosine, while UER has an interval crossing zero. The full-summary MRR bar is included to show endpoint heterogeneity rather than complete replication.
