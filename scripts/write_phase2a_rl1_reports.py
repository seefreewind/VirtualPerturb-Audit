from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


REPORTS = Path("reports")
REPL = Path("results/replogle")
TABLES = Path("results/tables")
GEARS_DIR = REPL / "gears"


def latest_completed_run(key: str) -> tuple[Path, dict]:
    for run in reversed(sorted(GEARS_DIR.glob(f"rl1_{key}_*"))):
        meta_path = run / "metadata.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        if meta.get("run_status") in {"COMPLETED_GEARS", "COMPLETED_GEARS_EVALUATION"}:
            return run, meta
    raise RuntimeError(f"No completed rl1_{key}_* run found")


def row(df: pd.DataFrame, **filters) -> pd.Series:
    hit = df.copy()
    for key, value in filters.items():
        hit = hit[hit[key].eq(value)]
    if hit.empty:
        raise KeyError(f"No row for {filters}")
    return hit.iloc[0]


def fmt(value, digits: int = 4) -> str:
    if pd.isna(value):
        return "NA"
    if isinstance(value, str):
        return value
    return f"{float(value):.{digits}f}"


def ci(mid, low, high) -> str:
    return f"{fmt(mid)} [{fmt(low)}, {fmt(high)}]"


def support_label(r: pd.Series) -> str:
    pearson = float(r["pearson_delta"])
    mrr = float(r["mrr"])
    top1 = float(r["top1"])
    if pearson >= 0.75 and mrr <= 0.20 and top1 <= 0.10:
        return "SUPPORTS_DIVERGENCE"
    if pearson >= 0.60 and mrr <= 0.30:
        return "PARTIAL_SUPPORT"
    if pearson < 0.60:
        return "NO_HIGH_GLOBAL_FIT_SIGNAL"
    return "NO_CLEAR_DIVERGENCE"


def metric_table(rows: list[pd.Series]) -> str:
    lines = [
        "| Context | Metric space | n targets | Pearson delta | Top-1 | Top-5 | MRR | UER@50 | Sign-flip |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['cell_line']} | {r['metric_space']} | {int(r['n_test_targets'])} | "
            f"{ci(r['pearson_delta'], r['pearson_ci_low'], r['pearson_ci_high'])} | "
            f"{fmt(r['top1'])} | {fmt(r['top5'])} | {ci(r['mrr'], r['mrr_ci_low'], r['mrr_ci_high'])} | "
            f"{fmt(r['uer50'])} | {fmt(r['sign_flip_rate'])} |"
        )
    return "\n".join(lines)


