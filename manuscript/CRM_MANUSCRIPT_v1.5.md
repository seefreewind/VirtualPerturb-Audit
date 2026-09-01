# VirtualPerturb-Audit: a reproducible framework for stress-testing perturbation-response models

Draft version: CRM_MANUSCRIPT_v1.5

Generated: 2026-09-01 12:39:49 UTC

## Author Information

Authors: Yi Zha1, Da Lin1, Ying Chen2, Yue Liu2, Yu Zhang1

Affiliations: 1 Department of Ophthalmology, The Second Affiliated Hospital of Wenzhou Medical University, No. 109 Xueyuan West Road, Lucheng District, Wenzhou, Zhejiang Province, China

2 Wenzhou Medical University, Wenzhou, Zhejiang Province, China

Correspondence: Yu Zhang, zhangyu1@wzhealth.com; ORCID: 0000-0001-8579-3692

## Summary

Perturbation-response models are increasingly used to predict transcriptional consequences of cellular interventions, yet aggregate transcriptomic similarity can obscure failures that matter for interpretation. VirtualPerturb-Audit is a reproducible framework for stress-testing perturbation-response models by freezing analysis inputs and separating global fit, perturbation-specific retrieval, falsification probes, unsupported-effect behavior, sign-flip behavior, and matched-target context transfer. Across frozen GEARS and STATE analyses, the framework showed that high global similarity did not guarantee perturbation identity recovery or cross-context stability. In GEARS on GEARS-compatible filtered Replogle K562 and RPE1 data, matched K562-to-RPE1 audit-delta Pearson decreased by 0.2883; the reverse direction decreased by 0.5480. In an independent STATE analysis, the matched K562-to-RPE1 audit-delta Pearson drop was 0.1163 across 15 shared targets. These results support VirtualPerturb-Audit as a methods framework for assigning bounded, endpoint-specific claims rather than a new perturbation predictor or universal model leaderboard.

## Introduction

Single-cell perturbation screens can now measure transcriptional responses to targeted cellular and genetic perturbations at a scale that was not practical with low-throughput assays. Genetic-interaction maps and genome-scale Perturb-seq datasets, including Norman et al. and Replogle et al., have made these responses a central substrate for predictive modeling [1,2]. Perturbation-response models such as GEARS, together with recent virtual-cell and cross-context models such as STATE, extend this setting from description toward counterfactual prediction [3,25]. The most useful application is not simply reconstructing an average observed expression profile. It is deciding whether a model has learned response information that can support prioritization for unseen perturbations, cellular backgrounds, or experimental contexts. For these models to guide biological prioritization, predictive accuracy must reflect perturbation-specific and context-transferable signal rather than broad transcriptional similarity alone.

Perturbation-model evaluation has become substantially more rigorous in 2025-2026. Recent work has shown that simple linear baselines can rival complex perturbation models and that model-to-model comparisons can overstate progress when baseline strength is not explicit [9]. Other studies have shown that systematic transcriptional variation can inflate commonly used prediction scores, making apparent performance sensitive to variation that is not necessarily perturbation-specific [5]. Standardized benchmarks and modular evaluation frameworks have further shown that endpoint families are not interchangeable: expression-fit metrics, ranking-style metrics, biological-response endpoints, score transformations, and task construction can lead to different conclusions [4,6,7,27]. Signal, bound, calibration, in-the-wild, and context-generalization studies extend this point by emphasizing empirical signal strength and stricter perturbation-, dataset-, and context-transfer settings [8,27]. Together, these studies establish that perturbation prediction should be judged through strong baselines, multiple endpoint families, and explicit generalization tasks rather than a single aggregate expression-fit score.

These advances leave a narrower methodological gap. Existing benchmarks primarily ask how models should be scored and compared; less explicit is how a specific performance claim should be challenged before it is promoted to a stronger biological interpretation. Three problems are especially important for reviewer-facing interpretation. First, a strong global score may persist after target-specific information is removed, which weakens claims about perturbation identity. Second, cross-context comparisons may change the perturbation target universe, so an apparent transfer difference can mix context shift with target-composition shift. Third, different endpoint families may support conflicting claims for the same predictions, for example broad response agreement without strong retrieval or directional fidelity. Recent benchmark frameworks increasingly address individual parts of these problems. The missing layer is a falsification-oriented workflow that freezes analysis provenance, applies information-removal probes, matches perturbation targets across contexts, reports endpoint disagreement, and maps each endpoint to an explicit claim boundary. VirtualPerturb-Audit complements recent benchmarking frameworks by shifting the unit of evaluation from model ranking to claim falsification.

