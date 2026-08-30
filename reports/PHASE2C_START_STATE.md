# Phase 2C Start State

## Frozen Inputs

- Phase 2A freeze commit: `6872a97 Freeze Replogle Phase 2A RL1-RL4 GEARS audit`
- Phase 2B commit: `80a3ffb Complete Phase 2B matched-target and second-model audit`
- Local GPU gate commit: `ff1caa4 Record Phase 2C GPU environment gate`
- GEARS rerun during Phase 2C: `false`
- Frozen GEARS splits modified: `false`
- Matched-target registry modified: `false`
- Phase 2A/2B primary metrics overwritten: `false`

## Execution Environments

Phase 2C began on the local Mac with STATE installed but no CUDA-capable GPU. The local machine was used for environment gating, input preparation, and postprocessing only. Full STATE training and prediction were moved to a remote Linux GPU server after the Mac gate returned `NO_GO_GPU_ENVIRONMENT`.

The remote GPU environment was:

- Host: `autodl-container-99ee42b29a-a7121b90`
- Workspace: `/root/autodl-tmp/vpa-work-slim/VirtualPerturb-Audit`
- GPU: NVIDIA GeForce RTX 4090
- PyTorch CUDA: `True`
- STATE: arc-state 0.11.1

## Locked Phase 2C Tasks

| Run ID | Task | Role |
| --- | --- | --- |
| `S1_norman_l1` | Norman L1 | Within-context STATE audit |
| `S2_norman_l2` | Norman L2 | Within-context STATE audit |
| `S3_replogle_k562_rl1` | Replogle K562 R-L1 | Within-context STATE audit |
| `S4_replogle_k562_to_rpe1_rl4` | Replogle K562-to-RPE1 R-L4 | Cross-context STATE audit |

## Start-State Boundary

The remote run used a slim synchronized workspace for compute, then synchronized outputs back to the external-drive local project. Large STATE prediction matrices are retained under `results/state/full_phase2c_20260829T131235Z/` but are intentionally excluded from git tracking by the repository ignore rules.
