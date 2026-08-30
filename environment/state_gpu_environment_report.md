# STATE GPU Environment Report

Generated: 2026-08-29T12:29:18Z

## Host

- hostname: autodl-container-99ee42b29a-a7121b90
- workspace: /root/autodl-tmp/vpa-work-slim/VirtualPerturb-Audit
- git_commit: ff1caa457463209b103e169871ad5a63284720a2

## OS

```text
Linux autodl-container-99ee42b29a-a7121b90 5.15.0-97-generic #107-Ubuntu SMP Wed Feb 7 13:26:48 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux
```

## GPU / Driver

```text
Sat Aug 29 20:29:16 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.76.05              Driver Version: 580.76.05      CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4090        On  |   00000000:27:00.0 Off |                  Off |
| 30%   28C    P8             21W /  450W |       0MiB /  24564MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```

## CUDA Toolkit

```text
/bin/sh: 1: nvcc: not found
```

## Python / PyTorch / STATE

```text
Python 3.12.3
torch 2.8.0+cu128
cuda_available True
device NVIDIA GeForce RTX 4090
torch_cuda_runtime 12.8
arc-state 0.11.1
state_file /root/miniconda3/lib/python3.12/site-packages/state/__init__.py
```

## Memory

```text
total        used        free      shared  buff/cache   available
Mem:           1.0Ti        43Gi       103Gi       3.4Gi       860Gi       954Gi
Swap:             0B          0B          0B
```

## Disk

```text
Filesystem      Size  Used Avail Use% Mounted on
overlay          30G  1.8G   29G   6% /
/dev/md0        146G   12G  135G   9% /root/autodl-tmp
```

## Gate

GO_GPU_ENVIRONMENT: PyTorch reports CUDA availability on NVIDIA GeForce RTX 4090.
