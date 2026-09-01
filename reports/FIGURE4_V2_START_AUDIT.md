# Figure 4 v2 Start Audit

Core conclusion: Substantial cross-context degradation persists after matching the perturbation-target universe.
Archetype: quantitative grid
Target journal: Cell Reports Methods

## Located current Figure 4

- Source file: `scripts/build_crm_submission_package.py` lines 172-192.
- Current style: grouped bar chart with within and cross bars.
- Current label needing replacement: `Matched-target Pearson`.
- Current title needing replacement: `Matched targets do not rescue GEARS cross-context transfer`.
- Archived old Figure 4 copies under `figures/archive/` before writing v2 outputs.

## Input tables

- `results/tables/replogle_matched_rl1_rl4_sensitivity.csv` for frozen summary estimates and paired bootstrap intervals.
- `results/tables/replogle_matched_rl1_rl4_target_level.csv` for frozen matched-target values.
- `results/tables/replogle_matched_target_registry.tsv` for matched-target provenance.

## Numeric integrity

- K562 -> RPE1: frozen primary values verified; target-level n=150.
- RPE1 -> K562: frozen primary values verified; target-level n=148.

## Primary plotted summary values

| direction                   |   n_targets |   within_estimate |   cross_estimate |   paired_difference |   ci_low |   ci_high | difference_definition   |
|:----------------------------|------------:|------------------:|-----------------:|--------------------:|---------:|----------:|:------------------------|
| K562_within_vs_K562_to_RPE1 |         150 |           0.28122 |        -0.007049 |            0.288269 | 0.255949 |  0.320587 | within_minus_cross      |
| RPE1_within_vs_RPE1_to_K562 |         148 |           0.5501  |         0.002084 |            0.548016 | 0.514575 |  0.580184 | within_minus_cross      |
