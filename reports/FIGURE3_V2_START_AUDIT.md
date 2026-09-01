# Figure 3 v2 Start Audit

Core conclusion: Response agreement can remain substantial after removing or scrambling perturbation-specific information, whereas retrieval behaves as a more target-specific endpoint in these frozen within-context tasks.
Archetype: quantitative grid
Target journal: Cell Reports Methods

## Located current Figure 3

- Source file: `scripts/build_crm_submission_package.py` lines 150-169.
- Current style: two-panel vertical bar plot with repeated context labels on the x-axis.
- Current labels: mean, shuffled, GEARS; Panel A title used `Global perturbation effect`.
- Current axis limits: Panel A autoscaled from bar values; Panel B autoscaled from MRR values.
- Archived old figure files under `figures/archive/` before writing v2 copies.

## Input tables

- `results/tables/replogle_gears_vs_probes.csv` for frozen probe and plotted summary values.
- `results/replogle/gears_rl1_summary.csv` for frozen GEARS audit-delta summary values.
- `results/replogle/replogle_perturbation_retrieval.csv` and GEARS per-run retrieval files for candidate-universe auditing.

## Plotted values

| context   | method         | model                          |   pearson_delta |      mrr | source                                      |
|:----------|:---------------|:-------------------------------|----------------:|---------:|:--------------------------------------------|
| K562      | Mean-effect    | B1_global_perturbed_mean       |        0.386866 | 0.027358 | results/tables/replogle_gears_vs_probes.csv |
| K562      | Label-shuffled | FP3_label_shuffled_mean_effect |        0.153189 | 0.033497 | results/tables/replogle_gears_vs_probes.csv |
| K562      | GEARS          | GEARS_cell_gears_0.1.2         |        0.283983 | 0.049724 | results/replogle/gears_rl1_summary.csv      |
| RPE1      | Mean-effect    | B1_global_perturbed_mean       |        0.634888 | 0.020428 | results/tables/replogle_gears_vs_probes.csv |
| RPE1      | Label-shuffled | FP3_label_shuffled_mean_effect |        0.386519 | 0.018968 | results/tables/replogle_gears_vs_probes.csv |
| RPE1      | GEARS          | GEARS_cell_gears_0.1.2         |        0.461604 | 0.026167 | results/replogle/gears_rl1_summary.csv      |
