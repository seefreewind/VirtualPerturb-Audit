# Phase 2A RL1 Config Deviations

Date: 2026-08-23

## Purpose

Document every deliberate difference between the frozen Norman GEARS pilot configuration and the Replogle R-L1 full-run configuration, per the audit rule that any adjustment must be recorded with rationale and comparability impact.

## Frozen Norman GEARS Pilot Configuration (reference)

Source: `results/pilot/gears_*` metadata; official `cell-gears==0.1.2` defaults via `GEARS.train()`.

| Field | Norman pilot value |
|---|---|
| epochs | 20 |
| seed | 1 |
| batch_size / test_batch_size | 16 / 16 |
| device | cpu |
| optimizer | Adam (lr 1e-3, weight_decay 5e-4) |
| scheduler | StepLR (step 1, gamma 0.5) |
| hidden_size | 64 |
| GO GNN layers / gene GNN layers | 3 / 3 |
| decoder_hidden_size | 128 |
| num_similar_genes_go_graph | 20 |
| num_similar_genes_co_express_graph | 20 |
| coexpress_threshold | 0.4 |
| pert_graph | essential (`essential_all_data_pert_genes.pkl`) |
| GO graph | filtered GO tensor (GO edges restricted to perturbation node map + self edges) |
| co-expression graph | GEARS-inferred from train control cells (train-only) |
| metric space | GEARS-internal vocabulary; Pearson/retrieval computed in raw GEARS space (no test ctrl) |
| bootstrap | 200 resamples, 95% CI, perturbation-level (pilot default) |

## Replogle RL1 Full-Run Configuration (frozen)

Files:

- `configs/replogle/gears_rl1_k562_seed1.yaml`
- `configs/replogle/gears_rl1_rpe1_seed1.yaml`

| Field | Replogle RL1 value | Change vs Norman |
|---|---|---|
| epochs | 20 | none |
| seed | 1 | none |
| batch_size / test_batch_size | 16 / 16 | none |
| device | cpu | none |
| optimizer / lr / weight_decay | Adam 1e-3 / 5e-4 | none (official `GEARS.train` defaults) |
| scheduler | StepLR | none |
| hidden / layers / decoder | 64 / 3 / 3 / 128 | none |
| pert_graph | essential | none |
| GO graph | filtered GO tensor with official-style top-k=20 per-target trimming + self edges (before trim ~12.1M edges; after trim ~207k) | **trim added**; see item 4 below |
| co-expression graph | GEARS-inferred from train control cells | none |
| split | R-L1 via `assign_replogle_l1_context_perturbation_holdout` seed 1, then rebuilt inside GEARS-filtered vocabulary | split-dict construction mirrors the Norman custom-split convention (split written from GEARS-filtered adata so no condition is lost to `filter_pert_in_go`); frozen split hashes verified (`e9fcaf7afdb972e4`, `288d45dbeb512ce5`) |
| bootstrap | 2000 resamples, 95% CI, perturbation-level | **200 -> 2000**; this phase locks 2000 per the phase plan (section 17). Norman comparisons use already-frozen Norman rows; the difference in resample count does not change point estimates, only CI width. Documented for transparency; Norman rows are not recomputed. |
| metric spaces | two exported spaces: `gears_raw` (exact Norman convention) and `audit_delta` (subtract audit control mean for baseline/probe comparability) | **added** `audit_delta` space; the `gears_raw` space is bit-for-bit the same convention as Norman so cross-dataset rows remain directly comparable |
| inference | full test loader, all test conditions within GEARS vocabulary | none |
| training log | captured GEARS stderr telemetry into `training_log.csv` | added; observation-only, official `model.train()` unchanged |
| checkpoint | `model.save_model(...)` | none |

## What changed, why, and comparability impact

1. **Split-dict vocabulary rebuild (engineering fix).**
   - Original behavior: custom split dict built from raw `obs.condition`; GEARS `load()` then drops cells whose condition is not in the GO gene set (`filter_pert_in_go`), producing `KeyError` inside `get_dataloader` (observed on RPE1 smoke: `AC118549.1+ctrl`).
   - Modified behavior: after `PertData.load`, the split dict is rebuilt from `pert_data.adata.obs` (GEARS-filtered vocabulary) using the same frozen per-cell split assignment.
   - Reason: same convention as the frozen Norman runs (`write_gears_custom_split(adata=pert_data.adata)`), keeping the official package unmodified.
   - Fairness impact: `set2conditions` may contain fewer test conditions than the audit-vocabulary test set (targets whose perturbation genes are absent from the essential GO graph are not evaluable by GEARS). Both counts are recorded (`n_test_targets_audit_vocabulary`, `n_test_targets_gears_vocabulary_*`). This mirrors the documented Norman behavior (55/57 L1 test perturbations) and is reported, not hidden.

2. **Bootstrap resamples 200 -> 2000.**
   - What: this phase uses 2000 resamples for Replogle rows per the phase plan.
   - Why: the phase plan (section 17) locks the statistical unit to perturbation with 2000 resamples; the Norman pilot used the pilot default of 200.
   - Comparability impact: point estimates are identical; CIs are slightly wider. Norman frozen rows are NOT recomputed; the comparison table reports Norman frozen values and Replogle 2000-resample values side by side.

3. **Two metric spaces.**
   - What: Replogle runs export both `gears_raw` (Norman convention) and `audit_delta` (baseline/probe convention) metric sets.
   - Why: `gears_raw` makes the Norman vs Replogle comparison measurement-identical; `audit_delta` makes the within-Replogle GEARS vs B0/B1/B2/B4/B5 and FP1/FP3 comparison measurement-identical (baselines are computed in audit-delta space with the same all-control mean).
   - Comparability impact: none on Norman; enables both required comparisons without redefinition.

4. **GO graph top-k trimming (engineering fix, runtime).**
   - Original behavior: the injected filtered GO tensor retained every GO edge inside the 9,853-gene perturbation node map. For Replogle essential data this produced ~12.1M edges, i.e. a ~90x denser GO GNN message-passing step than the frozen Norman runs (133,961 edges), making a 20-epoch CPU run infeasible (measured ~3 s/step with heavy swapping).
   - Modified behavior: `run_gears_replogle_rl1.py` trims the GO tensor to the top k=20 edges per target (`num_similar_genes_go_graph=20`, the official default) plus self edges, which is exactly the trimming the official GEARS `get_similarity_network` applies (`groupby('target').nlargest(k+1)`). Node set unchanged (9,853).
   - Reason: match official GEARS GO graph construction and restore Norman-comparable compute cost; without it the full run was not executable within this phase's budget.
   - Fairness impact: edges removed are the lowest-importance GO similarities per target; perturbation node set is identical; the leaning of the perturbation graph definition is unchanged in spirit and now matches the official package more closely than the previous injection. Recorded per run as `go_edges_before_trim`, `go_edges_after_trim`, `go_trim_k`, `filtered_go_nodes`.

## Items NOT changed

- No hyperparameter search; no test-set-guided tuning; no cherry-picking.
- Official `GEARS.train()` untouched; the train loop is the package code.
- Official `PertData` druid pipeline untouched; only split-dict content (a runtime argument) and output parsing were adapted.