Here we present VirtualPerturb-Audit as a model-agnostic audit protocol for bounded interpretation of perturbation-response predictions. The framework freezes data and code provenance, separates raw-space and control-subtracted endpoints, evaluates perturbation retrieval, compares strong and simple baselines, applies information-removal falsification probes, matches perturbation targets across contexts, and reports unsupported-effect and sign-direction behavior. Its output is not a single pass/fail score. It is a claim profile stating whether the evidence supports global expression agreement, perturbation identity recovery, matched-target context transfer, or only a narrower response-structure interpretation. We demonstrate the protocol on frozen GEARS and STATE outputs using GEARS-compatible Norman data and GEARS-compatible filtered Replogle K562/RPE1 essential-screen data. We hypothesized that conclusions based on aggregate transcriptomic agreement would narrow when predictions were evaluated for perturbation specificity and matched-target context transfer, and we further asked whether an independent model architecture would reproduce the same audit phenotype.

## Results

### VirtualPerturb-Audit defines five auditable stages

VirtualPerturb-Audit evaluates perturbation-response predictions through five linked components: input and provenance freeze, global-fit audit, perturbation-specific audit, falsification audit, and transfer and error-burden audit (Figure 1; Table 1). The input and provenance freeze locks the dataset version, target universe, gene universe, model checkpoint, split assignments, preprocessing, and evaluation code. The global-fit audit reports raw-space and audit-delta agreement as noninterchangeable metric spaces. The perturbation-specific audit asks whether the true perturbation is retrieved from a candidate universe. The falsification audit applies baselines and probe controls that remove or scramble target-specific information. The transfer and error-burden audit evaluates matched-target context transfer, unsupported-effect rate (UER@K), and sign-flip rate.

This staged design prevents one endpoint from carrying claims that it cannot support. Raw-space Pearson can support global transcriptomic agreement. Audit-delta Pearson can support agreement in control-subtracted response direction and magnitude. Retrieval can support perturbation identity recovery within the declared candidate universe. UER@K and sign-flip rate can flag large prediction effects that lack observed support or oppose observed direction under the chosen null and support thresholds. Context-transfer tests can support or narrow claims about portability across cellular contexts.

**Table 1. VirtualPerturb-Audit components and interpretation**

| Audit component | Input | Metric/test | Question | Diagnostic signal | Supported interpretation |
| --- | --- | --- | --- | --- | --- |
| Input and provenance freeze | Expression matrices, labels, predictions, splits | Dataset/checkpoint/split/preprocessing/code freeze | What exactly is evaluated? | Mutable inputs change results | Reproducible audit for declared state |
| Global-fit audit | Observed and predicted profiles | Raw-space Pearson, audit-delta Pearson, Spearman, RMSE, cosine | Does broad expression structure agree? | High raw-space with weak delta | Global expression agreement |
| Perturbation-specific audit | Predicted and true deltas | Top1, Top5, MRR | Is the correct perturbation recoverable? | Low correct-target rank | Perturbation identity within candidate universe |
| Falsification audit | B0-B5 and FP1-FP3 | Endpoint survival after information removal | Does signal survive target removal? | Probe approaches model | Endpoint partly reflects shared structure |
| Transfer and error-burden audit | Context holdouts, matched targets, top-K genes | Matched transfer drop, UER@K, sign-flip | Which claims survive context shift? | Large drop or high burden | Bounded transfer and error-burden interpretation |

### Global agreement and perturbation retrieval diverge across datasets

Frozen GEARS analyses showed that aggregate similarity and perturbation-specific retrieval describe different behavior when viewed as separate endpoint families (Figure 2). Norman L1 GEARS had raw-space Pearson 0.9887 and mean reciprocal rank (MRR) 0.3277. Replogle K562 R-L1 retained high raw-space Pearson (0.9851) but had much lower MRR (0.0445). Replogle RPE1 R-L1 had raw-space Pearson 0.9709 and MRR 0.0209.

These values were interpreted only within their metric space. Raw-space Pearson measures agreement between observed and predicted expression profiles in the expression space used by the GEARS evaluation output. Audit-delta Pearson, used below for response-specific analyses, measures agreement between control-subtracted perturbation effects. Reporting both endpoints makes clear whether a result reflects broad expression structure or perturbation-level response recovery.

