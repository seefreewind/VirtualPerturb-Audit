# METHODS v0.2

## Phase 2B Matched-Target Sensitivity

The matched-target sensitivity analysis reused frozen GEARS outputs from the Replogle Phase 2A within-context and cross-context runs. No completed GEARS run was retrained. For each transfer direction, perturbation targets were restricted to the intersection of the source-context within split and the corresponding cross-context evaluation split. Metrics were recomputed on this matched target set to separate target-composition effects from context-transfer effects.

For K562-to-RPE1, the source-context matched set contained 150 perturbation targets. For RPE1-to-K562, the source-context matched set contained 148 perturbation targets. The analysis reported paired within-minus-cross differences for correlation and retrieval metrics, and cross-minus-within penalties for error and uncertainty/error-rate metrics. Bootstrap intervals used target-level resampling.

Common-candidate retrieval was recomputed by restricting the candidate pool to the same matched target set before ranking. This analysis tests whether retrieval deterioration is driven by a larger or different candidate universe.

## Phase 2B Second-Model Feasibility

scGPT and STATE were audited as candidate second models. scGPT was rejected for local Phase 2B execution because a reproducible import and smoke environment could not be established without replacing the frozen GEARS dependency stack. STATE installed successfully through the official `uv tool install arc-state` route and passed command-line and one-step smoke tests. The full deep STATE confirmatory matrix was not launched locally because the local trainer used CPU and official full-run settings require tens to hundreds of thousands of steps. Smoke outputs were retained as executable-chain evidence only and were excluded from performance tables.

## Phase 2C STATE Cross-Architecture Audit

Phase 2C evaluated STATE as an independent deep architecture in a GPU/Linux environment. The four locked tasks were Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4. The GPU run used synchronized STATE prediction outputs from `results/state/full_phase2c_20260829T131235Z` and did not modify frozen GEARS splits, registries, or Phase 2A/2B primary metrics.

STATE predictions and paired observed expression matrices were evaluated at the perturbation-target level. For each task, predicted and observed cells were grouped by normalized perturbation label. The project normalization rule removes explicit control partners, so labels such as `ctrl+X` and `X` are evaluated as target `X`. This produced 53 normalized Norman L1 targets, 28 normalized Norman L2 targets, 216 Replogle K562 R-L1 targets, and 73 Replogle K562-to-RPE1 R-L4 targets. The frozen split-alignment audit remained fully aligned at the condition level.

The primary STATE metric space was audit-delta expression. For each target, the real control mean in the corresponding prediction pair was subtracted from both the predicted target mean and the observed target mean. The R-L4 task used the target-context control baseline and is reported as `target_control_audit_delta`, matching the GEARS R-L4 adapter convention. A secondary `gears_raw` space was also retained for compatibility checks where both predicted and observed controls were available.

The endpoint family matched the GEARS audit: delta-Pearson, Spearman, RMSE, cosine similarity, retrieval Top1/Top5/MRR, UER@20/50/100, and sign-flip rate. Retrieval was computed by ranking observed perturbation delta centroids by cosine similarity to each predicted perturbation delta centroid. Perturbation-level bootstrap intervals used 2,000 resamples. BNS remained unverified, and UER was treated as sensitivity-only because the null threshold was derived from the median absolute observed delta rather than an independently verified biological null.

## Data Scope

All Replogle analyses use GEARS-compatible filtered essential-screen data. Complete Figshare+ processed Replogle objects were not available through the command-line route used in this project, and replicate-bounded negative sampling remains unverified.
