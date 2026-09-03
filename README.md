# VirtualPerturb-Audit

## What problem it solves

VirtualPerturb-Audit is a reproducible framework for stress-testing perturbation-response model outputs. It helps reviewers and model developers distinguish global expression agreement from perturbation identity, matched-context transfer, unsupported-effect behavior, and directional fidelity.

## Audit workflow

1. Freeze dataset, split, preprocessing, checkpoint, target universe, gene universe, and code state.
2. Compute raw-space and audit-delta agreement metrics.
3. Evaluate perturbation-specific retrieval within a declared candidate universe.
4. Compare simple baselines and target-information-restricted falsification probes.
5. Evaluate matched-target context transfer, unsupported-effect rate, and sign-flip behavior.
6. Assign a bounded claim profile rather than a single model score.

## Required inputs

Supported inputs are cell-level AnnData objects, target-level pseudobulk matrices, or precomputed prediction matrices/centroids with declared perturbation labels, control labels, context labels, gene identifiers, and candidate universes. The public repository is a slim reproducibility deposit containing code, compact frozen result tables, and a minimal example; submission manuscripts and review-package files are distributed separately through the archived record.

## Quick start

```bash
git clone https://github.com/seefreewind/VirtualPerturb-Audit.git
cd VirtualPerturb-Audit
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python examples/minimal_audit/run_minimal_audit.py
```

If full checkout is slow on a weak network, the lightweight reviewer workflow can be checked out with sparse clone:

```bash
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/seefreewind/VirtualPerturb-Audit.git
cd VirtualPerturb-Audit
git sparse-checkout init --cone
git sparse-checkout set README.md requirements.txt examples scripts results/tables submission/SOURCE_DATA_MANIFEST.tsv
git checkout
```

## Minimal example

The toy example in `examples/minimal_audit/` writes `minimal_audit_table.csv` with audit-delta Pearson, retrieval rank, MRR contribution, UER@2, and sign-flip rate. It demonstrates audit mechanics only and is not manuscript evidence.

## Baseline and probe naming

In the frozen single-context Replogle R-L1 analyses, B1, B2, B5, and FP1 collapse to the same target-blind mean-delta construction. B2 falls back to B1 because no additional within-task context covariate is available; B5 and FP1 differ by interpretive role rather than prediction vector.

FP3 randomly assigns training-target deltas to test perturbations with replacement under the frozen seed in Figure 3; the Norman FP3 20-randomization summary is a separate source table and is not used as Figure 3 uncertainty.

Legacy internal module names do not imply that UER is a validated biological hallucination metric; UER is a threshold-defined unsupported-effect sensitivity endpoint.

## Reproducing manuscript figures

Frozen manuscript-facing tables are in `results/tables/`. Main figure builders read those frozen tables and write PNG, SVG, and PDF files under a locally generated `figures/main/` directory:

```bash
python scripts/build_figure1_v2.py
python scripts/build_figure2_v2.py
python scripts/build_figure3_v2.py
python scripts/build_figure4_v2.py
python scripts/build_figure5_v2.py
```

## Expected outputs

Expected local outputs include `results/tables/FINAL_MANUSCRIPT_NUMERIC_REGISTRY.tsv` and regenerated Figure 1-5 files under `figures/main/`. Word manuscripts, PDF review copies, rendered QC pages, and submission-package folders are intentionally excluded from the GitHub repository.

## Data provenance

Norman perturbation data were used through a GEARS-compatible processed mirror derived from Norman et al. Replogle analyses used GEARS-compatible filtered K562 and RPE1 essential-screen objects derived from Replogle et al. Raw third-party datasets are not redistributed in this repository; obtain them from the original sources listed in `DATASET_PROVENANCE.md`.

## Known limitations

The Replogle demonstration uses filtered GEARS-compatible essential-screen data. UER is an internal sensitivity endpoint. GEARS R-L4 is an adapter-style cross-context inference stress test. STATE matched transfer uses 15 shared targets and supports partial, endpoint-heterogeneous cross-architecture interpretation.

## Citation

Code and compact derived result tables are available at https://github.com/seefreewind/VirtualPerturb-Audit. The archived release DOI is https://doi.org/10.5281/zenodo.22232963. Use `CITATION.cff` for citation metadata.

## License

MIT.
