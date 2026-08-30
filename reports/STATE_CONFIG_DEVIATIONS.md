# STATE Configuration Deviations

Allowed compute-only adaptations are recorded here before model runs.

| item | value | rationale | performance_eligibility |
|---|---:|---|---|
| training.train_seed | 1 | Locked Phase 2C seed | eligible |
| training.devices | 1 | Single RTX 4090 server | eligible |
| training.batch_size | benchmarked per run | Fit within 24 GB VRAM | eligible if unchanged after benchmark |
| training.gradient_accumulation_steps | benchmarked per run | Preserve effective batch when needed | eligible |
| data.kwargs.num_workers | 4 | Avoid oversubscribing shared server CPU during I/O | eligible |
| precision / mixed precision | STATE default unless benchmark requires change | Compute adaptation only | eligible if recorded |
| smoke max_steps | 1-5 | Load/train/predict verification only | not performance-eligible |

No test-guided tuning is permitted. Any full-run hyperparameter adjustment must be justified by memory/runtime diagnostics rather than metric feedback.

## Batch Probe Update

Selected `training.batch_size=8` for full Phase 2C runs after batch-capacity probes completed without OOM. `data.kwargs.num_workers=8` is used for full runs to improve input throughput on the 20-core host. Validation and checkpoint intervals are increased for full runs to reduce non-training overhead.

## Final Batch Selection

Selected `training.batch_size=48` for full Phase 2C runs after batch-capacity probes. `data.kwargs.num_workers=8`, low-frequency validation/checkpointing, and single-GPU execution are compute-only adaptations.
