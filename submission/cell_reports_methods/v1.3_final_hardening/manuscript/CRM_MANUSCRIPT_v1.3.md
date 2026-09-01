# VirtualPerturb-Audit: a reproducible framework for stress-testing perturbation-response models

Draft version: CRM_MANUSCRIPT_v1.3

Generated: 2026-09-01 12:05:52 UTC

## Author Information

Authors: Da Lin1, Ying Chen2, Yue Liu2, Yu Zhang1

Affiliations: 1 Department of Ophthalmology, The Second Affiliated Hospital of Wenzhou Medical University, No. 109 Xueyuan West Road, Lucheng District, Wenzhou, Zhejiang Province, China

2 Wenzhou Medical University, Wenzhou, Zhejiang Province, China

Correspondence: Yu Zhang, zhangyu1@wzhealth.com; ORCID: 0000-0001-8579-3692

## Summary

Perturbation-response models are increasingly used to predict transcriptional consequences of cellular interventions, yet aggregate transcriptomic similarity can obscure failures that matter for interpretation. VirtualPerturb-Audit is a reproducible framework for stress-testing perturbation-response models by freezing analysis inputs and separating global fit, perturbation-specific retrieval, falsification probes, unsupported-effect behavior, sign-flip behavior, and matched-target context transfer. Across frozen GEARS and STATE analyses, the framework showed that high global similarity did not guarantee perturbation identity recovery or cross-context stability. In GEARS on GEARS-compatible filtered Replogle K562 and RPE1 data, matched K562-to-RPE1 audit-delta Pearson decreased by 0.2883; the reverse direction decreased by 0.5480. In an independent STATE analysis, the matched K562-to-RPE1 audit-delta Pearson drop was 0.1163 across 15 shared targets. These results support VirtualPerturb-Audit as a methods framework for assigning bounded, endpoint-specific claims rather than a new perturbation predictor or universal model leaderboard.

## Introduction

Single-cell perturbation screens make it possible to observe transcriptome-scale consequences of targeted cellular or genetic perturbations in thousands to millions of cells. Genetic-interaction maps from Norman et al. and genome-scale Perturb-seq from Replogle et al. have become central resources for training and evaluating models that predict perturbation responses from single-cell expression data [1,2]. Methods such as GEARS, scGen, and newer foundation or virtual-cell models reflect a broader shift from descriptive single-cell analysis to counterfactual prediction [3,12-17,25].

Evaluation has not kept pace with this ambition. A perturbation-response model can look strong under aggregate expression similarity while failing to preserve perturbation identity, transfer across contexts, or avoid large unsupported gene-level effects. Recent benchmarking work has shown that rankings can change with task design, endpoint definition, data filtering, and treatment of systematic variation [4-9]. These observations create a practical problem for authors and reviewers: a single headline number rarely states which biological or computational claim it supports.

VirtualPerturb-Audit addresses this problem by making claim assignment explicit. The framework freezes the input state, distinguishes raw expression-space agreement from control-subtracted response agreement, adds retrieval and unsupported-effect endpoints, and uses baselines and probe controls to test whether apparent performance survives removal of perturbation-specific information. Matched-target transfer tests then ask whether within-context claims persist when the same perturbation targets are evaluated across cellular contexts.

Here we present VirtualPerturb-Audit as a model-agnostic audit protocol and demonstrate it on frozen GEARS and STATE outputs. The worked example uses GEARS-compatible Norman data and GEARS-compatible filtered Replogle essential-screen K562/RPE1 data, with STATE used as an independent deep architecture check. The study's contribution is the audit grammar: each endpoint maps to a constrained interpretation, and each stress test narrows the claim that can be made from model outputs.

## Results

### VirtualPerturb-Audit defines five auditable stages

VirtualPerturb-Audit evaluates perturbation-response predictions through five stages: input freeze, global-fit audit, perturbation-specific audit, falsification audit, and transfer/unsupported-effect audit (Figure 1; Table 1). Stage 1 freezes the dataset version, target universe, gene universe, model checkpoint, split assignments, preprocessing, and evaluation code. Stage 2 reports global-fit metrics, explicitly separating raw-space Pearson from audit-delta Pearson. Stage 3 asks whether the true perturbation is retrieved from a candidate universe. Stage 4 applies baselines and probe controls that remove or scramble target-specific information. Stage 5 evaluates matched-target context transfer, unsupported-effect rate (UER@K), and sign-flip rate.

