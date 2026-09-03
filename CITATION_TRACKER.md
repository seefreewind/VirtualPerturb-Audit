> Historical project record; not authoritative for the submission state. See `README.md` and `results/tables/FINAL_MANUSCRIPT_NUMERIC_REGISTRY.tsv` for current manuscript-facing status.

# Citation Tracker

Search date: 2026-08-12.

## Norman et al. 2019

- Title: Exploring genetic interaction manifolds constructed from rich single-cell phenotypes
- Year: 2019
- Journal / preprint: Science
- DOI: 10.1126/science.aax4438
- URL: https://www.science.org/doi/10.1126/science.aax4438
- Dataset: K562 CRISPRa Perturb-seq single and combinatorial perturbations
- Model: none; experimental dataset
- Evaluation metric: genetic interaction and transcriptomic manifold analyses
- Split strategy: not a virtual perturbation benchmark split
- Main finding: rich single-cell phenotypes can map genetic interaction manifolds
- Relevant limitation: later ML uses require independent leakage-aware split design
- Relevance to VirtualPerturb-Audit: primary pilot dataset

## Replogle et al. 2022

- Title: Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq
- Year: 2022
- Journal / preprint: Cell
- DOI: 10.1016/j.cell.2022.05.013
- URL: https://www.cell.com/cell/fulltext/S0092-8674(22)00597-9
- Dataset: K562 and RPE1 CRISPRi Perturb-seq
- Model: none; experimental dataset
- Evaluation metric: genome-scale perturbation transcriptional phenotypes
- Split strategy: not primarily a virtual perturbation benchmark
- Main finding: genome-scale CRISPRi Perturb-seq maps genotype-phenotype landscapes
- Relevant limitation: processed/public-release chronology must be separated from experiment and paper dates
- Relevance to VirtualPerturb-Audit: planned cross-context and dataset-held-out evaluation

## GEARS

- Title: Predicting transcriptional outcomes of novel multigene perturbations with GEARS
- Year: 2023
- Journal / preprint: Nature Biotechnology
- DOI: 10.1038/s41587-023-01905-6
- URL: https://www.nature.com/articles/s41587-023-01905-6
- Dataset: Norman, Adamson, Dixit, Replogle-style Perturb-seq datasets
- Model: graph-enhanced perturbation response predictor
- Evaluation metric: transcriptomic prediction and genetic interaction subtype metrics
- Split strategy: simulation/combinatorial splits in official implementation
- Main finding: graph-informed model predicts transcriptional outcomes for unseen perturbation combinations
- Relevant limitation: audit must distinguish model performance under original benchmark splits from stricter leakage ladders
- Relevance to VirtualPerturb-Audit: first complex pilot model

## scGPT

- Title: scGPT: toward building a foundation model for single-cell multi-omics using generative AI
- Year: 2024
- Journal / preprint: Nature Methods
- DOI: UNVERIFIED
- URL: https://github.com/bowang-lab/scGPT
- Dataset: broad single-cell corpora; perturbation tutorial uses GEARS-style loader
- Model: transformer foundation model
- Evaluation metric: task-specific; perturbation prediction tutorials report expression prediction metrics
- Split strategy: UNVERIFIED
- Main finding: single-cell foundation model supports multiple downstream tasks
- Relevant limitation: pretraining corpus overlap must be audited before contamination claims
- Relevance to VirtualPerturb-Audit: planned second-stage foundation model

## STATE / Virtual Cell Challenge

- Title: STATE
- Year: 2025/2026 UNVERIFIED
- Journal / preprint: UNVERIFIED
- DOI: UNVERIFIED
- URL: https://github.com/ArcInstitute/state
- Dataset: Virtual Cell Challenge context
- Model: perturbation response model across diverse contexts
- Evaluation metric: UNVERIFIED
- Split strategy: UNVERIFIED
- Main finding: UNVERIFIED
- Relevant limitation: release/checkpoint/corpus evidence required
- Relevance to VirtualPerturb-Audit: planned later model and temporal-clean candidate

## Open Registry Gaps

The following topics are registered but require primary-source citation completion before manuscript use: scFoundation, Geneformer perturbation use, Systema, PerturBench, scArchon, Signal-Bounds-Baselines, VCBench, in-the-wild perturbation benchmark, scContam, perturbation-specific evaluation, pretraining contamination, membership inference, temporal holdout, biological hallucination or unsupported generation.