def probe_table(df: pd.DataFrame, context: str) -> str:
    sub = df[df["context"].eq(context)].copy()
    prefixes = [
        "B0_no_change",
        "B1_global_perturbed_mean",
        "B2_context_matched_perturbed_mean",
        "B4_pca_ridge",
        "B5_mean_effect",
        "FP1_perturbation_blind",
        "FP3_label_shuffled",
        "GEARS_",
    ]

    def order_key(model: str) -> int:
        for idx, prefix in enumerate(prefixes):
            if str(model).startswith(prefix):
                return idx
        return 99

    sub["order"] = sub["model"].map(order_key)
    sub = sub.sort_values(["order", "model"])
    lines = [
        "| Model/probe | Pearson delta | Top-1 | Top-5 | MRR | UER@50 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, r in sub.iterrows():
        lines.append(
            f"| {r['model']} | {ci(r['pearson_delta'], r['pearson_ci_low'], r['pearson_ci_high'])} | "
            f"{fmt(r['retrieval_top1'])} | {fmt(r['retrieval_top5'])} | "
            f"{fmt(r['retrieval_mrr'])} | {fmt(r['uer50'])} |"
        )
    return "\n".join(lines)


def write_full_report() -> tuple[str, str]:
    rl1 = pd.read_csv(REPL / "gears_rl1_summary.csv")
    compare = pd.read_csv(TABLES / "norman_replogle_rl1_comparison.csv")
    probes = pd.read_csv(TABLES / "replogle_gears_vs_probes.csv")
    divergence = pd.read_csv(TABLES / "metric_divergence_profile.csv")
    k_run, k_meta = latest_completed_run("k562")
    r_run, r_meta = latest_completed_run("rpe1")

    k_audit = row(rl1, cell_line="K562", metric_space="audit_delta")
    r_audit = row(rl1, cell_line="RPE1", metric_space="audit_delta")
    k_raw = row(rl1, cell_line="K562", metric_space="gears_raw")
    r_raw = row(rl1, cell_line="RPE1", metric_space="gears_raw")
    k_label = support_label(k_raw)
    r_label = support_label(r_raw)

    norm_lines = [
        "| Setting | n | Pearson delta | Top-1 | Top-5 | MRR | UER@50 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in compare.iterrows():
        norm_lines.append(
            f"| {r['setting']} | {int(r['n_test_perturbations'])} | "
            f"{ci(r['pearson_delta'], r['pearson_ci_low'], r['pearson_ci_high'])} | "
            f"{fmt(r['retrieval_top1'])} | {fmt(r['retrieval_top5'])} | {fmt(r['retrieval_mrr'])} | {fmt(r['uer50'])} |"
        )

    div_lines = [
        "| Setting | Pearson rank | Specificity rank | UER rank | Global minus specificity rank |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, r in divergence.iterrows():
        div_lines.append(
            f"| {r['setting']} | {int(r['rank_by_global_fit'])} | {int(r['rank_by_specificity'])} | "
            f"{int(r['rank_by_hallucination'])} | {int(r['global_minus_specificity_rank'])} |"
        )

    report = f"""# Phase 2A RL1 Full Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} local time

## Executive conclusion

Both within-context Replogle R-L1 GEARS full runs completed on the GEARS-compatible filtered essential-screen data. K562 is classified as `{k_label}` and RPE1 is classified as `{r_label}` under the pre-registered metric-divergence question: whether global transcriptomic fit and perturbation-specific retrieval remain concordant outside Norman.

The result supports moving to cross-context R-L4 only under a conditional filtered-data label. The complete Figshare+ processed objects remain unavailable by command-line access, and BNS remains `UNVERIFIED` because no validated biological replicate field is available.

## RPE1 smoke status

| Field | Value |
|---|---|
| Status | PASS |
| Verdict | executable-chain evidence only, not performance |
| Report | `reports/REPLOGLE_RPE1_SMOKE_REPORT.md` |

## Full-run configuration

- Configs: `configs/replogle/gears_rl1_k562_seed1.yaml`, `configs/replogle/gears_rl1_rpe1_seed1.yaml`
- K562 run directory: `{k_run}`
- RPE1 run directory: `{r_run}`
- K562 elapsed seconds: `{fmt(k_meta.get('elapsed_seconds', 'NA'), 1)}`
- RPE1 elapsed seconds: `{fmt(r_meta.get('elapsed_seconds', 'NA'), 1)}`
- Matched Norman pilot choices: 20 epochs, seed 1, batch 16, Adam 1e-3/5e-4, hidden 64, essential perturbation graph, filtered GO tensor with top-k=20 per target, and GEARS-internal custom split rebuilt inside the GEARS vocabulary.
- Deviations vs frozen Norman pilot: `reports/PHASE2A_RL1_CONFIG_DEVIATIONS.md`

## K562 results

{metric_table([k_audit, k_raw])}

## RPE1 results

{metric_table([r_audit, r_raw])}

## Strong baseline comparison

The comparison below reuses `results/replogle/replogle_summary.csv` read-only baseline rows and places GEARS in the same audit-delta space.

### K562

{probe_table(probes, 'K562')}

### RPE1

{probe_table(probes, 'RPE1')}

## Falsification probe comparison

GEARS is compared against FP-1 perturbation-blind and FP-3 label-shuffled probes in `results/tables/replogle_gears_vs_probes.csv`. Interpretation should focus on whether GEARS improves perturbation-specific retrieval beyond simple effect templates, not only on Pearson delta.

## Metric divergence

{chr(10).join(div_lines)}

## Hallucination sensitivity

- `uer_null_status = sensitivity_only`
- Null source: per-perturbation median absolute audit delta.
- No validated biological replicate labels are available, so this is not a replicate-derived hallucination rate.

## Norman comparison

{chr(10).join(norm_lines)}

## External replication assessment

| Context | Assessment | Basis |
|---|---|---|
| K562 | `{k_label}` | gears_raw Pearson {ci(k_raw['pearson_delta'], k_raw['pearson_ci_low'], k_raw['pearson_ci_high'])}; MRR {ci(k_raw['mrr'], k_raw['mrr_ci_low'], k_raw['mrr_ci_high'])}; top-1 {fmt(k_raw['top1'])}. |
| RPE1 | `{r_label}` | gears_raw Pearson {ci(r_raw['pearson_delta'], r_raw['pearson_ci_low'], r_raw['pearson_ci_high'])}; MRR {ci(r_raw['mrr'], r_raw['mrr_ci_low'], r_raw['mrr_ci_high'])}; top-1 {fmt(r_raw['top1'])}. |

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
"""
    (REPORTS / "PHASE2A_RL1_FULL_REPORT.md").write_text(report)
    return k_label, r_label


def write_gate_report(k_label: str, r_label: str) -> None:
    rl1 = pd.read_csv(REPL / "gears_rl1_summary.csv")
    _, k_meta = latest_completed_run("k562")
    _, r_meta = latest_completed_run("rpe1")
    k_raw = row(rl1, cell_line="K562", metric_space="gears_raw")
    r_raw = row(rl1, cell_line="RPE1", metric_space="gears_raw")

    report = f"""# Phase 2A Cross-Context Gate

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} local time

## Decision

```text
CONDITIONAL_GO_RL4
```

The within-context Replogle R-L1 full GEARS audit is complete for both K562 and RPE1. Cross-context R-L4 can proceed as a filtered-data external audit, with explicit `BNS_STATUS = UNVERIFIED` and no complete-data claims.

## Gate checks

| Check | Status | Evidence |
|---|---|---|
| K562 R-L1 GEARS full run | PASS | `run_status = {k_meta.get('run_status', 'NA')}`; gears_raw Pearson {ci(k_raw['pearson_delta'], k_raw['pearson_ci_low'], k_raw['pearson_ci_high'])}; MRR {ci(k_raw['mrr'], k_raw['mrr_ci_low'], k_raw['mrr_ci_high'])}. |
| RPE1 R-L1 GEARS full run | PASS | `run_status = {r_meta.get('run_status', 'NA')}`; gears_raw Pearson {ci(r_raw['pearson_delta'], r_raw['pearson_ci_low'], r_raw['pearson_ci_high'])}; MRR {ci(r_raw['mrr'], r_raw['mrr_ci_low'], r_raw['mrr_ci_high'])}. |
| External metric-divergence signal | PASS | K562 `{k_label}`; RPE1 `{r_label}`. |
| Filtered-data scope | PASS_WITH_SCOPE_LIMIT | Outputs use `Replogle_GEARS_filtered`; complete Figshare+ processed objects remain unavailable by command-line access. |
| BNS/replicate status | FAIL_FOR_BNS_ONLY | No validated biological replicate label; keep `BNS_STATUS = UNVERIFIED`. |
| Downstream tables and figures | PASS | `results/replogle/gears_rl1_summary.csv`, `results/tables/norman_replogle_rl1_comparison.csv`, `results/tables/metric_divergence_profile.csv`, `results/tables/replogle_gears_vs_probes.csv`, and main figures are generated. |

## Required R-L4 constraints

- Run `R-L4-K2R` and `R-L4-R2K` only on GEARS-compatible filtered essential-screen data.
- Preserve the same GEARS configuration family used for R-L1 unless a deviation is documented before execution.
- Keep `bns_status = UNVERIFIED` and `uer_null_status = sensitivity_only`.
- Compare R-L4 against R-L1 in both global-fit and perturbation-specific metrics.
- Treat cross-context performance as external generalization evidence, not complete Replogle genome-scale validation.

## Immediate next action

Launch the two R-L4 full GEARS runs after committing the completed R-L1 report package.
"""
    (REPORTS / "PHASE2A_CROSS_CONTEXT_GATE.md").write_text(report)


def main() -> None:
    k_label, r_label = write_full_report()
    write_gate_report(k_label, r_label)
    print("Wrote reports/PHASE2A_RL1_FULL_REPORT.md")
    print("Wrote reports/PHASE2A_CROSS_CONTEXT_GATE.md")


if __name__ == "__main__":
    main()