This staged design prevents one endpoint from carrying claims that it cannot support. Raw-space Pearson can support global transcriptomic agreement. Audit-delta Pearson can support agreement in control-subtracted response direction and magnitude. Retrieval can support perturbation identity recovery within the declared candidate universe. UER@K and sign-flip rate can flag large prediction effects that lack observed support or oppose observed direction under the chosen null and support thresholds. Context-transfer tests can support or narrow claims about portability across cellular contexts.

**Table 1. VirtualPerturb-Audit components and interpretation**

| Audit component | Input | Metric/test | Question | Diagnostic signal | Supported interpretation |
| --- | --- | --- | --- | --- | --- |
| Input freeze | Expression matrices, labels, predictions, splits | Dataset/checkpoint/split/preprocessing/code freeze | What exactly is evaluated? | Mutable inputs change results | Reproducible audit for declared state |
| Global-fit audit | Observed and predicted profiles | Raw-space Pearson, audit-delta Pearson, Spearman, RMSE, cosine | Does broad expression structure agree? | High raw-space with weak delta | Global expression agreement |
| Perturbation-specific audit | Predicted and true deltas | Top1, Top5, MRR | Is the correct perturbation recoverable? | Low correct-target rank | Perturbation identity within candidate universe |
| Falsification audit | B0-B5 and FP1-FP3 | Endpoint survival after information removal | Does signal survive target removal? | Probe approaches model | Endpoint partly reflects shared structure |
| Transfer and unsupported-effect audit | Context holdouts, matched targets, top-K genes | Matched transfer drop, UER@K, sign-flip | Which claims survive context shift? | Large drop or high burden | Bounded transfer and error-burden interpretation |

### Global agreement and perturbation retrieval diverge across datasets

Frozen GEARS analyses showed that aggregate similarity and perturbation-specific retrieval describe different behavior (Figure 2). Norman L1 GEARS had raw-space Pearson 0.9887 and mean reciprocal rank (MRR) 0.3277. Replogle K562 R-L1 retained high raw-space Pearson (0.9851) but had much lower MRR (0.0445). Replogle RPE1 R-L1 had raw-space Pearson 0.9709 and MRR 0.0209.

These values were interpreted only within their metric space. Raw-space Pearson measures agreement between observed and predicted expression profiles in the expression space used by the GEARS evaluation output. Audit-delta Pearson, used below for response-specific analyses, measures agreement between control-subtracted perturbation effects. Reporting both endpoints makes clear whether a result reflects broad expression structure or perturbation-level response recovery.

### Probe controls identify endpoints driven by shared response structure

Within-context Replogle analyses compared GEARS against simple baselines and falsification probes (Figure 3). Mean-effect probes achieved substantial audit-delta Pearson in both K562 and RPE1, while retrieval remained low. GEARS showed modest improvements on some retrieval endpoints, but absolute retrieval remained limited.

The falsification result changes the interpretation of within-context fit. It indicates that part of the apparent response agreement can be produced by shared mean-effect structure rather than perturbation-specific prediction. VirtualPerturb-Audit therefore treats probe survival as a required condition for perturbation-specific claims: if a target-blind or label-shuffled probe approaches the model on an endpoint, the supported interpretation narrows to global response structure rather than target identity.

### Matched-target GEARS analysis shows strong context-transfer degradation

The strongest quantitative stress test came from matched-target GEARS transfer (Figure 4). In K562-to-RPE1 transfer, audit-delta Pearson decreased from 0.2812 within context to -0.0070 cross context. The paired drop was 0.2883, with a 95% interval of [0.2559, 0.3206]. UER50 increased from 0.1532 to 0.3877, and sign-flip rate increased from 0.2714 to 0.5718.

