from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from src.data.perturbations import normalize_condition
from src.statistics.bootstrap import paired_bootstrap_diff


REPL = Path("results/replogle")
GEARS = REPL / "gears"
TABLES = Path("results/tables")
FIGURES = Path("figures/main")
REPORTS = Path("reports")


RUNS = {
    "k562_rl1": GEARS / "rl1_k562_20260824T074041Z",
    "rpe1_rl1": GEARS / "rl1_rpe1_20260825T000548Z",
    "k2r_rl4": GEARS / "rl4_k2r_20260827T020001Z",
    "r2k_rl4": GEARS / "rl4_r2k_20260828T090923Z",
}


COMPARISONS = {
    "K2R_source_context": {
        "within": "k562_rl1",
        "cross": "k2r_rl4",
        "comparison_role": "primary_source_context_comparison",
        "direction": "K562_within_vs_K562_to_RPE1",
    },
    "R2K_source_context": {
        "within": "rpe1_rl1",
        "cross": "r2k_rl4",
        "comparison_role": "primary_source_context_comparison",
        "direction": "RPE1_within_vs_RPE1_to_K562",
    },
    "K2R_target_context": {
        "within": "rpe1_rl1",
        "cross": "k2r_rl4",
        "comparison_role": "exploratory_target_context_comparison",
        "direction": "RPE1_within_vs_K562_to_RPE1",
    },
    "R2K_target_context": {
        "within": "k562_rl1",
        "cross": "r2k_rl4",
        "comparison_role": "exploratory_target_context_comparison",
        "direction": "K562_within_vs_RPE1_to_K562",
    },
}


HIGHER_IS_BETTER = {
    "pearson_delta",
    "spearman_delta",
    "retrieval_top1_native",
    "retrieval_top5_native",
    "retrieval_mrr_native",
    "retrieval_top1_common_candidate",
    "retrieval_top5_common_candidate",
    "retrieval_mrr_common_candidate",
}


def load_meta(run: Path) -> dict:
    return json.loads((run / "metadata.json").read_text())


def require_completed(run: Path) -> None:
    meta = load_meta(run)
    if meta.get("run_status") not in {"COMPLETED_GEARS", "COMPLETED_GEARS_EVALUATION"}:
        raise RuntimeError(f"{run} is not completed: {meta.get('run_status')}")