### Probe controls identify endpoints driven by shared response structure

Within-context Replogle analyses compared GEARS against target-information-restricted probes in the K562 and RPE1 R-L1 tasks (Figure 3). Mean-effect probes achieved substantial audit-delta Pearson in both contexts, and label-shuffled probes retained non-zero response agreement after perturbation labels were scrambled. GEARS showed higher retrieval within each context, but absolute retrieval remained limited.

The falsification result changes the interpretation of within-context fit. It indicates that part of the apparent response agreement can be produced by shared mean-effect structure rather than perturbation-specific prediction. VirtualPerturb-Audit therefore treats probe survival as a required condition for perturbation-specific claims: if a target-blind or label-shuffled probe approaches the model on an endpoint, the supported interpretation narrows to global response structure rather than target identity.

### Matched-target GEARS analysis shows strong context-transfer degradation

The strongest quantitative stress test came from matched-target GEARS transfer (Figure 4). In K562-to-RPE1 transfer, audit-delta Pearson decreased from 0.2812 within context to -0.0070 cross context. The paired drop was 0.2883, with a 95% interval of [0.2559, 0.3206]. UER50 increased from 0.1532 to 0.3877, and sign-flip rate increased from 0.2714 to 0.5718.

The reverse RPE1-to-K562 direction showed the same qualitative pattern. Audit-delta Pearson decreased from 0.5501 to 0.0021, with a paired drop of 0.5480 and a 95% interval of [0.5146, 0.5802]. Because the analysis used matched perturbation targets, the comparison reduced target-composition differences between within-context and cross-context conditions. It did not remove all possible context-dependent confounding, so the supported claim is a matched-target transfer-degradation claim rather than a universal statement about all perturbations or architectures.

### Independent STATE analysis provides partial cross-architecture support

STATE was evaluated as an independent deep architecture on four locked tasks. Audit-delta Pearson was 0.4445 for Norman L1, 0.4060 for Norman L2, 0.2639 for Replogle K562 R-L1, and 0.1874 for Replogle K562-to-RPE1 R-L4. These outputs used the same endpoint grammar as the GEARS audit while preserving STATE-specific preprocessing and inference constraints.

Matched STATE targets supported the direction of the GEARS transfer-degradation signal, although the evidence was smaller and endpoint-specific (Figure 5). Across 15 shared targets, audit-delta Pearson decreased from 0.2955 within context to 0.1792 cross context, for a mean drop of 0.1163 and a 95% interval of [0.0684, 0.1599]. Spearman decreased by 0.0709 and cosine decreased by 0.1048. Sign-flip rate was worse cross context, while the UER50 interval crossed zero. Leave-one-target-out sensitivity showed positive Pearson, Spearman, and cosine drops after omitting each of the 15 matched targets, indicating that the agreement-endpoint signal was not driven by one target.

The independent STATE analysis therefore supports the direction of matched-target transfer degradation but does not establish architecture-level generality. In full-summary comparisons, STATE R-L4 had higher retrieval MRR than STATE R-L1 in a smaller normalized target universe. In the v1.3 common-candidate sensitivity using the same 15 matched targets as candidates, MRR was 0.2594 for within-context STATE and 0.2212 for cross-context STATE. VirtualPerturb-Audit records this as partial cross-architecture support with endpoint heterogeneity.

## Discussion

A central lesson from this audit is that perturbation-model performance is not a unitary property. A prediction system can show strong global expression agreement while giving weaker support to perturbation identification, unsupported-effect control, sign-direction fidelity, or cross-context transfer. These endpoint families answer different questions and should not be collapsed into a single interpretation. In the frozen GEARS and STATE examples, the strongest conclusion was not that a model simply succeeded or failed; it was that each score family supported a different claim boundary. VirtualPerturb-Audit formalizes this distinction by treating evaluation as a stress test of interpretation. The framework asks what remains supported after perturbation-specific information is removed, after transfer comparisons are restricted to matched targets, and after regression-style agreement is compared with retrieval and error-burden endpoints. The practical implication is direct: perturbation-response predictions should be reported according to the biological or computational claim being made, because the appropriate audit depends on whether the claim concerns broad expression reconstruction, target identity, context portability, or directional response fidelity.