The reverse RPE1-to-K562 direction showed the same qualitative pattern. Audit-delta Pearson decreased from 0.5501 to 0.0021, with a paired drop of 0.5480 and a 95% interval of [0.5146, 0.5802]. Because the analysis used matched perturbation targets, the comparison reduced target-composition differences between within-context and cross-context conditions. It did not remove all possible context-dependent confounding, so the supported claim is a matched-target transfer-degradation claim rather than a universal statement about all perturbations or architectures.

### Independent STATE analysis provides partial cross-architecture support

STATE was evaluated as an independent deep architecture on four locked tasks. Audit-delta Pearson was 0.4445 for Norman L1, 0.4060 for Norman L2, 0.2639 for Replogle K562 R-L1, and 0.1874 for Replogle K562-to-RPE1 R-L4. These outputs used the same endpoint grammar as the GEARS audit while preserving STATE-specific preprocessing and inference constraints.

Matched STATE targets supported the direction of the GEARS transfer-degradation signal, although the evidence was smaller and endpoint-specific (Figure 5). Across 15 shared targets, audit-delta Pearson decreased from 0.2955 within context to 0.1792 cross context, for a mean drop of 0.1163 and a 95% interval of [0.0684, 0.1599]. Spearman decreased by 0.0709 and cosine decreased by 0.1048. Sign-flip rate was worse cross context, while the UER50 interval crossed zero. Leave-one-target-out sensitivity showed positive Pearson, Spearman, and cosine drops after omitting each of the 15 matched targets, indicating that the agreement-endpoint signal was not driven by one target.

The independent STATE analysis therefore supports the direction of matched-target transfer degradation but does not establish architecture-level generality. In full-summary comparisons, STATE R-L4 had higher retrieval MRR than STATE R-L1 in a smaller normalized target universe. In the v1.3 common-candidate sensitivity using the same 15 matched targets as candidates, MRR was 0.2594 for within-context STATE and 0.2212 for cross-context STATE. VirtualPerturb-Audit records this as partial cross-architecture support with endpoint heterogeneity.

## Discussion

VirtualPerturb-Audit provides a reproducible audit grammar for perturbation-response model evaluation. Its main premise is simple: model outputs should be linked to the narrowest claim supported by the endpoint and stress test. In the worked example, high raw-space agreement did not imply perturbation identity recovery, and within-context performance did not imply cross-context stability.

The GEARS matched-target analysis illustrates the value of pairing. Restricting the comparison to shared perturbation targets showed a large decrease in audit-delta Pearson for both K562-to-RPE1 and RPE1-to-K562 transfer. The same analysis also showed higher UER50 and sign-flip rates in the cross-context setting. These results support a strong matched-target transfer-degradation claim for the frozen GEARS setup.

The STATE analysis is deliberately interpreted more narrowly. It replicated the direction of the matched transfer drop for audit-delta Pearson, Spearman, and cosine, but it did not produce a uniform endpoint-level confirmation. The v1.3 leave-one-target-out analysis reduced concern that one target drove the STATE agreement-endpoint signal, while the common-candidate retrieval analysis emphasized that retrieval and regression-style agreement can move differently. This mixed result is useful: a methods audit should expose agreement and disagreement rather than converting heterogeneous evidence into a single verdict.

### Practical reporting recommendations

Perturbation-response studies should report dataset version, context labels, control definition, perturbation-label normalization, gene universe, target universe, split construction, model checkpoint, preprocessing freeze, evaluation code version, a strong baseline, raw-space metrics, control-subtracted metrics, retrieval candidate universe, falsification probes, context-shift tests where relevant, matched-target transfer where relevant, null provenance for UER, statistical unit, and model/data overlap provenance. These items are formalized in the VirtualPerturb-Audit reporting checklist.

This reporting discipline would make perturbation-response claims easier to review. A paper could state that a model supports global expression agreement, perturbation identity recovery, within-context generalization, or matched-target context transfer, without implying support for endpoints that were not tested. It would also make negative or mixed results more useful because endpoint-specific failure would identify where future model development should focus.

## Limitations of the study

