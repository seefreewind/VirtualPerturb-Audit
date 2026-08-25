# Phase 2A RL1 Full Report

Generated: 2026-08-25 21:25:17 local time

## Executive conclusion

Both within-context Replogle R-L1 GEARS full runs completed on the GEARS-compatible filtered essential-screen data. K562 is classified as `SUPPORTS_DIVERGENCE` and RPE1 is classified as `SUPPORTS_DIVERGENCE` under the pre-registered metric-divergence question: whether global transcriptomic fit and perturbation-specific retrieval remain concordant outside Norman.

The result supports moving to cross-context R-L4 only under a conditional filtered-data label. The complete Figshare+ processed objects remain unavailable by command-line access, and BNS remains `UNVERIFIED` because no validated biological replicate field is available.

## RPE1 smoke status

| Field | Value |
|---|---|
| Status | PASS |
| Verdict | executable-chain evidence only, not performance |
| Report | `reports/REPLOGLE_RPE1_SMOKE_REPORT.md` |

## Full-run configuration

- Configs: `configs/replogle/gears_rl1_k562_seed1.yaml`, `configs/replogle/gears_rl1_rpe1_seed1.yaml`
- K562 run directory: `results/replogle/gears/rl1_k562_20260824T074041Z`
- RPE1 run directory: `results/replogle/gears/rl1_rpe1_20260825T000548Z`
- K562 elapsed seconds: `50939.4`
- RPE1 elapsed seconds: `43319.3`
- Matched Norman pilot choices: 20 epochs, seed 1, batch 16, Adam 1e-3/5e-4, hidden 64, essential perturbation graph, filtered GO tensor with top-k=20 per target, and GEARS-internal custom split rebuilt inside the GEARS vocabulary.
- Deviations vs frozen Norman pilot: `reports/PHASE2A_RL1_CONFIG_DEVIATIONS.md`

## K562 results

| Context | Metric space | n targets | Pearson delta | Top-1 | Top-5 | MRR | UER@50 | Sign-flip |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| K562 | audit_delta | 216 | 0.2840 [0.2558, 0.3107] | 0.0139 | 0.0556 | 0.0497 [0.0332, 0.0689] | 0.1580 | 0.2691 |
| K562 | gears_raw | 216 | 0.9851 [0.9836, 0.9864] | 0.0139 | 0.0417 | 0.0445 [0.0290, 0.0624] | 0.0000 | 0.0000 |

## RPE1 results

| Context | Metric space | n targets | Pearson delta | Top-1 | Top-5 | MRR | UER@50 | Sign-flip |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| RPE1 | audit_delta | 308 | 0.4616 [0.4345, 0.4878] | 0.0097 | 0.0195 | 0.0262 [0.0166, 0.0385] | 0.0940 | 0.1720 |
| RPE1 | gears_raw | 308 | 0.9709 [0.9690, 0.9727] | 0.0000 | 0.0162 | 0.0209 [0.0158, 0.0263] | 0.0000 | 0.0000 |

## Strong baseline comparison

The comparison below reuses `results/replogle/replogle_summary.csv` read-only baseline rows and places GEARS in the same audit-delta space.

### K562

| Model/probe | Pearson delta | Top-1 | Top-5 | MRR | UER@50 |
|---|---:|---:|---:|---:|---:|
| B0_no_change | NA [NA, NA] | NA | NA | NA | 0.5287 |
| B1_global_perturbed_mean | 0.3869 [0.3614, 0.4099] | 0.0046 | 0.0229 | 0.0274 | 0.1230 |
| B2_context_matched_perturbed_mean | 0.3869 [0.3614, 0.4099] | 0.0046 | 0.0229 | 0.0274 | 0.1230 |
| B4_pca_ridge | 0.3869 [0.3614, 0.4099] | 0.0046 | 0.0229 | 0.0274 | 0.1230 |
| B5_mean_effect | 0.3869 [0.3614, 0.4099] | 0.0046 | 0.0229 | 0.0274 | 0.1230 |
| FP1_perturbation_blind_mean_effect | 0.3869 [0.3614, 0.4099] | 0.0046 | 0.0229 | 0.0274 | 0.1230 |
| FP3_label_shuffled_mean_effect | 0.1532 [0.1302, 0.1764] | 0.0092 | 0.0229 | 0.0335 | 0.1768 |
| GEARS_cell_gears_0.1.2 | 0.2840 [0.2558, 0.3107] | 0.0139 | 0.0556 | 0.0497 | 0.1580 |

### RPE1

