# Figure 4 Target-Level Data Audit

Status: AVAILABLE

- Target-level table rows: 596
- Primary matched rows used in Figure 4: 298
- Matched-target registry rows: 955
- Target-level distributions are plotted from frozen per-target `within_pearson_delta` and `cross_pearson_delta` columns.

| Direction | n | within mean | cross mean | within - cross mean | targets with within > cross |
|---|---:|---:|---:|---:|---:|
| K562 -> RPE1 | 150 | 0.281220 | -0.007049 | 0.288269 | 143/150 (95.3%) |
| RPE1 -> K562 | 148 | 0.550100 | 0.002084 | 0.548016 | 145/148 (98.0%) |
