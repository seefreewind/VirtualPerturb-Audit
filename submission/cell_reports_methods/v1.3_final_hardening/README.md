# VirtualPerturb-Audit

VirtualPerturb-Audit is a reproducible framework for stress-testing perturbation-response model outputs. It is not a new perturbation predictor and does not require GEARS or STATE as dependencies; those models are worked examples in the manuscript package.

## What It Does

The framework freezes inputs, computes global fit, tests perturbation-specific retrieval, compares simple baselines and falsification probes, and assigns bounded claims from matched transfer, UER, and sign-flip endpoints.

## Why Single Metrics Are Insufficient

High raw expression similarity can coexist with weak perturbation identity recovery or poor cross-context stability. VirtualPerturb-Audit separates raw-space agreement, control-subtracted response agreement, retrieval, unsupported-effect sensitivity, sign-direction errors, and transfer behavior.

## Audit Stages

1. Freeze dataset, split, preprocessing, checkpoint, and code state.
2. Compute raw-space and audit-delta global-fit metrics.
3. Compute perturbation retrieval with a declared candidate universe.
4. Compare B0-B5 baselines and FP1-FP3 falsification probes.
5. Assign endpoint-specific claims from matched transfer, UER@K, and sign-flip behavior.

## Required Inputs

See `manuscript/VIRTUALPERTURB_INPUT_CONTRACT.md`. Supported inputs are cell-level AnnData objects, target-level pseudobulk matrices, and precomputed prediction matrices or centroids with declared gene and target universes.

## Quick Start

```bash
python examples/minimal_audit/run_minimal_audit.py
```

## Example Output

The minimal example writes `examples/minimal_audit/minimal_audit_table.csv`. It demonstrates audit mechanics only and is not manuscript evidence.

## Reproducing Manuscript Analyses

Manuscript-facing frozen result tables are in `results/tables/`. The v1.3 hardening script is:

```bash
python scripts/build_crm_v13_final_hardening.py
```

No model training is performed by the v1.3 script.

## Known Limitations

The Replogle demonstration uses GEARS-compatible filtered essential-screen data. UER is an internal sensitivity endpoint. A replicate-derived empirical performance bound was not established. GEARS R-L4 is a cross-context inference adapter. STATE matched transfer uses 15 shared targets and is interpreted as partial, endpoint-heterogeneous support.

## Citation

Use `CITATION.cff` after the public repository and archive DOI are finalized.
