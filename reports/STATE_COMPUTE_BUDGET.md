# STATE Compute Budget

Generated: 2026-08-29T12:51:14Z

Benchmark: 50 training steps per locked Phase 2C task, `model=state`, `batch_size=4`, `gradient_accumulation_steps=1`, `num_workers=4`, seed 1. Smoke runs remain performance_eligible=false.

| run_id       | run_dir                                                                    |   return_code |   duration_seconds_50_steps |   seconds_per_step |   peak_gpu_mem_mb |   mean_gpu_util_pct |   checkpoint_mb |
|:-------------|:---------------------------------------------------------------------------|--------------:|----------------------------:|-------------------:|------------------:|--------------------:|----------------:|
| S1_norman_l1 | results/state/benchmark_phase2c_S1_norman_l1_20260829T124735Z/S1_norman_l1 |             0 |                         102 |               2.04 |              3853 |                 6.8 |          3473.1 |

## Budget Decision
GO_FULL_MATRIX: all benchmark return codes are 0 and observed 50-step durations/VRAM are compatible with completing the four-task matrix on a single RTX 4090. Full-run wall time remains dependent on the selected max_steps; the next run will use a bounded Phase 2C compute configuration rather than metric-guided tuning.

## Batch Capacity Probe

Probe directory: `results/state/batch_probe_phase2c_20260829T125730Z`

|   batch_size |   return_code |   duration_seconds_20_steps |   seconds_per_step |   peak_gpu_mem_mb |   mean_gpu_util_pct | oom   | run_dir                                                    |
|-------------:|--------------:|----------------------------:|-------------------:|------------------:|--------------------:|:------|:-----------------------------------------------------------|
|            8 |             0 |                         109 |               5.45 |              5701 |                 2.6 | False | results/state/batch_probe_phase2c_20260829T125730Z/batch_8 |

Chosen full-run batch_size: `8`. This is a compute-only adaptation based on successful short training probes, not on validation/test metrics.

## Batch Capacity Probe Updated

| probe_dir                                          |   batch_size |   return_code |   duration_seconds_20_steps |   seconds_per_step |   peak_gpu_mem_mb |   mean_gpu_util_pct | oom   | run_dir                                                     |
|:---------------------------------------------------|-------------:|--------------:|----------------------------:|-------------------:|------------------:|--------------------:|:------|:------------------------------------------------------------|
| results/state/batch_probe_phase2c_20260829T125730Z |            8 |             0 |                         109 |               5.45 |              5701 |                 2.6 | False | results/state/batch_probe_phase2c_20260829T125730Z/batch_8  |
| results/state/batch_probe_phase2c_20260829T130012Z |           16 |             0 |                         142 |               7.1  |              8941 |                 6.8 | False | results/state/batch_probe_phase2c_20260829T130012Z/batch_16 |
| results/state/batch_probe_phase2c_20260829T130012Z |           32 |             0 |                         210 |              10.5  |             15887 |                 4.4 | False | results/state/batch_probe_phase2c_20260829T130012Z/batch_32 |
| results/state/batch_probe_phase2c_20260829T130012Z |           48 |             0 |                         314 |              15.7  |             22975 |                 2.9 | False | results/state/batch_probe_phase2c_20260829T130012Z/batch_48 |

Chosen full-run batch_size: `48`. This is a compute-only adaptation from short stability probes.
