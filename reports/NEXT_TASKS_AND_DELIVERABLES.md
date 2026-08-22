# Next Tasks and Deliverables

Updated: 2026-08-22

## Current State

The audit framework is now functional for Norman/GEARS processed data. Baselines, falsification probes, retrieval/confusion metrics, HGNC gene-family L3 holdout, seed robustness, gemgroup sensitivity, and replicate-label audit are implemented and reproducible through local scripts.

GEARS full evaluation has started on this Mac CPU. L1 completed successfully with `COMPLETED_GEARS_EVALUATION`. L2 was started but failed after about 825 seconds with `BrokenPipeError`, caused by the stdout/stderr pipe being interrupted during GEARS progress printing. This is a run-management issue, not evidence of a model or data failure.

## Completed Deliverables

| Area | Deliverable | Status |
|---|---|---|
| Baseline audit | `results/pilot/pilot_summary.csv` with B0-B5, FP1-FP3, L0/L1/L2/L3 rows | Completed |
| Retrieval audit | `results/pilot/perturbation_retrieval.csv` | Completed |
| Seed robustness | `results/pilot/seed_robustness_summary.csv` and table 8 exports | Completed |
| FP3 permutation | `results/pilot/fp3_label_shuffle_permutation_summary.csv` and table 7 exports | Completed |
| HGNC family confusion | `results/pilot/gene_family_confusion_summary.csv` and table 9 exports | Completed |
| L3 candidates | `results/pilot/l3_gene_family_holdout_candidates.csv` and table 10 exports | Completed |
| Replicate-label audit | `reports/replicate_label_audit.md` | Completed |
| GEARS L1 full run | `results/pilot/gears_20260822T065552Z/` | Completed |
| GEARS full-run handoff | `reports/GEARS_FULL_RUN_HANDOFF.md` and `scripts/run_gears_full_audit.sh` | Completed |

## Next Tasks

| Priority | Task | Why It Matters | Required Deliverables | Completion Criteria |
|---|---|---|---|---|
| P0 | Resume and complete GEARS L2 full evaluation on CPU | L2 is the strict component-held-out setting and is needed for comparison with B0-B5 and FP probes | A new `results/pilot/gears_*/` directory with `metadata.json`, `gears_metrics.csv`, `gears_delta_centroids.pt`, and `gears_perturbation_retrieval.csv` | `metadata.json` has `audit_split: L2`, `status: COMPLETED_GEARS`, and `summary_row.status: COMPLETED_GEARS_EVALUATION` |
| P0 | Run GEARS L3 full evaluation on CPU | L3 tests HGNC gene-family holdout behavior, which is central to the shortcut/leakage audit | A new `results/pilot/gears_*/` directory with L3 outputs | `pilot_summary.csv` contains a `GEARS_cell_gears_0.1.2` row for `split: L3` and `status: COMPLETED_GEARS_EVALUATION` |
| P0 | Rebuild downstream audit outputs after GEARS L2/L3 finish | GEARS outputs must be included in the same tables and figures as baselines | Updated `results/pilot/pilot_summary.csv`, `results/pilot/perturbation_retrieval.csv`, `figures/main/*`, and `results/tables/*` | `scripts/build_figures.py`, `scripts/build_tables.py`, and tests complete without error |
| P1 | Extend gemgroup-aware null-envelope sensitivity to completed GEARS rows | Current sensitivity table is baseline/probe oriented; GEARS full rows need comparable sensitivity reporting | Updated `results/pilot/null_envelope_sensitivity.csv` and table 6 exports | Table 6 contains GEARS rows for completed L1/L2/L3 splits |
| P1 | Update project decision report | The pilot decision should reflect real GEARS full results while preserving smoke/performance distinction | Updated `reports/PILOT_DECISION.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, and `NEXT_ACTIONS.md` | Reports clearly distinguish completed full GEARS rows from bounded smoke rows |
| P1 | Commit final GEARS result artifacts | Preserve reproducibility checkpoints after long CPU runs | Git commit containing small metadata/metric/centroid/retrieval files and updated reports | Git worktree is clean except ignored raw data, venv, logs, and model-weight directories |
| P2 | Decide whether to keep or archive failed L2 run metadata | Failed run is useful provenance but may clutter result folders | Either keep `results/pilot/gears_20260822T120129Z/` with explicit failed status, or move its note into a failure log | Failure is documented and cannot be mistaken for a completed result |

## Recommended Run Pattern on This Mac

Run one GEARS split at a time in the active terminal session instead of piping through long background jobs. Background/nohup attempts were unreliable in this Codex execution environment, while the foreground command successfully completed L1.

```bash
cd "/Users/zy/Documents/ChatGPT/VirtualPerturb-Audit 方案设计/VirtualPerturb-Audit"
PYTHONUNBUFFERED=1 PYTHONFAULTHANDLER=1 PYTHONPATH=. \
  environment/gears-venv/bin/python scripts/run_gears_pilot.py \
  --audit-split L2 \
  --epochs 20 \
  --batch-size 16 \
  --test-batch-size 16 \
  --device cpu
```

After L2 completes, repeat with `--audit-split L3`.

## Expected Time

The completed L1 CPU run took about 18,284 seconds, approximately 5.1 hours. L2 and L3 should be treated as multi-hour runs on this Mac. Exact duration depends on split size, validation time, test evaluation time, thermal throttling, and whether the terminal session remains alive.

## Required Final Package

When all feasible CPU GEARS runs are complete, the final package should include:

- Updated `results/pilot/pilot_summary.csv`
- Updated `results/pilot/perturbation_retrieval.csv`
- GEARS run folders with `metadata.json`, `gears_metrics.csv`, `gears_delta_centroids.pt`, and `gears_perturbation_retrieval.csv`
- Updated `results/pilot/null_envelope_sensitivity.csv`
- Updated tables under `results/tables/`
- Updated figures under `figures/main/`
- Updated `PROJECT_STATUS.md`
- Updated `reports/PILOT_DECISION.md`
- Updated `CHANGELOG.md`
- A final verification note reporting `pytest` status and which GEARS splits completed

## Interpretation Guardrails

- Do not treat bounded smoke rows as model performance.
- Interpret GEARS only for rows marked `COMPLETED_GEARS_EVALUATION`.
- Keep replicate-derived BNS marked `UNVERIFIED` unless a true replicate label is found.
- Treat GEO `gemgroup` as batch-like sensitivity metadata, not a biological replicate.
- Report perturbation-level uncertainty; do not use cell-level counts to create misleadingly small uncertainty.