The divergence between global fit and perturbation specificity is consistent with recent benchmark evidence that standard expression-space scores can be shaped by shared, systematic, or context-common transcriptional structure rather than perturbation-specific signal alone [4,5,9,27]. Strong-baseline work has shown that simple linear or mean-effect predictors can be competitive under common evaluation regimes [9]. Systematic-variation analyses further show that apparent prediction quality can reflect response structure shared across perturbations [5]. PerturBench and scPertEval extend this point by showing that metric family, representation, score transformation, and candidate construction affect the conclusion drawn from the same prediction setting [4,27]. Our results extend these observations from baseline comparison to active falsification: target-blind and label-disrupting probes are not merely alternative baselines, but direct tests of whether the endpoint still carries perturbation-identity information. When a probe approaches a model on an agreement endpoint while retrieval remains weak, the defensible interpretation narrows from target-specific prediction to shared response-structure capture.

The matched-transfer analyses address a related but distinct question: whether a within-context response claim survives movement across cellular context. Perturbation effects are conditional on basal state, regulatory configuration, lineage background, and gene-by-context interactions, so transfer performance can change even when the perturbation label is nominally the same. Recent STATE, Virtual Cell Challenge, and in-the-wild benchmarking efforts emphasize this broader context-generalization problem [7,25,26]. VirtualPerturb-Audit adds a matched-target control to this setting. The persistence of degradation after target matching argues against target-composition change as the sole explanation. However, this design does not isolate cellular context as the sole causal factor because training design, inference adapters, and model-context mismatch remain intertwined with the shift. The GEARS result should therefore be read as a strong matched-target transfer-degradation finding for the frozen adapter-based setup, while the STATE result provides partial cross-architecture support in the same direction. The evidence supports a context-transfer stress-test claim, not a universal statement about all perturbations, all contexts, or all model classes.

Endpoint heterogeneity is also informative rather than inconvenient. In the STATE audit, agreement metrics moved consistently under matched transfer and leave-one-target-out analysis indicated that this pattern was not explained by one target, while common-candidate retrieval showed a weaker contrast and unsupported-effect behavior remained sensitive to its internal null. Pearson, Spearman, cosine similarity, MRR, UER, and sign-flip rate are not interchangeable measurements. Pearson and cosine emphasize response-vector agreement; MRR asks whether the correct perturbation can be recovered from a candidate universe; UER depends on a chosen support or null threshold; sign-flip rate asks whether supported directional effects are reversed. Benchmarking studies increasingly make the same point at the protocol level: evaluation design determines the scientific question that a score can answer [4,27]. Discordant endpoints should not be averaged into a reassuring composite. They should be used to assign separate claims, so that global agreement, retrieval, context transfer, unsupported magnitude, and sign direction can each support or restrict a specific interpretation.

The methodological contribution of VirtualPerturb-Audit is a falsification layer between benchmark performance and scientific interpretation. It makes three advances for reviewer-facing use: information-removal probes that test whether an endpoint survives loss of perturbation-specific content, matched-target transfer controls that reduce target-composition confounding in cross-context comparisons, and endpoint-specific claim assignment under frozen provenance. This layer is useful for several audiences. Model developers can use it to identify whether improvements affect perturbation identity, context transfer, or only broad expression structure. Benchmark developers can use it to report candidate universes, control definitions, and endpoint-specific claim boundaries more transparently. Experimental users can avoid promoting global similarity to biological prioritization unless retrieval, direction, and transfer evidence support that use. Software and reproducibility reviewers can audit whether the data version, split, model checkpoint, preprocessing, and post-processing state used to make a claim are recoverable. The resulting claim profile is more useful than a single leaderboard position because it states what the prediction output can and cannot currently support.

## Limitations of the study

The main limitations affect scope rather than the internal direction of the matched-transfer findings. The Replogle analyses use GEARS-compatible filtered essential-screen data, so the conclusions apply to that frozen subset and should not be generalized to the complete processed release without reanalysis. GEARS R-L4 uses a cross-context inference adapter rather than a native cell-line-aware training design; this limits architectural interpretation but does not remove the matched-target degradation observed under the declared adapter. The independent STATE matched analysis contains a small shared-target set, and leave-one-target-out sensitivity mitigates single-target dominance without replacing larger-context replication. UER remains an internal sensitivity endpoint because no replicate-derived biological null was available, so it should not be read as a validated biological-null endpoint. Recent shared-control work also shows that reusing the same control population in differential-expression comparisons can inflate correlation or cosine scores [28]. A new shared-control split sensitivity was not run here because the frozen manuscript package does not preserve a statistically valid, non-overlapping control-cell construction across all GEARS and STATE endpoints without changing the locked analysis state. This limitation makes the audit more conservative: it reinforces the need to interpret agreement scores alongside retrieval, sign, probe, and matched-transfer endpoints rather than relying on shared-control-subtracted correlation alone. Perturbation-response predictions should therefore be reported not only by how well they score, but by which biological or computational claims remain supported after explicit falsification and context-shift testing.

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