| Model/probe | Pearson delta | Top-1 | Top-5 | MRR | UER@50 |
|---|---:|---:|---:|---:|---:|
| B0_no_change | NA [NA, NA] | NA | NA | NA | 0.5590 |
| B1_global_perturbed_mean | 0.6349 [0.6043, 0.6633] | 0.0032 | 0.0162 | 0.0204 | 0.0375 |
| B2_context_matched_perturbed_mean | 0.6349 [0.6043, 0.6633] | 0.0032 | 0.0162 | 0.0204 | 0.0375 |
| B4_pca_ridge | 0.6349 [0.6043, 0.6633] | 0.0032 | 0.0162 | 0.0204 | 0.0375 |
| B5_mean_effect | 0.6349 [0.6043, 0.6633] | 0.0032 | 0.0162 | 0.0204 | 0.0375 |
| FP1_perturbation_blind_mean_effect | 0.6349 [0.6043, 0.6633] | 0.0032 | 0.0162 | 0.0204 | 0.0375 |
| FP3_label_shuffled_mean_effect | 0.3865 [0.3571, 0.4148] | 0.0000 | 0.0227 | 0.0190 | 0.1065 |
| GEARS_cell_gears_0.1.2 | 0.4616 [0.4345, 0.4878] | 0.0097 | 0.0195 | 0.0262 | 0.0940 |

## Falsification probe comparison

GEARS is compared against FP-1 perturbation-blind and FP-3 label-shuffled probes in `results/tables/replogle_gears_vs_probes.csv`. Interpretation should focus on whether GEARS improves perturbation-specific retrieval beyond simple effect templates, not only on Pearson delta.

## Metric divergence

| Setting | Pearson rank | Specificity rank | UER rank | Global minus specificity rank |
|---|---:|---:|---:|---:|
| Norman L1 GEARS | 1 | 1 | 1 | 0 |
| Norman L2 GEARS | 4 | 3 | 1 | 1 |
| Norman L3 GEARS | 3 | 2 | 1 | 1 |
| Replogle K562 R-L1 GEARS | 2 | 4 | 1 | -2 |
| Replogle RPE1 R-L1 GEARS | 5 | 5 | 1 | 0 |

## Hallucination sensitivity

- `uer_null_status = sensitivity_only`
- Null source: per-perturbation median absolute audit delta.
- No validated biological replicate labels are available, so this is not a replicate-derived hallucination rate.

## Norman comparison

| Setting | n | Pearson delta | Top-1 | Top-5 | MRR | UER@50 |
|---|---:|---:|---:|---:|---:|---:|
| Norman L1 GEARS | 55 | 0.9887 [0.9860, 0.9914] | 0.2000 | 0.4910 | 0.3277 | 0.0000 |
| Norman L2 GEARS | 40 | 0.9838 [0.9795, 0.9875] | 0.0750 | 0.1500 | 0.1471 | 0.0000 |
| Norman L3 GEARS | 25 | 0.9843 [0.9781, 0.9896] | 0.0800 | 0.3200 | 0.2067 | 0.0000 |
| Replogle K562 R-L1 GEARS | 216 | 0.9851 [0.9836, 0.9864] | 0.0139 | 0.0417 | 0.0445 | 0.0000 |
| Replogle RPE1 R-L1 GEARS | 308 | 0.9709 [0.9690, 0.9727] | 0.0000 | 0.0162 | 0.0209 | 0.0000 |

## External replication assessment

| Context | Assessment | Basis |
|---|---|---|
| K562 | `SUPPORTS_DIVERGENCE` | gears_raw Pearson 0.9851 [0.9836, 0.9864]; MRR 0.0445 [0.0290, 0.0624]; top-1 0.0139. |
| RPE1 | `SUPPORTS_DIVERGENCE` | gears_raw Pearson 0.9709 [0.9690, 0.9727]; MRR 0.0209 [0.0158, 0.0263]; top-1 0.0000. |

## Limitations

- Replogle data are `GEARS-compatible filtered essential-screen data`, not the complete Figshare+ processed objects.
- BNS is `UNVERIFIED`; all UER values are sensitivity checks, not biological-replicate upper-bound estimates.
- GEARS uses its internal condition vocabulary after filtering to graph-supported genes, so counts can differ from the frozen audit split vocabulary.
- CPU full runs are terminal-lifetime sensitive; failed/interrupted attempts are preserved as provenance and must not be mixed with completed runs.

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

```text
CONDITIONAL_GO_RL4
```

Proceed to R-L4 cross-context GEARS runs only with filtered-data and BNS-unverified labels.