The Replogle analyses use GEARS-compatible filtered essential-screen data rather than the complete Figshare+ processed objects. A replicate-derived empirical performance bound could not be established because validated biological replicate metadata were unavailable. UER is an internal sensitivity measure based on the selected null envelope and should not be interpreted as experimental proof of hallucination. GEARS R-L4 uses a GEARS-compatible cross-context inference adapter rather than a native cell-line-aware GEARS training design. The independent STATE matched transfer analysis contains 15 shared targets and provides partial, endpoint-heterogeneous support. The manuscript does not claim a universal model ranking.

## STAR Methods

### Resource availability

#### Lead contact

Further information and requests should be directed to Yu Zhang, zhangyu1@wzhealth.com.

#### Materials availability

This computational study did not generate new physical reagents.

#### Data and code availability

Norman perturbation data were used through a GEARS-compatible processed mirror [1,3]. Replogle analyses used GEARS-compatible filtered essential-screen K562 and RPE1 objects; complete Figshare+ processed objects were not part of the frozen analyses [2,10,11]. Derived result tables are stored under `results/tables/`, and manuscript figures are stored under `figures/main/` and `figures/supplementary/`. Public repository URL and archived code/result DOI remain to be completed before journal submission. Working metadata use `[ZENODO_DOI_PENDING]` only as a placeholder.

### Method details

#### VirtualPerturb-Audit protocol

VirtualPerturb-Audit contains five stages. Stage 1 freezes expression data, perturbation labels, control labels, context labels, model predictions, split assignments, dataset version, target universe, gene universe, model checkpoint, preprocessing, and evaluation code. Stage 2 computes global-fit endpoints, including raw-space Pearson, audit-delta Pearson, Spearman, RMSE, MAE, and cosine. Stage 3 computes perturbation-specific retrieval using Top1, Top5, and MRR. Stage 4 applies baselines and falsification probes B0-B5 and FP1-FP3. Stage 5 evaluates context holdout, matched-target transfer, UER@K, and sign-flip rate.

#### Dataset acquisition and provenance

Norman data were analyzed as a GEARS-compatible processed object derived from the published Perturb-seq study [1,3]. The audit retains the processed cell and gene universe used by GEARS-compatible workflows rather than reprocessing raw sequencing output. Replogle data were analyzed as GEARS-compatible filtered essential-screen objects for K562 and RPE1. This scope is narrower than the complete Figshare+ processed release and is treated as a permanent limitation [2,10,11].

#### Data harmonization

Gene identifiers were represented as gene symbols after normalization to the common model vocabulary. Duplicate gene symbols were handled during preprocessing by retaining the model-compatible representation used in frozen AnnData objects. Control cells were identified from control perturbation labels. Perturbation labels were canonicalized so that explicit control partners were collapsed consistently; for example, `ctrl+X` and `X+ctrl` were represented as the same single-target perturbation. Single and double perturbations were retained in the task definitions used by the corresponding split. AnnData expression matrices, observation labels, and variable gene fields were the primary data containers.

The harmonization layer did not infer missing targets from free-text labels, did not impute genes outside the model vocabulary, and did not use target-context perturbation measurements to alter source-context model output. When a label could not be mapped into the declared perturbation universe, the affected row was excluded from that endpoint rather than repaired post hoc.

#### Split construction

L0 is a random cell holdout. L1 is an unseen-perturbation holdout in which non-control perturbations are assigned to train, validation, or test and controls remain in training. L2 is a component-holdout split in which perturbations are assigned by held-out perturbation components; mixed overlaps with held-out components are excluded. L3 is a gene-family holdout based on the HGNC-derived candidate file `results/pilot/l3_gene_family_holdout_candidates.csv` and provenance file `data/metadata/hgnc_perturbation_gene_groups_provenance.json`. R-L1 is a within-context Replogle target holdout within a cell line. R-L4 is a source-context to target-context cross-context inference stress test in which source-context perturbations are training examples and target-context perturbations plus target-context controls are assigned to test. R-L4 supports context-transfer stress testing only with its adapter limitation.

#### Leakage integrity checks