VirtualPerturb-Audit contains five linked components. Input and provenance freeze records expression data, perturbation labels, control labels, context labels, model predictions, split assignments, dataset version, target universe, gene universe, model checkpoint, preprocessing, and evaluation code. The global-fit audit computes raw-space Pearson, audit-delta Pearson, Spearman, RMSE, MAE, and cosine. The perturbation-specific audit computes retrieval using Top1, Top5, and MRR. The falsification audit applies baselines and falsification probes B0-B5 and FP1-FP3. The transfer and error-burden audit evaluates context holdout, matched-target transfer, UER@K, and sign-flip rate.

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

27. Cai, Y. et al. scPertEval: A benchmark for single-cell perturbation prediction evaluation. bioRxiv (2026). https://doi.org/10.1101/2026.07.23.740433.

28. Nicol, P. B., Shivakumar, S. and Irizarry, R. A. Spurious correlation inflates performance in single-cell perturbation prediction. bioRxiv (2026). https://doi.org/10.64898/2026.05.07.723486.

## Figure Legends

**Figure 1. VirtualPerturb-Audit protocol.** VirtualPerturb-Audit accepts observed perturbation responses, model predictions, controls, perturbation and context labels, and frozen analysis provenance. The framework separately evaluates global expression agreement, perturbation-specific retrieval, falsification probes, matched-target context transfer, and unsupported or directional effects. Results are translated into endpoint-specific claim boundaries rather than a single model score. The schematic depicts the general framework and does not represent a direct GEARS-versus-STATE ranking.

**Figure 2. High global expression agreement does not imply perturbation-specific retrieval.** Raw-space Pearson agreement (A) and perturbation retrieval by mean reciprocal rank (MRR; B) are displayed separately for frozen Norman and GEARS-compatible filtered Replogle within-context tasks. The Pearson axis is restricted to resolve values that are uniformly close to one; dot positions rather than bar lengths encode estimates. Retrieval is evaluated within each task's declared non-control candidate universe, and candidate-set size should be considered when comparing absolute MRR values across tasks. Open markers indicate the theoretical expectation under random ranking for the corresponding candidate universe. These endpoint families quantify distinct properties: global transcriptomic agreement and perturbation identity recovery.

**Figure 3. Falsification probes separate shared response agreement from perturbation-specific retrieval.** Audit-delta Pearson (A) and perturbation retrieval by MRR (B) are shown for GEARS and target-information-restricted probes in GEARS-compatible filtered Replogle K562 and RPE1 within-context tasks. The mean-effect probe does not use perturbation-specific target identity at prediction time, and the label-shuffled probe disrupts that identity by scrambling perturbation labels. These probes retain non-zero or substantial response agreement, whereas GEARS shows higher retrieval within each context. The comparisons are diagnostic rather than a model leaderboard: survival of an endpoint after perturbation information is removed narrows its interpretation toward shared response structure rather than perturbation identity. Gray reference markers denote the theoretical expectation under random ranking for the corresponding candidate universe.

**Figure 4. Matched-target GEARS context-transfer stress test.** Shared-target analysis compares within-context and cross-context audit-delta Pearson for K562-to-RPE1 (n=150 matched targets) and RPE1-to-K562 (n=148 matched targets). Labels show paired drops and perturbation-level bootstrap 95% intervals. Figure 4 uses QC and matched-transfer language only.

**Figure 5. STATE shows partial cross-architecture transfer degradation with endpoint heterogeneity.** STATE K562-to-RPE1 matched targets (n=15) show lower cross-context audit-delta Pearson, Spearman, and cosine. UER50 has an interval crossing zero, sign-flip rate is worse cross context, and common-candidate retrieval from frozen centroids is reported as an exploratory sensitivity panel.