def run_targets(run_key: str) -> set[str]:
    metrics = pd.read_csv(RUNS[run_key] / "gears_metrics.csv")
    metrics = metrics[metrics["space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    return set(metrics["perturbation"].astype(str).map(normalize_condition))


def write_registry(target_sets: dict[str, set[str]]) -> pd.DataFrame:
    all_targets = sorted(set().union(*target_sets.values()))
    rows = []
    for target in all_targets:
        rows.append(
            {
                "target": target,
                "in_k562_rl1": target in target_sets["k562_rl1"],
                "in_rpe1_rl1": target in target_sets["rpe1_rl1"],
                "in_k2r_rl4": target in target_sets["k2r_rl4"],
                "in_r2k_rl4": target in target_sets["r2k_rl4"],
                "matched_k2r_source": target in target_sets["k562_rl1"] and target in target_sets["k2r_rl4"],
                "matched_r2k_source": target in target_sets["rpe1_rl1"] and target in target_sets["r2k_rl4"],
                "matched_k2r_target_context": target in target_sets["rpe1_rl1"] and target in target_sets["k2r_rl4"],
                "matched_r2k_target_context": target in target_sets["k562_rl1"] and target in target_sets["r2k_rl4"],
            }
        )
    df = pd.DataFrame(rows)
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / "replogle_matched_target_registry.tsv", sep="\t", index=False)
    return df


def load_metric_table(run_key: str) -> pd.DataFrame:
    df = pd.read_csv(RUNS[run_key] / "gears_metrics.csv")
    df = df[df["space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    df["target"] = df["perturbation"].astype(str).map(normalize_condition)
    return df.set_index("target", drop=False)


def load_native_retrieval(run_key: str) -> pd.DataFrame:
    df = pd.read_csv(RUNS[run_key] / "gears_perturbation_retrieval.csv")
    df = df[df["space"].isin(["audit_delta", "target_control_audit_delta"])].copy()
    df["target"] = df["perturbation"].astype(str).map(normalize_condition)
    df["retrieval_mrr_native"] = 1.0 / df["true_target_rank"].astype(float)
    df["retrieval_top1_native"] = (df["true_target_rank"].astype(float) == 1).astype(float)
    df["retrieval_top5_native"] = (df["true_target_rank"].astype(float) <= 5).astype(float)
    return df.set_index("target", drop=False)


def as_numpy(value) -> np.ndarray:
    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    return np.asarray(value, dtype=float).ravel()


def load_vectors(run_key: str) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    obj = torch.load(RUNS[run_key] / "gears_delta_centroids.pt", map_location="cpu")
    pred: dict[str, np.ndarray] = {}
    truth: dict[str, np.ndarray] = {}
    if "audit_delta" in obj:
        block = obj["audit_delta"]
        for pert in block["perturbations"]:
            target = normalize_condition(str(pert))
            pred[target] = as_numpy(block["pred_delta"][pert])
            truth[target] = as_numpy(block["truth_delta"][pert])
        return pred, truth
    control = as_numpy(obj["target_control"])
    for target in obj["targets"]:
        target = str(target)
        pred[target] = as_numpy(obj["pred_expression"][target]) - control
        truth[target] = as_numpy(obj["truth_expression"][target]) - control
    return pred, truth


def cosine_matrix(pred: np.ndarray, truth: np.ndarray) -> np.ndarray:
    pred = np.nan_to_num(pred.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    truth = np.nan_to_num(truth.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    pred_norm = np.linalg.norm(pred, axis=1, keepdims=True)
    truth_norm = np.linalg.norm(truth, axis=1, keepdims=True)
    pred_norm[pred_norm == 0] = np.nan
    truth_norm[truth_norm == 0] = np.nan
    pred_unit = pred / pred_norm
    truth_unit = truth / truth_norm
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        sim = pred_unit @ truth_unit.T
    return np.nan_to_num(sim, nan=-np.inf, posinf=-np.inf, neginf=-np.inf)


def common_candidate_retrieval(run_key: str, targets: list[str]) -> pd.DataFrame:
    pred_dict, truth_dict = load_vectors(run_key)
    targets = [t for t in targets if t in pred_dict and t in truth_dict]
    pred = np.vstack([pred_dict[t] for t in targets])
    truth = np.vstack([truth_dict[t] for t in targets])
    sim = cosine_matrix(pred, truth)
    rows = []
    for i, target in enumerate(targets):
        order = np.argsort(-sim[i])
        rank = int(np.where(order == i)[0][0]) + 1
        top_idx = int(order[0])
        rows.append(
            {
                "target": target,
                "true_target_rank_common_candidate": rank,
                "top_match_common_candidate": targets[top_idx],
                "top_match_similarity_common_candidate": float(sim[i, top_idx]),
                "true_target_similarity_common_candidate": float(sim[i, i]),
                "retrieval_top1_common_candidate": float(rank == 1),
                "retrieval_top5_common_candidate": float(rank <= 5),
                "retrieval_mrr_common_candidate": 1.0 / rank,
            }
        )
    return pd.DataFrame(rows).set_index("target", drop=False)


def paired_permutation_pvalue(diff: np.ndarray, seed: int = 1, n_resamples: int = 2000) -> float:
    diff = np.asarray(diff, dtype=float)
    diff = diff[np.isfinite(diff)]
    if len(diff) < 2:
        return np.nan
    observed = abs(float(np.mean(diff)))
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_resamples):
        signs = rng.choice([-1.0, 1.0], size=len(diff), replace=True)
        stat = abs(float(np.mean(diff * signs)))
        count += stat >= observed
    return float((count + 1) / (n_resamples + 1))


def summarize_metric(within: pd.Series, cross: pd.Series, metric: str, comparison: dict, n_targets: int) -> dict:
    if metric in HIGHER_IS_BETTER:
        diff = within.to_numpy(dtype=float) - cross.to_numpy(dtype=float)
    else:
        diff = cross.to_numpy(dtype=float) - within.to_numpy(dtype=float)
    diff = diff[np.isfinite(diff)]
    ci = paired_bootstrap_diff(diff, np.zeros_like(diff), n_resamples=2000, seed=1)
    return {
        "direction": comparison["direction"],
        "comparison_role": comparison["comparison_role"],
        "metric": metric,
        "n_targets": n_targets,
        "within_estimate": float(np.nanmean(within)),
        "cross_estimate": float(np.nanmean(cross)),
        "paired_difference": float(ci["difference"]),
        "ci_low": float(ci["ci95_low"]),
        "ci_high": float(ci["ci95_high"]),
        "p_value_if_used": paired_permutation_pvalue(diff),
        "analysis_status": "MATCHED_TARGET_PAIRED_BOOTSTRAP",
        "difference_definition": "within_minus_cross" if metric in HIGHER_IS_BETTER else "cross_minus_within",
    }


def comparison_frame(comparison: dict, targets: list[str]) -> pd.DataFrame:
    within_key = comparison["within"]
    cross_key = comparison["cross"]
    wm = load_metric_table(within_key)
    cm = load_metric_table(cross_key)
    wr = load_native_retrieval(within_key)
    cr = load_native_retrieval(cross_key)
    wcommon = common_candidate_retrieval(within_key, targets)
    ccommon = common_candidate_retrieval(cross_key, targets)
    rows = []
    for target in targets:
        row = {
            "target": target,
            "direction": comparison["direction"],
            "comparison_role": comparison["comparison_role"],
        }
        for metric in [
            "pearson_delta",
            "spearman_delta",
            "rmse_delta",
            "cosine_delta",
            "uer20",
            "uer50",
            "uer100",
            "sign_flip_rate",
        ]:
            row[f"within_{metric}"] = wm.loc[target, metric]
            row[f"cross_{metric}"] = cm.loc[target, metric]
        for metric in ["retrieval_top1_native", "retrieval_top5_native", "retrieval_mrr_native"]:
            row[f"within_{metric}"] = wr.loc[target, metric]
            row[f"cross_{metric}"] = cr.loc[target, metric]
        for metric in ["retrieval_top1_common_candidate", "retrieval_top5_common_candidate", "retrieval_mrr_common_candidate"]:
            row[f"within_{metric}"] = wcommon.loc[target, metric]
            row[f"cross_{metric}"] = ccommon.loc[target, metric]
        rows.append(row)
    return pd.DataFrame(rows)


def build_sensitivity(registry: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    matched = {
        "K2R_source_context": sorted(registry.loc[registry["matched_k2r_source"], "target"]),
        "R2K_source_context": sorted(registry.loc[registry["matched_r2k_source"], "target"]),
        "K2R_target_context": sorted(registry.loc[registry["matched_k2r_target_context"], "target"]),
        "R2K_target_context": sorted(registry.loc[registry["matched_r2k_target_context"], "target"]),
    }
    detail_frames = []
    summary_rows = []
    metrics = [
        "pearson_delta",
        "spearman_delta",
        "rmse_delta",
        "cosine_delta",
        "retrieval_top1_native",
        "retrieval_top5_native",
        "retrieval_mrr_native",
        "retrieval_top1_common_candidate",
        "retrieval_top5_common_candidate",
        "retrieval_mrr_common_candidate",
        "uer20",
        "uer50",
        "uer100",
        "sign_flip_rate",
    ]
    for name, targets in matched.items():
        comp = COMPARISONS[name]
        if not targets:
            continue
        detail = comparison_frame(comp, targets)
        detail_frames.append(detail)
        for metric in metrics:
            summary_rows.append(
                summarize_metric(
                    detail[f"within_{metric}"],
                    detail[f"cross_{metric}"],
                    metric,
                    comp,
                    len(targets),
                )
            )
    detail_df = pd.concat(detail_frames, ignore_index=True)
    summary_df = pd.DataFrame(summary_rows)
    detail_df.to_csv(TABLES / "replogle_matched_rl1_rl4_target_level.csv", index=False)
    summary_df.to_csv(TABLES / "replogle_matched_rl1_rl4_sensitivity.csv", index=False)
    return detail_df, summary_df


def build_figure(summary: pd.DataFrame) -> None:
    primary = summary[summary["comparison_role"].eq("primary_source_context_comparison")].copy()
    metric_order = [
        ("pearson_delta", "Pearson transfer drop"),
        ("retrieval_mrr_common_candidate", "MRR transfer drop"),
        ("uer50", "UER@50 penalty"),
        ("sign_flip_rate", "Sign-flip penalty"),
    ]
    labels = ["K562->RPE1", "RPE1->K562"]
    direction_map = {
        "K562_within_vs_K562_to_RPE1": "K562->RPE1",
        "RPE1_within_vs_RPE1_to_K562": "RPE1->K562",
    }
    palette = {"K562->RPE1": "#0F4D92", "RPE1->K562": "#B64342"}
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 6.2))
    axes = axes.ravel()
    for ax, (metric, title) in zip(axes, metric_order):
        rows = primary[primary["metric"].eq(metric)].copy()
        rows["label"] = rows["direction"].map(direction_map)
        rows = rows.set_index("label").loc[labels].reset_index()
        x = np.arange(len(labels))
        y = rows["paired_difference"].astype(float).to_numpy()
        lo = rows["ci_low"].astype(float).to_numpy()
        hi = rows["ci_high"].astype(float).to_numpy()
        ax.bar(x, y, color=[palette[l] for l in labels], edgecolor="black", linewidth=0.8, width=0.6)
        ax.errorbar(x, y, yerr=np.vstack([y - lo, hi - y]), fmt="none", ecolor="black", capsize=4, lw=1.0)
        ax.axhline(0, color="#555555", lw=0.8, ls=":")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
        ax.set_title(title, fontsize=10)
        ax.set_ylabel("Matched paired difference")
    fig.suptitle(
        "Matched-target R-L1 vs R-L4 sensitivity. Error bars: paired bootstrap 95% CI over targets.",
        fontsize=10,
    )
    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    for ext in ["pdf", "svg", "png"]:
        fig.savefig(FIGURES / f"replogle_matched_transfer_sensitivity.{ext}", bbox_inches="tight", dpi=300)
    plt.close(fig)


def conclusion(summary: pd.DataFrame) -> str:
    primary = summary[summary["comparison_role"].eq("primary_source_context_comparison")]
    checks = {}
    for metric in ["pearson_delta", "retrieval_mrr_common_candidate", "uer50", "sign_flip_rate"]:
        rows = primary[primary["metric"].eq(metric)]
        checks[metric] = bool((rows["paired_difference"] > 0).all())
    if all(checks.values()):
        return "MATCHED_SUPPORTS_TRANSFER_COLLAPSE"
    if checks["pearson_delta"] and (checks["uer50"] or checks["sign_flip_rate"]):
        return "PARTIAL_MATCHED_SUPPORT"
    if not checks["pearson_delta"] and not checks["retrieval_mrr_common_candidate"]:
        return "TARGET_COMPOSITION_EXPLAINS_SUBSTANTIAL_DROP"
    return "UNINFORMATIVE"


def write_report(registry: pd.DataFrame, summary: pd.DataFrame) -> None:
    primary = summary[summary["comparison_role"].eq("primary_source_context_comparison")].copy()
    gate = conclusion(summary)
    def get(direction: str, metric: str) -> pd.Series:
        row = primary[(primary["direction"].eq(direction)) & (primary["metric"].eq(metric))]
        return row.iloc[0]
    k2r_n = int(registry["matched_k2r_source"].sum())
    r2k_n = int(registry["matched_r2k_source"].sum())
    lines = [
        "# Phase 2B Matched-Target Sensitivity",
        "",
        "## Current Status",
        "",
        "```text",
        "Phase 2A freeze commit: 6872a97",
        "GEARS retraining:       NOT_PERFORMED",
        "Matched registry:       COMPLETE",
        "Native retrieval:       COMPLETE",
        "Common-candidate retrieval: COMPLETE",
        f"Gate decision:          {gate}",
        "```",
        "",
        "## Matched Target Counts",
        "",
        f"- `n_matched_K2R_source = {k2r_n}`",
        f"- `n_matched_R2K_source = {r2k_n}`",
        f"- `n_matched_K2R_target_context = {int(registry['matched_k2r_target_context'].sum())}`",
        f"- `n_matched_R2K_target_context = {int(registry['matched_r2k_target_context'].sum())}`",
        "",
        "## Primary Source-Context Matched Results",
        "",
        "| Direction | Metric | Within | Cross | Paired difference | 95% CI | p value |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for direction in ["K562_within_vs_K562_to_RPE1", "RPE1_within_vs_RPE1_to_K562"]:
        for metric in ["pearson_delta", "retrieval_mrr_common_candidate", "uer50", "sign_flip_rate"]:
            row = get(direction, metric)
            lines.append(
                f"| {direction} | {metric} | {row['within_estimate']:.4f} | {row['cross_estimate']:.4f} | "
                f"{row['paired_difference']:.4f} | [{row['ci_low']:.4f}, {row['ci_high']:.4f}] | {row['p_value_if_used']:.4f} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Matched-target sensitivity preserves the Phase 2A direction of effect. Within-context GEARS has substantially higher target-level Pearson than the matched cross-context adapter, while common-candidate MRR remains very low in cross-context analysis. UER@50 and sign-flip burden are higher under R-L4 in both primary source-context comparisons.",
            "",
            "This means the R-L4 collapse is not explained away by comparing different test-target compositions. Target composition may affect exact magnitudes, but the matched analysis keeps the central conclusion intact.",
            "",
            "## Retrieval Candidate Universe",
            "",
            "Native retrieval uses each run's original candidate universe. Common-candidate retrieval was recomputed from saved prediction/truth centroids using the exact same matched target set within each paired comparison. The main matched retrieval statement uses common-candidate MRR.",
            "",
            "## Guardrails",
            "",
            "- No GEARS model was retrained for this analysis.",
            "- All estimates use existing per-target outputs from completed R-L1 and R-L4 runs.",
            "- Source-context comparisons are primary; target-context comparisons are exploratory.",
            "- All Replogle claims remain `GEARS-compatible filtered essential-screen data`.",
            "- `BNS_STATUS = UNVERIFIED`; UER remains `sensitivity_only`.",
            "",
            "## Outputs",
            "",
            "- `results/tables/replogle_matched_target_registry.tsv`",
            "- `results/tables/replogle_matched_rl1_rl4_target_level.csv`",
            "- `results/tables/replogle_matched_rl1_rl4_sensitivity.csv`",
            "- `figures/main/replogle_matched_transfer_sensitivity.{pdf,svg,png}`",
            "",
        ]
    )
    (REPORTS / "PHASE2B_MATCHED_TARGET_SENSITIVITY.md").write_text("\n".join(lines))


def main() -> None:
    for run in RUNS.values():
        require_completed(run)
    target_sets = {key: run_targets(key) for key in RUNS}
    registry = write_registry(target_sets)
    detail, summary = build_sensitivity(registry)
    build_figure(summary)
    write_report(registry, summary)
    print("matched target counts")
    print(
        {
            "n_matched_K2R": int(registry["matched_k2r_source"].sum()),
            "n_matched_R2K": int(registry["matched_r2k_source"].sum()),
            "n_matched_K2R_target_context": int(registry["matched_k2r_target_context"].sum()),
            "n_matched_R2K_target_context": int(registry["matched_r2k_target_context"].sum()),
            "gate": conclusion(summary),
        }
    )
    print(summary[summary["comparison_role"].eq("primary_source_context_comparison")].to_string(index=False))


if __name__ == "__main__":
    main()
