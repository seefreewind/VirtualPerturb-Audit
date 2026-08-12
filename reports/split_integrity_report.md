# Split Integrity Report

Status: **PASS_ON_TOY_TESTS; BLOCKED_PENDING_REAL_DATA**

Implemented checks:

- `assert no_exact_cell_overlap`
- `assert no_forbidden_perturbation_overlap`
- `assert no_group_overlap`
- `assert training_only_scaler`

The checks pass on toy unit tests (`4 passed`, 2026-08-12). They have not yet been run on the real Norman AnnData file.

## CLI Smoke Test

`python3 -m src.run --config configs/norman_gears_L1_seed1.yaml` correctly failed loud because `data/raw/norman/perturb_processed.h5ad` is absent, and wrote blocked run metadata under `results/pilot/`.
