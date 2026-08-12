# Methods Working Draft

## Datasets

The pilot is designed for Norman et al. K562 CRISPRa Perturb-seq. Dataset-specific counts, perturbation numbers, and preprocessing details will be inserted only from program outputs after local acquisition and QC.

## Data Preprocessing

All fit-derived preprocessing must be training-only. Current code includes a training-only scaler audit utility. HVG/PCA fitting must be recorded with split-specific fit indices before main analyses.

## Model Implementation

The first complex model target is GEARS using official code and official processed data where available. Any source or adapter modification must be recorded in the model card.

## Baseline Models

Implemented baselines include no-change, global perturbed mean, context-matched perturbed mean, and PCA/Ridge.

## Leakage Taxonomy

The framework covers LKG-1 to LKG-6. The pilot currently implements exact cell overlap, perturbation holdout, component holdout, group overlap checks, and training-only preprocessing checks.

## Split Design

Pilot splits are L0 random-cell, L1 perturbation-held-out, and L2 component-held-out.

## Evaluation Metrics

Implemented endpoints include Pearson/Spearman/RMSE/MAE/cosine, perturbation-centroid retrieval, and bound-normalized score.

## Hallucination Metrics

Implemented endpoints include UER@K and Sign Flip Rate. Null envelopes must be estimated from real controls or replicate variation before these metrics are interpreted.

## Statistical Analysis

Paired bootstrap is implemented with perturbation-level sampling support. Main analyses will use perturbation or perturbation-context pairs, not individual cells, as the statistical unit.

## Software/Reproducibility

Each run writes timestamp, config, split hash, and dataset dimensions. Git commit, CUDA/GPU, dataset checksum, and model checkpoint fields will be added when the first real pilot run is executed.

