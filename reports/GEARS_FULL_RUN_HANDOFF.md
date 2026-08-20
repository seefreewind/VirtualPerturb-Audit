# GEARS Full-Run Handoff

Status: **USER_COMPUTE_REQUIRED**

## Why this needs intervention

The local Mac CPU can run bounded GEARS smoke checks, but a full GEARS training/evaluation run is not practical as an unattended local continuation. A previous CPU full-epoch attempt progressed beyond 1,600 batches and was stopped because it was too slow for development validation.

## Ready-to-run command

Use a GPU machine with the isolated GEARS environment or an equivalent environment containing `cell-gears==0.1.2`, PyTorch, and PyG:

```bash
cd "/Users/zy/Documents/ChatGPT/VirtualPerturb-Audit 方案设计/VirtualPerturb-Audit"
DEVICE=cuda EPOCHS=20 BATCH_SIZE=16 TEST_BATCH_SIZE=16 bash scripts/run_gears_full_audit.sh
```

For CPU-only execution, use:

```bash
DEVICE=cpu EPOCHS=20 bash scripts/run_gears_full_audit.sh
```

CPU-only execution is expected to be slow and should be treated as a deliberate compute decision.

## What the script does

- Runs GEARS on L1, L2, and L3 audit splits.
- Evaluates all test batches by default.
- Writes per-run metadata, per-perturbation metrics, delta centroid tensors, and perturbation retrieval/confusion rows.
- Rebuilds null-envelope sensitivity, family-confusion summaries, figures, and tables after GEARS outputs are added.

## Interpretation guardrails

- Bounded smoke rows remain software-integration checks only.
- Full GEARS rows should be interpreted only when `status` is `COMPLETED_GEARS_EVALUATION` and enough perturbation units are evaluated.
- Replicate-derived BNS remains unverified unless a true biological replicate label is found.
- GEO `gemgroup` supports batch-like sensitivity only, not a replicate upper bound.