The audit checked for exact cell overlap, forbidden target overlap under split definitions, training-only preprocessing, absence of test-label use during fitting, split-hash stability, and canonical perturbation labeling. These checks reduce identifiable evaluation-leakage risk. They do not prove that every possible biological, preprocessing, or dataset-curation dependency has been eliminated.

#### Baseline definitions

B0 is the no-change baseline, which returns control or basal input expression without a perturbation-specific delta. B1 is the global perturbed mean baseline. B2 is the context-matched perturbed mean baseline. B3 is an additive component baseline used only when component-level perturbation information exists and is not used for Replogle essential-screen analyses. B4 is a low-capacity PCA/Ridge baseline. B5 is a mean-effect baseline. The full frozen mapping is stored in `results/tables/baseline_definition_registry.tsv`.

#### Falsification probes

FP1 is a perturbation-blind mean-effect probe. FP2 is a cell-state-blind probe when the required implementation and component/context information are available. FP3 is a label-shuffled diagnostic probe. These probes are diagnostic stress tests, not biological models. The registry is stored in `results/tables/falsification_probe_registry.tsv`.

#### Delta-response endpoints

For perturbation target `p`, the observed response vector is `Delta_true,p = mean(X_perturbation,p) - mean(X_control)`. The predicted response vector is `Delta_pred,p = mean(X_prediction,p) - mean(X_control)`, using the audit control appropriate to the frozen endpoint. Audit-delta Pearson is `corr(Delta_true,p, Delta_pred,p)` over genes for a perturbation target, then summarized across perturbation targets. The analysis unit is the perturbation target, not the single cell.

#### Retrieval endpoints

For each perturbation `p`, the predicted perturbation delta was compared with candidate true perturbation centroids using cosine similarity. Vectors were not additionally standardized or centered inside the retrieval function. The candidate universe was the intersection of available predicted and true non-control perturbation centroids; controls were not candidates. Targets unavailable on either side were excluded. Top1 is the fraction of perturbations with rank 1, Top5 is the fraction with rank <= 5, and MRR is the mean of `1/rank`. Native-candidate retrieval and common-candidate retrieval are reported separately when the candidate universe differs across compared settings.

#### Unsupported-effect rate

For perturbation `p`, genes were ordered by `abs(Delta_pred,p)`. Among the top `K` predicted genes, a gene was counted as unsupported when `abs(Delta_true,p)` was less than or equal to the null absolute threshold. In frozen GEARS/Replogle and STATE scripts, the null threshold for UER50 is the median absolute observed delta in the evaluated perturbation/gene vector. UER@K is the fraction of unsupported genes among the predicted top K genes. UER is an internal sensitivity measure and not validated biological replicate ground truth.

#### Sign-flip endpoints

Supported genes were defined as genes with `abs(Delta_true,p)` greater than the support threshold. In the frozen scripts, this support threshold was the 95th percentile of absolute observed delta for the evaluated perturbation/gene vector. A sign flip was counted when `sign(Delta_pred,p)` differed from `sign(Delta_true,p)` among supported genes. A major sign flip also required `abs(Delta_pred,p)` greater than the same support threshold. The manuscript reports sign-flip rate unless otherwise specified.

#### Matched-target transfer analysis

GEARS matched K562-to-RPE1 transfer used the intersection between K562 R-L1 targets and K562-to-RPE1 R-L4 targets. The reverse analysis used the analogous RPE1 R-L1 and RPE1-to-K562 R-L4 intersection. STATE matched transfer used 15 common K562 targets shared by the within-context and K562-to-RPE1 outputs. Matching controls target-composition differences between within-context and cross-context comparisons, but it does not eliminate all context-dependent confounding.

#### Output claim assignment

VirtualPerturb-Audit assigns claims at the endpoint-family level. Raw-space Pearson supports global expression agreement. Audit-delta Pearson supports control-subtracted response agreement. Retrieval supports perturbation identity recovery only within the declared candidate universe. A transfer result supports context portability only for the matched target set and evaluated contexts. High UER@K or sign-flip rate narrows the claim by identifying unsupported magnitude or direction behavior under the selected threshold.

#### Standardized input and output contracts

