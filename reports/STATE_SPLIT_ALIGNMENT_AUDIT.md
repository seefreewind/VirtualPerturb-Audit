# STATE-GEARS Split Alignment Audit

- mode_prepared: full
- total_rows: 2894
- non_aligned_rows: 0
- exclusion_warning_gt_10pct: false

## Summary

| dataset                  | split                 | alignment_status   |   n_targets |
|:-------------------------|:----------------------|:-------------------|------------:|
| norman_l1                | L1_seed1              | ALIGNED            |         249 |
| norman_l2                | L2_seed1              | ALIGNED            |         200 |
| replogle_k562_rl1        | R-L1-K562_seed1       | ALIGNED            |         979 |
| replogle_k562_rl4_source | R-L4-K2R_seed1_source | ALIGNED            |         733 |
| replogle_rpe1_rl4_target | R-L4-K2R_seed1_target | ALIGNED            |         733 |

All rows are derived from frozen GEARS split pickle files and source AnnData condition labels.
