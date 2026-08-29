# Second Model Split Compatibility

更新时间：2026-08-29

## Scope

Second-model first round was restricted to four tasks:

| Task | Dataset | Split | Compatibility |
|---|---|---|---|
| M1 | Norman | L1 | compatible with frozen split after STATE perturbation-label adapter |
| M2 | Norman | L2 | compatible with frozen split after STATE perturbation-label adapter |
| M3 | Replogle K562 | R-L1-K562 | compatible with frozen split after `GENE+ctrl` to `GENE` mapping |
| M4 | Replogle K562 -> RPE1 | R-L4-K2R | conceptually compatible, but requires trained source-context checkpoint |

No new random splits were created.

## Frozen Split Sources

| Task | Split source |
|---|---|
| Norman L1 | `data/raw/norman/splits/virtualperturb_audit_L1_seed1.pkl` |
| Norman L2 | `data/raw/norman/splits/virtualperturb_audit_L2_seed1.pkl` |
| Replogle K562 R-L1 | `data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L1-K562_seed1_rl1.pkl` |
| Replogle K562 -> RPE1 R-L4 | `data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L4-K2R_seed1_rl4.pkl` |

## Adapter Result

The script `scripts/prepare_state_phase2b_inputs.py` converts each task into a STATE-compatible h5ad directory plus TOML file. For smoke testing, Norman L1 produced 180 cells, 9 conditions, and 5,045 genes and was accepted by the STATE data module.

## Final Compatibility Decision

```text
SPLITS_COMPATIBLE_WITH_STATE_ADAPTER = TRUE
PERFORMANCE_ELIGIBLE_SECOND_DEEP_MODEL_RUNS = FALSE
```

The blocker is compute/runtime fairness, not split incompatibility.