The software interface is defined in `manuscript/VIRTUALPERTURB_INPUT_CONTRACT.md` and `manuscript/VIRTUALPERTURB_OUTPUT_CONTRACT.md`. Supported inputs include cell-level AnnData, target-level pseudobulk matrices, and precomputed prediction matrices or centroids. Required output families include global-fit metrics, retrieval metrics, unsupported-effect metrics, sign-flip metrics, split-integrity reports, matched-transfer summaries when relevant, probe comparisons, and audit claim profiles.

#### Software and reproducibility

Frozen result tables are stored under `results/tables/`. Main figures are stored under `figures/main/`, supplementary figures under `figures/supplementary/`, manuscript-facing reports under `reports/`, and manuscript drafts under `manuscript/`. The minimal example in `examples/minimal_audit/` demonstrates the mechanics of audit-delta Pearson, retrieval rank, MRR contribution, UER@K, and sign-flip rate using toy tabular predictions. This example is intended for software onboarding and is not used as manuscript evidence.

### Quantification and statistical analysis

All uncertainty intervals were computed at the perturbation-target level. GEARS matched-target analyses used paired perturbation-level bootstrap intervals with 2000 bootstrap resamples. STATE matched transfer used bootstrap intervals over 15 common targets. The v1.3 STATE leave-one-target-out analysis and common-candidate retrieval analysis used frozen target-level metrics and frozen centroids only and are labelled exploratory. No cell-level P value was used for the manuscript claims.

## References

1. Norman, T. M. et al. Exploring genetic interaction manifolds constructed from rich single-cell phenotypes. Science 365, 786-793 (2019). https://doi.org/10.1126/science.aax4438.
2. Replogle, J. M. et al. Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq. Cell 185, 2559-2575.e28 (2022). https://doi.org/10.1016/j.cell.2022.05.013.
3. Roohani, Y., Huang, K. and Leskovec, J. Predicting transcriptional outcomes of novel multigene perturbations with GEARS. Nature Biotechnology 42, 927-935 (2024). https://doi.org/10.1038/s41587-023-01905-6.
4. Wu, Y. et al. PerturBench: Benchmarking Machine Learning Models for Cellular Perturbation Analysis. Advances in Neural Information Processing Systems 38, 106937-106977 (2025). https://doi.org/10.52202/085713-3225.
5. Vinas Torne, R. et al. Systema: a framework for evaluating genetic perturbation response prediction beyond systematic variation. Nature Biotechnology (2025). https://doi.org/10.1038/s41587-025-02777-8.
6. Radig, J. et al. scArchon: a scalable benchmarking framework for assessing single-cell perturbation models. Genome Biology 27, 162 (2026). https://doi.org/10.1186/s13059-026-04104-z.
7. Mao, X. et al. Benchmarking virtual cell models for in-the-wild perturbation response. arXiv:2604.27646 (2026). https://arxiv.org/abs/2604.27646.
8. Vollenweider, M. S. and Buhlmann, P. Signal, Bounds, and Baselines: Principles for Evaluating Virtual Cell Perturbation Models. bioRxiv (2026). https://doi.org/10.64898/2026.04.20.719650.
9. Ahlmann-Eltze, C., Huber, W. and Anders, S. Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines. Nature Methods (2025). https://doi.org/10.1038/s41592-025-02772-6.
10. Replogle, J. M. et al. Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq: SRA and GEO file manifest. Figshare+ (2022). https://doi.org/10.25452/figshare.plus.20022944.
11. Replogle, J. M. et al. Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq: processed datasets. Figshare+ (2022). https://doi.org/10.25452/figshare.plus.20029387.
12. Cui, H. et al. scGPT: toward building a foundation model for single-cell multi-omics using generative AI. Nature Methods 21, 1470-1480 (2024). https://doi.org/10.1038/s41592-024-02201-0.
13. Theodoris, C. V. et al. Transfer learning enables predictions in network biology. Nature 618, 616-624 (2023). https://doi.org/10.1038/s41586-023-06139-9.
14. Lopez, R. et al. Deep generative modeling for single-cell transcriptomics. Nature Methods 15, 1053-1058 (2018). https://doi.org/10.1038/s41592-018-0229-2.
15. Gayoso, A. et al. A Python library for probabilistic analysis of single-cell omics data. Nature Biotechnology 40, 163-166 (2022). https://doi.org/10.1038/s41587-021-01206-w.
16. Lotfollahi, M. et al. scGen predicts single-cell perturbation responses. Nature Methods 16, 715-721 (2019). https://doi.org/10.1038/s41592-019-0494-8.
17. Lotfollahi, M. et al. Mapping single-cell data to reference atlases by transfer learning. Nature Biotechnology 40, 121-130 (2022). https://doi.org/10.1038/s41587-021-01001-7.
18. Wolf, F. A., Angerer, P. and Theis, F. J. SCANPY: large-scale single-cell gene expression data analysis. Genome Biology 19, 15 (2018). https://doi.org/10.1186/s13059-017-1382-0.
19. Virshup, I. et al. The scverse project provides a computational ecosystem for single-cell omics data analysis. Nature Biotechnology 41, 604-606 (2023). https://doi.org/10.1038/s41587-023-01733-8.
20. Harris, C. R. et al. Array programming with NumPy. Nature 585, 357-362 (2020). https://doi.org/10.1038/s41586-020-2649-2.
21. McKinney, W. Data structures for statistical computing in Python. Proceedings of the 9th Python in Science Conference, 56-61 (2010). https://doi.org/10.25080/Majora-92bf1922-00a.
22. Pedregosa, F. et al. Scikit-learn: Machine learning in Python. Journal of Machine Learning Research 12, 2825-2830 (2011).
23. Virtanen, P. et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. Nature Methods 17, 261-272 (2020). https://doi.org/10.1038/s41592-019-0686-2.
24. Hunter, J. D. Matplotlib: A 2D graphics environment. Computing in Science and Engineering 9, 90-95 (2007). https://doi.org/10.1109/MCSE.2007.55.
25. Adduri, A. K. et al. Predicting cellular responses to perturbation across biological contexts with State. bioRxiv (2025). https://doi.org/10.1101/2025.06.26.661135.
26. Roohani, Y. H. et al. Virtual Cell Challenge: Toward a Turing test for the virtual cell. Cell 188, 3370-3374 (2025). https://doi.org/10.1016/j.cell.2025.06.008.

