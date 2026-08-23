# GEARS Replogle Compatibility

Date: 2026-08-23

## Status

```text
COMPATIBLE_WITH_SCOPE_LIMITS_K562_SMOKE_COMPLETE
```

The installed `cell-gears==0.1.2` package explicitly supports the filtered Replogle essential-screen datasets:

- `replogle_k562_essential`, Dataverse datafile `7458695`
- `replogle_rpe1_essential`, Dataverse datafile `7458694`

The package source comments describe these as filtered and not complete datasets. The current audit uses those filtered files.

## Local Files

| Dataset | Local h5ad | Shape |
|---|---|---:|
| K562 essential filtered | `data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad` | 162,751 x 5,000 |
| RPE1 essential filtered | `data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad` | 162,733 x 5,000 |

## Schema Compatibility

| Requirement | K562 | RPE1 |
|---|---|---|
| `obs.condition` perturbation labels | PASS | PASS |
| `obs.cell_type` context labels | PASS | PASS |
| `obs.control` control indicator | PASS | PASS |
| `var.gene_name` expression vocabulary | PASS | PASS |
| GEARS-style `perturb_processed.h5ad` | PASS | PASS |
| Biological replicate labels | ABSENT | ABSENT |
| Guide-level labels | ABSENT | ABSENT |

## Scope Limits

GEARS can be run on these files as a filtered essential-screen external audit. Results must not be described as complete Replogle genome-scale results. BNS remains unavailable unless an independent replicate field is recovered from complete metadata or source documentation.

## Recommendation

K562 R-L1 bounded smoke has verified dataloading, split injection, graph construction, training, checkpointing, and metric export. An optional RPE1 smoke can be run for symmetry. Full Replogle runs should launch only with `CONDITIONAL_GO_GEARS_FILTERED` status.
