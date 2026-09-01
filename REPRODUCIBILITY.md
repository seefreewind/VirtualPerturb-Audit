# Reproducibility

## Hardware and Operating Systems

- Local manuscript/finalization host: macOS on Apple Silicon.
- GEARS full CPU runs: Mac CPU, long-running jobs taking approximately 5-6 hours per Norman split and longer for Replogle R-L1.
- STATE Phase 2C full runs: CUDA-capable Linux GPU server.

## GPU and CUDA

STATE confirmatory execution requires a CUDA-capable Linux environment. The completed Phase 2C run used a rented GPU server with NVIDIA driver/CUDA support sufficient for STATE. Exact server details and run manifests are retained in `results/tables/state_phase2c_run_manifest.csv` and Phase 2C reports.

## Memory and Disk

Replogle and STATE artifacts require tens of GB of working storage. Raw Phase 2C h5ad outputs are local but not copied into the submission package.

## Python and Packages

Post-processing and CRM finalization use the project environment:

```bash
environment/state-postprocess-venv/bin/python
```

Key packages include pandas, matplotlib, python-docx, openpyxl, PyTorch, Scanpy, AnnData, scikit-learn, and SciPy. Final public release should include a pinned environment export.

## Seeds and Task Names

- GEARS seed: 1 for frozen full runs.
- GEARS R-L1 tasks: `R-L1-K562`, `R-L1-RPE1`.
- GEARS R-L4 tasks: `R-L4-K2R`, `R-L4-R2K`.
- STATE Phase 2C tasks: `S1_norman_l1`, `S2_norman_l2`, `S3_replogle_k562_rl1`, `S4_replogle_k2r_rl4`.

## Expected Result Files

- `results/tables/replogle_matched_rl1_rl4_sensitivity.csv`
- `results/tables/replogle_rl1_rl4_gears_comparison.csv`
- `results/tables/state_phase2c_primary_metrics.csv`
- `results/tables/state_transfer_drop.csv`
- `results/tables/gears_state_primary_comparison.csv`

## Public Release

- GitHub repository: https://github.com/seefreewind/VirtualPerturb-Audit
- The repository includes source code, manuscript-facing derived result tables, figure scripts, generated figures, reports, and manuscript drafts.
- Raw downloaded datasets, large model outputs, external dependency checkouts, and local runtime environments are intentionally excluded.

## Figure Regeneration

```bash
environment/state-postprocess-venv/bin/python scripts/finalize_crm_submission_v11.py
```

## Known Non-Portable Steps

- Complete Replogle Figshare+ command-line access was blocked by HTTP 403 in the frozen project state.
- Full GEARS training is slow and terminal-lifetime sensitive on CPU.
- STATE execution depends on a CUDA-capable Linux server and local adapter paths.
- Archive DOI and final environment export remain manual release tasks.