## Figure Legends

**Figure 1. VirtualPerturb-Audit protocol.** Frozen datasets, predictions, split assignments, and preprocessing enter a five-stage audit that separates input freeze, global fit, perturbation-specific retrieval, falsification probes, and matched transfer/unsupported-effect testing. The figure emphasizes method identity and claim boundaries rather than model ranking.

**Figure 2. Global expression agreement and perturbation retrieval diverge.** GEARS raw-space Pearson and retrieval MRR are shown for frozen Norman and GEARS-compatible filtered Replogle within-context tasks. Pearson is raw expression Pearson in the GEARS output space. MRR measures perturbation-specific retrieval from the declared candidate universe.

**Figure 3. Probe controls for within-context Replogle evaluation.** GEARS, baselines, and falsification probes are compared on GEARS-compatible filtered Replogle K562 and RPE1 R-L1 tasks. Bars report audit-delta Pearson and retrieval MRR from frozen result tables. Probe performance narrows the supported interpretation of endpoints that can be approached without perturbation-specific information.

**Figure 4. Matched-target GEARS context-transfer stress test.** Shared-target analysis compares within-context and cross-context audit-delta Pearson for K562-to-RPE1 (n=150 matched targets) and RPE1-to-K562 (n=148 matched targets). Labels show paired drops and perturbation-level bootstrap 95% intervals. Figure 4 uses QC and matched-transfer language only.

**Figure 5. STATE shows partial cross-architecture transfer degradation with endpoint heterogeneity.** STATE K562-to-RPE1 matched targets (n=15) show lower cross-context audit-delta Pearson, Spearman, and cosine. UER50 has an interval crossing zero, sign-flip rate is worse cross context, and common-candidate retrieval from frozen centroids is reported as an exploratory sensitivity panel.
