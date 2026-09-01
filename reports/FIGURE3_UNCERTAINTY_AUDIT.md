# Figure 3 Uncertainty Audit

- Audit-delta Pearson: valid frozen perturbation-level bootstrap intervals are present for all six plotted rows.
- MRR: GEARS rows contain frozen bootstrap intervals in `results/replogle/gears_rl1_summary.csv`; probe rows in `results/tables/replogle_gears_vs_probes.csv` do not provide frozen MRR confidence intervals.
- Decision: show thin error bars only for Panel A Pearson, where all six rows have comparable frozen intervals. Do not fabricate Panel B uncertainty.

| context   | method         |   pearson_ci_low |   pearson_delta |   pearson_ci_high |   mrr_ci_low |       mrr |   mrr_ci_high | uncertainty_status                                                          |
|:----------|:---------------|-----------------:|----------------:|------------------:|-------------:|----------:|--------------:|:----------------------------------------------------------------------------|
| K562      | Mean-effect    |         0.361379 |        0.386866 |          0.409877 |  nan         | 0.0273578 |   nan         | BOOTSTRAP_PERTURBATION_LEVEL for Pearson; no frozen MRR CI in summary table |
| K562      | Label-shuffled |         0.130197 |        0.153189 |          0.176391 |  nan         | 0.0334967 |   nan         | BOOTSTRAP_PERTURBATION_LEVEL for Pearson; no frozen MRR CI in summary table |
| K562      | GEARS          |         0.255754 |        0.283983 |          0.310721 |    0.0332292 | 0.0497239 |     0.0688635 | BOOTSTRAP_PERTURBATION_LEVEL                                                |
| RPE1      | Mean-effect    |         0.604313 |        0.634888 |          0.663325 |  nan         | 0.0204277 |   nan         | BOOTSTRAP_PERTURBATION_LEVEL for Pearson; no frozen MRR CI in summary table |
| RPE1      | Label-shuffled |         0.357078 |        0.386519 |          0.414824 |  nan         | 0.0189678 |   nan         | BOOTSTRAP_PERTURBATION_LEVEL for Pearson; no frozen MRR CI in summary table |
| RPE1      | GEARS          |         0.434463 |        0.461604 |          0.487831 |    0.0166122 | 0.0261673 |     0.0384685 | BOOTSTRAP_PERTURBATION_LEVEL                                                |
