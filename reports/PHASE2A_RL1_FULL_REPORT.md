# Phase 2A RL1 Full Report

> **NOTE:** This report is generated after both R-L1 full runs complete. Placeholder markers are filled by the executed runs. All Replogle values refer to **GEARS-compatible filtered essential-screen data** (not the complete Figshare+ processed objects).

## Executive conclusion

<!-- placeholder: filled after runs -->

## RPE1 smoke status

<!-- placeholder:

| Field | Value |
|---|---|
| Status | PASS |
| Run directory | `results/replogle/gears/gears_replogle_rpe1_smoke_20260823T072300Z/` |
| Verdict | executable-chain evidence only, not performance |
| Report | `reports/REPLOGLE_RPE1_SMOKE_REPORT.md` |
-->

## Full-run configuration

- Configs: `configs/replogle/gears_rl1_k562_seed1.yaml`, `configs/replogle/gears_rl1_rpe1_seed1.yaml`
- Deviations vs frozen Norman pilot: `reports/PHASE2A_RL1_CONFIG_DEVIATIONS.md`
- Matches Norman pilot: 20 epochs, seed 1, batch 16, Adam 1e-3/5e-4, hidden 64, essential perturbation graph, filtered GO tensor (top-k=20 per target), GEARS-internal custom split rebuilt inside GEARS vocabulary.

## K562 results

<!-- placeholder -->

## RPE1 results

<!-- placeholder -->

## Strong baseline comparison

<!-- placeholder: read-only reuse of `results/replogle/replogle_summary.csv` B0/B1/B2/B4/B5 rows -->

## Falsification probe comparison

<!-- placeholder: FP-1 and FP-3 from `results/replogle/replogle_summary.csv`; GEARS vs probes in audit-delta space -->

## Metric divergence

<!-- placeholder: `results/tables/metric_divergence_profile.csv` -->

## Hallucination sensitivity

- `uer_null_status = sensitivity_only`
- Null source: per-perturbation median absolute audit delta (no validated biological replicate available)
- Not a replicate-derived hallucination rate.

## Norman comparison

<!-- placeholder: `results/tables/norman_replogle_rl1_comparison.csv` -->

## External replication assessment

<!-- placeholder: SUPPORTS_DIVERGENCE / PARTIAL_SUPPORT / NO_SUPPORT / UNINFORMATIVE per context -->

## Limitations

-- placeholder --

## BNS status

```text
BNS = NA / existing unverified value
bns_status = UNVERIFIED
bns_role = sensitivity_only
```

No field in SRA runinfo or filtered h5ad `obs` is treated as a biological replicate. `batch`, `library`, `gemgroup`, `run`, and `SRA run` are technical metadata only.

## Data completeness caveat

```text
Replogle data = GEARS-compatible filtered essential-screen data
NOT complete Figshare+ processed objects
```

## Recommended next gate

<!-- placeholder: GO_RL4 / CONDITIONAL_GO_RL4 / HOLD_RL4 -->