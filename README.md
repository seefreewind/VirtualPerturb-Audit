# VirtualPerturb-Audit

VirtualPerturb-Audit is a model-agnostic framework for stress-testing perturbation-response model claims. It separates global transcriptomic fit from perturbation identity, unsupported-effect behavior, sign-direction errors, leakage risk, and matched-target context transfer.

## Quick Start

Run the minimal toy audit:

```bash
cd examples/minimal_audit
python run_minimal_audit.py
```

Regenerate the Cell Reports Methods v1.2 method-strengthening package from frozen outputs:

```bash
environment/state-postprocess-venv/bin/python scripts/build_crm_v12_method_strengthening.py
```

## Audit Stages

1. Freeze inputs: dataset version, target universe, gene universe, checkpoint, split, preprocessing, predictions, and evaluation code.
2. Global-fit audit: raw-space Pearson, audit-delta Pearson, Spearman, RMSE, and cosine.
3. Perturbation-specific audit: Top1, Top5, and MRR retrieval.
4. Falsification audit: no-change, mean-effect, perturbation-blind, cell-state-blind, and label-shuffled probes.
5. Transfer and unsupported-effect audit: context holdout, matched-target comparison, UER@K, and sign-flip rate.

## Inputs

- Expression matrices and model predictions.
- Perturbation, control, and context labels.
- Split assignments and frozen preprocessing.
- Target and gene universes.

## Outputs

- Endpoint-specific result tables under `results/tables/`.
- Main and supplementary manuscript files under `manuscript/`.
- Figures under `figures/main/` and `figures/supplementary/`.
- Reporting and deposition audits under `reports/`.
- Minimal demonstration under `examples/minimal_audit/`.

## Figures

Figure 1 should present the five-stage audit protocol. Figures 2-5 summarize metric divergence, probe controls, matched GEARS transfer, and independent STATE analysis. Figure files are retained as PNG/SVG/PDF assets.

## Known Limitations

- Replogle scope is GEARS-compatible filtered essential-screen data.
- Biological-null score could not be verified from validated biological replicate metadata.
- UER is an internal sensitivity measure, not experimental proof of unsupported biology.
- GEARS R-L4 is a cross-context inference adapter.
- STATE support is partial and endpoint-heterogeneous.
- Current outputs are not a universal model leaderboard.
