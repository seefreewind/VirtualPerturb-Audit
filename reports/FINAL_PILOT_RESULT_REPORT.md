# Final Pilot Result Report

Execution date: 2026-08-23
Source task list: `reports/NEXT_TASKS_AND_DELIVERABLES.md` (updated 2026-08-22)

## Summary

All feasible CPU tasks in the handoff were executed on this Mac. GEARS full evaluations completed for all three audit splits (L1, L2, L3) at 20 epochs, seed 1, `essential` perturbation graph, on CPU. Downstream summary tables, figures, gemgroup null-envelope sensitivity, project reports, and a final commit were produced. `pytest` passes 10/10.

## GEARS Full Runs Completed

| Split | Run folder | Test perturbations | Elapsed (s) | Status |
|---|---|---|---|---|
| L1 | `results/pilot/gears_20260822T065552Z/` | 55 | 18,284 | `COMPLETED_GEARS` / `COMPLETED_GEARS_EVALUATION` |
| L2 | `results/pilot/gears_20260822T122126Z/` | 40 | 17,987 | `COMPLETED_GEARS` / `COMPLETED_GEARS_EVALUATION` |
| L3 | `results/pilot/gears_20260822T172146Z/` | 25 | 21,057 | `COMPLETED_GEARS` / `COMPLETED_GEARS_EVALUATION` |

Each run folder contains `gears_metrics.csv`, `gears_delta_centroids.pt`, `gears_perturbation_retrieval.csv`, and strict `metadata.json`. Model weights are git-ignored; all other artifacts are committed.

## GEARS Full Metrics (completion criteria met)

| Split | n | Pearson Δ (95% CI) | UER@50 | Sign flip | Retrieval top-1 | top-5 | MRR | BNS status |
|---|---|---|---|---|---|---|---|---|
| L1 | 55 | 0.9887 (0.9860, 0.9914) | 0.0 | 0.0 | 0.200 | 0.491 | 0.328 | UNVERIFIED |
| L2 | 40 | 0.9838 (0.9795, 0.9875) | 0.0 | 0.0 | 0.075 | 0.150 | 0.147 | UNVERIFIED |
| L3 | 25 | 0.9843 (0.9781, 0.9896) | 0.0 | 0.0 | 0.080 | 0.320 | 0.207 | UNVERIFIED |

- `metadata.json` has `audit_split: L2/L3`, `status: COMPLETED_GEARS`, and `summary_row.status: COMPLETED_GEARS_EVALUATION` for all three runs.
- `pilot_summary.csv` contains `GEARS_cell_gears_0.1.2` rows for splits L1, L2, L3 all with `status: COMPLETED_GEARS_EVALUATION`.

## Context vs Baselines and Probes

GEARS delta-Pearson is very high on all splits (≈0.98-0.99), well above baselines (B3 additive L1 0.77, L2/L3 0.43/0.35) and falsification probes (FP-1/FP-2/FP-3 L1 0.51/0.77/0.22). However, GEARS perturbation retrieval collapses under stricter holdouts:

- Top-1 retrieval: L1 0.20 → L2 0.075 → L3 0.08; MRR 0.328 → 0.147 → 0.207.
- Baselines with seen components (B3/FP-2) show the same collapse pattern (L1 0.58 → L2 0.03 → L3 0.04 top-1), supporting the shortcut/leakage interpretation: exact-condition identity is recoverable under perturbation-held-out splits, but strict component-held-out (L2) and HGNC gene-family holdout (L3) cuts retrieval while delta-Pearson remains high.

This dissociation (stable correlation + collapsing retrieval) is the headline pilot signal for the manuscript.

## Null-Envelope Sensitivity (GEARS rows added, P1)

`results/pilot/null_envelope_sensitivity.csv` and table 6 now include `COMPLETED_SENSITIVITY_GEARS_EVALUATION` rows:

| Split | n | UER@50 vs gemgroup null (q95) |
|---|---|---|
| L1 | 55 | 0.172 |
| L2 | 40 | 0.262 |
| L3 | 25 | 0.235 |

GEARS raw predictions were converted to audit-delta space via the audit control mean; condition names were canonicalized (`ctrl+X` vs `X+ctrl`). Note the GEARS-run test vocabulary differs slightly from the audit splitter's test sets (e.g., L1: 55 vs 57 perturbations); metrics are computed within the GEARS-run vocabulary. This sensitivity is batch-like (GEO `gemgroup`) metadata, not a replicate-derived BNS upper bound.

## Rebuilt Downstream Outputs

- `results/pilot/pilot_summary.csv` — GEARS full rows for L1/L2/L3.
- `results/pilot/perturbation_retrieval.csv` — GEARS retrieval rows.
- `results/pilot/null_envelope_sensitivity.csv` — GEARS rows added.
- `results/tables/table2_models.*` — GEARS status updated to `FULL_EVALUATION_COMPLETED_L1_L2_L3_PILOT`.
- `results/tables/table5_primary_pilot_metrics.*`, `table6_null_envelope_sensitivity.*` — rebuilt with GEARS rows.
- `figures/main/pilot_truthfulness.*`, `pilot_hallucination.*` — rebuilt; bounded smoke rows are excluded from performance plots.
- Verification: `python3 scripts/build_tables.py` and `python3 scripts/build_figures.py` complete without error; `python3 -m pytest tests` → 10 passed.

## Reports Updated

- `reports/PILOT_DECISION.md` — decision updated to `PROVISIONAL_GO_FOR_BASELINE_AUDIT; GEARS_FULL_EVALUATION_COMPLETED_PILOT (BNS unverified)`; GEARS rows interpretable only with `bns_status: UNVERIFIED`.
- `PROJECT_STATUS.md` — completed/failed/risks/interpretation updated; smoke-vs-full distinction maintained.
- `CHANGELOG.md` — 2026-08-23 entry added.
- `NEXT_ACTIONS.md` — reprioritized around the L2/L3 retrieval-collapse finding and BNS-verification constraint.

## Failure Provenance (P2)

The first L2 attempt (`results/pilot/gears_20260822T120129Z/`) is kept with explicit `status: FAILED_GEARS` and `traceback.txt` (`BrokenPipeError` after 825 s, stdout pipe interruption; not a model/data failure). It cannot be mistaken for a completed result. The failed CUDA attempt (`gears_20260822T065423Z/`) is likewise retained with explicit failed status.

## Commit

- `a2885cf` "Complete GEARS L1/L2/L3 full CPU evaluation and rebuild downstream outputs" — 46 files (GEARS run metadata/metrics/centroids/retrieval, updated tables/figures/reports/scripts).
- Git worktree clean; ignored items are raw data, venv, logs, and model-weight directories.

## Interpretation Guardrails Applied

- Bounded smoke rows are not treated as model performance.
- GEARS rows are interpreted only for `COMPLETED_GEARS_EVALUATION` status.
- Replicate-derived BNS remains `UNVERIFIED` (no true replicate label found).
- GEO `gemgroup` is treated as batch-like sensitivity metadata, not a biological replicate.
- Uncertainty is reported at perturbation level (bootstrap), not inflated via cell-level counts.