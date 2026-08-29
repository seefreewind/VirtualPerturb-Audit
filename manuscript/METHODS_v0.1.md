# METHODS v0.1

## Phase 2B Matched-Target Sensitivity

The matched-target sensitivity analysis reused frozen GEARS outputs from the Replogle Phase 2A within-context and cross-context runs. No completed GEARS run was retrained. For each transfer direction, perturbation targets were restricted to the intersection of the source-context within split and the corresponding cross-context evaluation split. Metrics were recomputed on this matched target set to separate target-composition effects from context-transfer effects.

For K562-to-RPE1, the source-context matched set contained 150 perturbation targets. For RPE1-to-K562, the source-context matched set contained 148 perturbation targets. The analysis reported paired within-minus-cross differences for correlation and retrieval metrics, and cross-minus-within penalties for error and uncertainty/error-rate metrics. Bootstrap intervals used target-level resampling.

Common-candidate retrieval was recomputed by restricting the candidate pool to the same matched target set before ranking. This analysis tests whether retrieval deterioration is driven by a larger or different candidate universe.

## Phase 2B Second-Model Feasibility

scGPT and STATE were audited as candidate second models. scGPT was rejected for local Phase 2B execution because a reproducible import and smoke environment could not be established without replacing the frozen GEARS dependency stack. STATE installed successfully through the official `uv tool install arc-state` route and passed command-line and one-step smoke tests. The full deep STATE confirmatory matrix was not launched because the local trainer used CPU and official full-run settings require tens to hundreds of thousands of steps. Smoke outputs were retained as executable-chain evidence only and were excluded from performance tables.

## Data Scope

All Replogle analyses use GEARS-compatible filtered essential-screen data. Complete Figshare+ processed Replogle objects were not available through the command-line route used in this project, and replicate-bounded negative sampling remains unverified.
