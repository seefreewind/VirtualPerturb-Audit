# STATE GPU Environment Report

更新时间：2026-08-29 15:45 CST

## Command Audit

| Check | Result |
|---|---|
| `hostname` | `zhangyudeMacBook-Air.local` |
| `uname -a` | `Darwin zhangyudeMacBook-Air.local 25.4.0 Darwin Kernel Version 25.4.0: Thu Mar 19 19:33:43 PDT 2026; root:xnu-12377.101.15~1/RELEASE_ARM64_T8142 arm64` |
| `sw_vers` | macOS 26.4, build 25E246 |
| `nvidia-smi` | command not found |
| `nvcc --version` | command not found |
| `python3 --version` | Python 3.9.6 |
| `state --help` | pass |
| workspace disk | `/dev/disk6s1`, 1.8 TiB total, 866 GiB used, 997 GiB available |
| system RAM | 17,179,869,184 bytes |
| `free -h` | command not found on macOS |

## CUDA Sanity Test

```text
python3_torch_version 2.8.0
python3_cuda_available False
python3_cuda_device NO_GPU

state_python_torch_version 2.13.0
state_python_cuda_available False
state_python_cuda_device NO_GPU
arc_state_version 0.11.1
```

## STATE Environment

```yaml
state_executable: /Users/zy/.local/bin/state
state_tool_python: /Users/zy/.local/share/uv/tools/arc-state/bin/python
arc_state_version: 0.11.1
pip_freeze_record: environment/state_gpu_pip_freeze.txt
state_repository_commit_checked: 9bbfe78a434a55205e4de834e1ea99f85f7a3add
```

## Gate Decision

```text
GPU_ENVIRONMENT_STATUS = NO_GO_GPU_ENVIRONMENT
```

This machine does not provide an NVIDIA CUDA environment. Per Phase 2C instructions, full STATE confirmatory runs must not fall back to CPU.
