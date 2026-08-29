# Current Overall Status and Progress

更新时间：2026-08-29 00:35 CST

## Executive Snapshot

```text
Active project path:         /Volumes/EMPTY2TB/VirtualPerturb-Audit 方案设计/VirtualPerturb-Audit
Norman pilot:                COMPLETE_AND_FROZEN
Replogle Phase 2A scope:     GEARS-compatible filtered essential-screen data
Replogle R-L1 GEARS:         COMPLETED
Replogle R-L4 GEARS:         COMPLETED
R-L4 postprocess/report:     COMPLETED
BNS:                         UNVERIFIED
UER/null status:             sensitivity_only
Complete-data replication:   BLOCKED_BY_FIGSHARE_PLUS_COMMAND_LINE_403
```

The long R-L4 R2K training has finished. Both cross-context GEARS directions now have completed metadata, per-perturbation metrics, retrieval rows, summary rows, and a consolidated Phase 2A-RL4 report.

## Completed Since Last Handoff

- Completed R-L4 K562 -> RPE1 full GEARS run: `results/replogle/gears/rl4_k2r_20260827T020001Z/`.
- Completed R-L4 RPE1 -> K562 full GEARS run: `results/replogle/gears/rl4_r2k_20260828T090923Z/`.
- Added R-L4 postprocess script: `scripts/build_gears_rl4_analysis.py`.
- Generated R-L4 consolidated outputs:
  - `results/replogle/gears_rl4_summary.csv`
  - `results/tables/replogle_rl4_gears_cross_context.csv`
  - `results/tables/replogle_rl4_gears_vs_baselines.csv`
  - `results/tables/replogle_rl1_rl4_gears_comparison.csv`
  - `figures/main/replogle_rl1_rl4_gears_transfer.{png,svg,pdf}`
  - `reports/PHASE2A_RL4_FULL_REPORT.md`
- Updated R-L4 progress and next-action handoff files.

## Core R-L4 Results

| Direction | Test context | n targets | Pearson delta | Top-1 | Top-5 | MRR | UER@50 | Sign-flip |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| K562 -> RPE1 | RPE1 | 732 | 0.0063 [0.0005, 0.0123] | 0.0027 | 0.0096 | 0.0126 | 0.3847 | 0.5520 |
| RPE1 -> K562 | K562 | 732 | 0.0022 [0.0007, 0.0036] | 0.0000 | 0.0068 | 0.0089 | 0.4666 | 0.4962 |

## Interpretation

R-L4 cross-context transfer collapses toward near-random perturbation retrieval in both directions. Audit-delta Pearson is close to zero, UER@50 is high, and sign-flip rates are high. This supports the Phase 2A stress-test conclusion that within-context expression agreement does not imply perturbation-specific transfer across cell-line contexts.

The result should be written as filtered-data stress-test evidence. It is not complete Replogle validation, not replicate-bounded BNS evidence, and not a claim that GEARS natively supports cell-line-aware condition splitting.

## Current Blockers

- Complete Figshare+ processed Replogle objects and manifest downloads remain blocked by command-line HTTP 403 from the official/paper-linked route.
- No validated biological replicate field is available in SRA runinfo or filtered h5ad `obs`; BNS remains `UNVERIFIED`.
- Project was moved to an external volume. Git status is noisy after the move, so avoid broad commits or destructive status cleanup unless the file-mode/mount issue is handled deliberately.

## Next Step

Move from execution into synthesis: write the R-L1/R-L4 contrast into the manuscript/results narrative, keep all caveats explicit, and leave complete-data replication blocked until official processed objects become accessible.
