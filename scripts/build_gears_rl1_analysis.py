from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src.statistics.bootstrap import bootstrap_mean_ci

warnings.filterwarnings("ignore")

REPL = Path("results/replogle")
GEARS_DIR = REPL / "gears"
TABLES = Path("results/tables")
FIGURES = Path("figures/main")

NORMAN_ROWS = [
    {"setting": "Norman L1 GEARS", "split": "L1", "n": 55, "pearson": 0.988748, "ci_low": 0.986001, "ci_high": 0.991368,
     "top1": 0.200, "top5": 0.491, "mrr": 0.327747, "uer50": 0.0, "sign_flip": 0.0},
    {"setting": "Norman L2 GEARS", "split": "L2", "n": 40, "pearson": 0.983792, "ci_low": 0.979453, "ci_high": 0.987480,
     "top1": 0.075, "top5": 0.150, "mrr": 0.147070, "uer50": 0.0, "sign_flip": 0.0},
    {"setting": "Norman L3 GEARS", "split": "L3", "n": 25, "pearson": 0.984334, "ci_low": 0.978093, "ci_high": 0.989626,
     "top1": 0.080, "top5": 0.320, "mrr": 0.206694, "uer50": 0.0, "sign_flip": 0.0},
]

SETTING_LABELS = {
    "Norman L1 GEARS": "Norman L1",
    "Norman L2 GEARS": "Norman L2",
    "Norman L3 GEARS": "Norman L3",
    "Replogle K562 R-L1 GEARS": "Replogle K562 L1",
    "Replogle RPE1 R-L1 GEARS": "Replogle RPE1 L1",
}


def load_run(key: str) -> tuple[Path, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    runs = sorted(GEARS_DIR.glob(f"rl1_{key}_*"))
    if not runs:
        raise FileNotFoundError(f"no full run for {key}")
    run = runs[-1]
    meta = json.loads((run / "metadata.json").read_text())
    if meta.get("run_status") not in ("COMPLETED_GEARS", "COMPLETED_GEARS_EVALUATION"):
        raise SystemExit(f"latest run {run.name} not completed: {meta.get('run_status')}")
    metrics = pd.read_csv(run / "gears_metrics.csv")
    retrieval = pd.read_csv(run / "gears_perturbation_retrieval.csv")
    summary = pd.read_csv(run / "gears_summary.csv")
    return run, metrics, retrieval, summary, meta


def space_block(metrics: pd.DataFrame, retrieval: pd.DataFrame, space: str) -> dict:
    m = metrics[metrics["space"].eq(space)].copy()
    r = retrieval[retrieval["space"].eq(space)].copy()
    pearson_ci = bootstrap_mean_ci(m["pearson_delta"].to_numpy(), n_resamples=2000, seed=1)
    uer50_ci = bootstrap_mean_ci(m["uer50"].to_numpy(), n_resamples=2000, seed=1)
    top1 = float(np.mean(r["true_target_rank"] == 1))
    top5 = float(np.mean(r["true_target_rank"] <= 5))
    rrs = 1.0 / r["true_target_rank"].astype(float)
    mrr_ci = bootstrap_mean_ci(rrs.to_numpy(), n_resamples=2000, seed=1)
    return {
        "space": space,
        "n": int(m["perturbation"].nunique()),
        "pearson": pearson_ci["mean"],
        "pearson_ci_low": pearson_ci["ci95_low"],
        "pearson_ci_high": pearson_ci["ci95_high"],
        "spearman": float(m["spearman_delta"].mean()),
        "rmse": float(m["rmse_delta"].mean()),
        "top1": top1,
        "top5": top5,
        "mrr": mrr_ci["mean"],
        "mrr_ci_low": mrr_ci["ci95_low"],
        "mrr_ci_high": mrr_ci["ci95_high"],
        "uer20": float(m["uer20"].mean()),
        "uer50": uer50_ci["mean"],
        "uer50_ci_low": uer50_ci["ci95_low"],
        "uer50_ci_high": uer50_ci["ci95_high"],
        "uer100": float(m["uer100"].mean()),
        "sign_flip": float(m["sign_flip_rate"].mean()),
        "null_status": "sensitivity_only",
    }


def build_rl1_summary() -> pd.DataFrame:
    rows = []
    for key, cell_line, split in [("k562", "K562", "R-L1-K562"), ("rpe1", "RPE1", "R-L1-RPE1")]:
        run, metrics, retrieval, summary, meta = load_run(key)
        for space in ["audit_delta", "gears_raw"]:
            b = space_block(metrics, retrieval, space)
            rows.append(
                {
                    "dataset": "Replogle_GEARS_filtered",
                    "cell_line": cell_line,
                    "split": split,
                    "model": "GEARS_cell_gears_0.1.2",
                    "model_type": "GEARS",
                    "seed": meta["seed"],
                    "pearson_delta": b["pearson"],
                    "pearson_ci_low": b["pearson_ci_low"],
                    "pearson_ci_high": b["pearson_ci_high"],
                    "spearman_delta": b["spearman"],
                    "rmse_delta": b["rmse"],
                    "top1": b["top1"],
                    "top5": b["top5"],
                    "mrr": b["mrr"],
                    "mrr_ci_low": b["mrr_ci_low"],
                    "mrr_ci_high": b["mrr_ci_high"],
                    "uer20": b["uer20"],
                    "uer50": b["uer50"],
                    "uer100": b["uer100"],
                    "sign_flip_rate": b["sign_flip"],
                    "bns": np.nan,
                    "bns_status": "UNVERIFIED",
                    "filtered_data": True,
                    "performance_eligible": True,
                    "run_status": "COMPLETED_GEARS_EVALUATION",
                    "metric_space": space,
                    "n_test_targets": b["n"],
                    "null_status": b["null_status"],
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(REPL / "gears_rl1_summary.csv", index=False)
    print(df.to_string(index=False))
    return df


def build_norman_comparison() -> pd.DataFrame:
    rows = []
    for r in NORMAN_ROWS:
        rows.append(
            {
                "setting": r["setting"],
                "dataset": "Norman2019_GEARS_processed_mirror",
                "split": r["split"],
                "model": "GEARS_cell_gears_0.1.2",
                "metric_space": "gears_raw",
                "filtered_data": False,
                "n_test_perturbations": r["n"],
                "pearson_delta": r["pearson"],
                "pearson_ci_low": r["ci_low"],
                "pearson_ci_high": r["ci_high"],
                "retrieval_top1": r["top1"],
                "retrieval_top5": r["top5"],
                "retrieval_mrr": r["mrr"],
                "uer50": r["uer50"],
                "sign_flip_rate": r["sign_flip"],
                "bns_status": "UNVERIFIED",
                "note": "Frozen Norman pilot row; raw GEARS space; upper-bound and replicate status unverified.",
            }
        )
    for key, cell_line, split in [("k562", "K562", "R-L1-K562"), ("rpe1", "RPE1", "R-L1-RPE1")]:
        run, metrics, retrieval, summary, meta = load_run(key)
        b = space_block(metrics, retrieval, "gears_raw")
        rows.append(
            {
                "setting": f"Replogle {cell_line} R-L1 GEARS",
                "dataset": "Replogle_GEARS_filtered",
                "split": split,
                "model": "GEARS_cell_gears_0.1.2",
                "metric_space": "gears_raw",
                "filtered_data": True,
                "n_test_perturbations": b["n"],
                "pearson_delta": b["pearson"],
                "pearson_ci_low": b["pearson_ci_low"],
                "pearson_ci_high": b["pearson_ci_high"],
                "retrieval_top1": b["top1"],
                "retrieval_top5": b["top5"],
                "retrieval_mrr": b["mrr"],
                "uer50": b["uer50"],
                "sign_flip_rate": b["sign_flip"],
                "bns_status": "UNVERIFIED",
                "note": "Replogle analyses use GEARS-compatible filtered essential-screen data; BNS unverified; metric space gears_raw for direct Norman comparability.",
            }
        )
    df = pd.DataFrame(rows)
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / "norman_replogle_rl1_comparison.csv", index=False)
    print(df.to_string(index=False))
    return df


def build_divergence_profile(audit_delta_rows: dict, raw_rows: dict) -> pd.DataFrame:
    settings = {
        "Norman L1 GEARS": {"pearson": NORMAN_ROWS[0]["pearson"], "mrr": NORMAN_ROWS[0]["mrr"], "uer50": NORMAN_ROWS[0]["uer50"]},
        "Norman L2 GEARS": {"pearson": NORMAN_ROWS[1]["pearson"], "mrr": NORMAN_ROWS[1]["mrr"], "uer50": NORMAN_ROWS[1]["uer50"]},
        "Norman L3 GEARS": {"pearson": NORMAN_ROWS[2]["pearson"], "mrr": NORMAN_ROWS[2]["mrr"], "uer50": NORMAN_ROWS[2]["uer50"]},
        "Replogle K562 R-L1 GEARS": {"pearson": raw_rows["k562"]["pearson"], "mrr": raw_rows["k562"]["mrr"], "uer50": raw_rows["k562"]["uer50"]},
        "Replogle RPE1 R-L1 GEARS": {"pearson": raw_rows["rpe1"]["pearson"], "mrr": raw_rows["rpe1"]["mrr"], "uer50": raw_rows["rpe1"]["uer50"]},
    }
    df = pd.DataFrame(settings).T.reset_index().rename(columns={"index": "setting"})
    df["rank_by_global_fit"] = df["pearson"].rank(ascending=False, method="min").astype(int)
    df["rank_by_specificity"] = df["mrr"].rank(ascending=False, method="min").astype(int)
    df["rank_by_hallucination"] = df["uer50"].rank(ascending=True, method="min").astype(int)
    df["global_minus_specificity_rank"] = df["rank_by_global_fit"] - df["rank_by_specificity"]
    df.to_csv(TABLES / "metric_divergence_profile.csv", index=False)
    print(df.to_string(index=False))
    return df


def fig1(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    setting_order = ["Norman L1", "Norman L2", "Norman L3", "Replogle K562 L1", "Replogle RPE1 L1"]
    dat = df.set_index("short") if "short" in df else None
    def yerr(values: list[tuple[float, float, float]]) -> np.ndarray:
        return np.array(
            [
                [0.0 if np.isnan(lo) else abs(mid - lo) for mid, lo, hi in values],
                [0.0 if np.isnan(hi) else abs(hi - mid) for mid, lo, hi in values],
            ]
        )
    # Panel A: delta-Pearson
    ax = axes[0]
    vals = [df.loc[df["short"] == s, ["pearson", "pearson_ci_low", "pearson_ci_high"]].iloc[0] for s in setting_order]
    ax.errorbar(
        range(len(setting_order)), [v["pearson"] for v in vals],
        yerr=yerr([(v["pearson"], v["pearson_ci_low"], v["pearson_ci_high"]) for v in vals]),
        fmt="o", color="#1a509a", capsize=4, ms=6, lw=1.2,
    )
    ax.set_xticks(range(len(setting_order))); ax.set_xticklabels(setting_order, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Delta-Pearson")
    ax.set_title("A: Global expression fit", fontsize=10)
    ax.set_ylim(0.6, 1.02)
    # Panel B: MRR
    ax = axes[1]
    vals = [df.loc[df["short"] == s, ["mrr", "mrr_ci_low", "mrr_ci_high"]].iloc[0] for s in setting_order]
    ax.errorbar(
        range(len(setting_order)), [v["mrr"] for v in vals],
        yerr=yerr([(v["mrr"], v["mrr_ci_low"], v["mrr_ci_high"]) for v in vals]),
        fmt="s", color="#c0392b", capsize=4, ms=6, lw=1.2,
    )
    ax.set_xticks(range(len(setting_order))); ax.set_xticklabels(setting_order, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Retrieval MRR")
    ax.set_title("B: Perturbation-specific retrieval", fontsize=10)
    ax.set_ylim(0.0, 0.55)
    # Panel C: UER@50
    ax = axes[2]
    vals = [df.loc[df["short"] == s, ["uer50", "uer50_ci_low", "uer50_ci_high"]].iloc[0] for s in setting_order]
    ax.errorbar(
        range(len(setting_order)), [v["uer50"] for v in vals],
        yerr=yerr([(v["uer50"], v["uer50_ci_low"], v["uer50_ci_high"]) for v in vals]),
        fmt="^", color="#7f8c8d", capsize=4, ms=6, lw=1.2,
    )
    ax.set_xticks(range(len(setting_order))); ax.set_xticklabels(setting_order, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("UER@50")
    ax.set_title("C: Unsupported effect rate", fontsize=10)
    ax.set_ylim(-0.02, 0.7)
    fig.suptitle(
        "Metric divergence profile. Replogle analyses use GEARS-compatible filtered essential-screen data.\n"
        "Bars: 95% bootstrap CI over perturbations (2000 resamples). Norman rows frozen from pilot; Replogle rows in gears_raw space (Norman-comparable).",
        fontsize=8, y=1.02,
    )
    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    for ext in ["pdf", "svg", "png"]:
        fig.savefig(FIGURES / f"norman_replogle_metric_divergence.{ext}", bbox_inches="tight")
    plt.close(fig)


def fig2() -> None:
    summary = pd.read_csv(REPL / "replogle_summary.csv")
    rows = {}
    for split, cell_line in [("R-L1-K562", "K562"), ("R-L1-RPE1", "RPE1")]:
        s = summary[summary["split"].eq(split)]
        def grab(model):
            row = s[s["model"].eq(model)]
            return row.iloc[0] if len(row) else None
        rows[cell_line] = {
            "GEARS": None,
            "B0 no-change": grab("B0_no_change"),
            "Context mean (B1/B2/B5, FP-1)": grab("B1_global_perturbed_mean"),
            "Label-shuffled (FP-3)": grab("FP3_label_shuffled_mean_effect"),
        }
    run_k, mk, rk, sk, meta_k = load_run("k562")
    run_r, mr, rr, sr, meta_r = load_run("rpe1")
    bk = space_block(mk, rk, "audit_delta")
    br = space_block(mr, rr, "audit_delta")
    rows["K562"]["GEARS"] = {"pearson": bk["pearson"], "mrr": bk["mrr"]}
    rows["RPE1"]["GEARS"] = {"pearson": br["pearson"], "mrr": br["mrr"]}

    def p(row):
        if row is None:
            return None
        if "pearson" in row and isinstance(row.get("pearson"), (int, float)):
            return {"pearson": row["pearson"], "mrr": row["mrr"]}
        try:
            pearson = row["pearson_delta"]
            mrr = row["mrr"] if np.isfinite(row["mrr"]) else np.nan
        except (KeyError, TypeError):
            return None
        return {"pearson": pearson, "mrr": mrr}

    colors = {"GEARS": "#1a509a", "B0 no-change": "#7f8c8d", "Context mean (B1/B2/B5, FP-1)": "#e67e22", "Label-shuffled (FP-3)": "#8e44ad"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for ax, cell_line in zip(axes, ["K562", "RPE1"]):
        labels = list(rows[cell_line])
        perrs, mrrs = [], []
        for lab in labels:
            d = p(rows[cell_line][lab])
            perrs.append(d["pearson"] if d else np.nan)
            mrrs.append(d["mrr"] if d else np.nan)
        for lab, pe, mr in zip(labels, perrs, mrrs):
            ax.scatter(pe, mr, s=110, color=colors.get(lab, "#333333"), label=lab, alpha=0.95, edgecolor="white", linewidth=0.7)
            ax.annotate("GEARS" if lab == "GEARS" else "", (pe, mr), xytext=(6, 6), textcoords="offset points", fontsize=8)
        ax.axvline(0.0, color="grey", lw=0.6, ls=":")
        ax.set_xlabel("Delta-Pearson (audit-delta space)")
        ax.set_ylabel("Retrieval MRR (audit-delta space)")
        ax.set_title(f"{cell_line} R-L1: GEARS vs baselines and falsification probes", fontsize=10)
        ax.legend(fontsize=7, loc="upper left", framealpha=0.9)
    fig.suptitle(
        "Global-fit vs perturbation-specific signal. Replogle analyses use GEARS-compatible filtered essential-screen data.\n"
        "GEARS shown in audit-delta space (same convention as baselines/probes).",
        fontsize=8, y=1.02,
    )
    fig.tight_layout()
    for ext in ["pdf", "svg", "png"]:
        fig.savefig(FIGURES / f"replogle_gears_vs_probes.{ext}", bbox_inches="tight")
    plt.close(fig)


def stats_report(raw: dict, audit: dict) -> None:
    if "k562" in audit and "rpe1" in audit:
        print("\n== Within-Replogle K562 vs RPE1 (audit-delta space; perturbation-level bootstrap 95% CI) ==")
        for metric, key in [("Pearson", "pearson"), ("MRR", "mrr"), ("UER50", "uer50")]:
            a = audit["k562"]; b = audit["rpe1"]
            print(f"{metric}: K562 {a[key]:.4f} [{a[key+'_ci_low']:.4f},{a[key+'_ci_high']:.4f}] | RPE1 {b[key]:.4f} [{b[key+'_ci_low']:.4f},{b[key+'_ci_high']:.4f}] | overlap=", end="")
            overlap = not (a[key + "_ci_high"] < b[key + "_ci_low"] or b[key + "_ci_high"] < a[key + "_ci_low"])
            print(overlap)
    print("\n== Norman vs Replogle (gears_raw space) ==")
    for row in NORMAN_ROWS:
        print(f"{row['setting']}: pearson {row['pearson']:.4f} mrr {row['mrr']:.4f} uer50 {row['uer50']}")
    for key, label in [("k562", "Replogle K562"), ("rpe1", "Replogle RPE1")]:
        if key not in raw:
            continue
        b = raw[key]
        print(f"{label}: pearson {b['pearson']:.4f} ({b['pearson_ci_low']:.4f},{b['pearson_ci_high']:.4f}) mrr {b['mrr']:.4f} top1 {b['top1']:.4f} uer50 {b['uer50']:.4f}")


def build_probe_comparison_table() -> None:
    """GEARS vs baselines/probes in audit-delta space (read-only reuse of baseline outputs)."""
    summary = pd.read_csv(REPL / "replogle_summary.csv")
    rows = []
    for key, cell_line, split in [("k562", "K562", "R-L1-K562"), ("rpe1", "RPE1", "R-L1-RPE1")]:
        run, metrics, retrieval, summary_run, meta = load_run(key)
        b = space_block(metrics, retrieval, "audit_delta")
        base = summary[summary["split"].eq(split)]
        for _, r in base.iterrows():
            rows.append(
                {
                    "context": cell_line,
                    "split": split,
                    "model": r["model"],
                    "run_status": r["run_status"],
                    "metric_space": "audit_delta",
                    "filtered_data": True,
                    "pearson_delta": r["pearson_delta"],
                    "pearson_ci_low": r["pearson_ci_low"],
                    "pearson_ci_high": r["pearson_ci_high"],
                    "retrieval_top1": r["retrieval_top1"],
                    "retrieval_top5": r["retrieval_top5"],
                    "retrieval_mrr": r["mrr"],
                    "uer50": r["uer50"],
                    "sign_flip_rate": r["sign_flip_rate"],
                    "bns_status": "UNVERIFIED",
                    "source": "replogle_summary.csv",
                }
            )
        rows.append(
            {
                "context": cell_line,
                "split": split,
                "model": "GEARS_cell_gears_0.1.2",
                "run_status": "COMPLETED_GEARS_EVALUATION",
                "metric_space": "audit_delta",
                "filtered_data": True,
                "pearson_delta": b["pearson"],
                "pearson_ci_low": b["pearson_ci_low"],
                "pearson_ci_high": b["pearson_ci_high"],
                "retrieval_top1": b["top1"],
                "retrieval_top5": b["top5"],
                "retrieval_mrr": b["mrr"],
                "uer50": b["uer50"],
                "sign_flip_rate": b["sign_flip"],
                "bns_status": "UNVERIFIED",
                "source": "gears_rl1_run",
            }
        )
    df = pd.DataFrame(rows)
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / "replogle_gears_vs_probes.csv", index=False)
    print(df.to_string(index=False))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["k562", "rpe1"], default=None, help="analyze a single completed context")
    args = parser.parse_args()
    keys = [args.only] if args.only else ["k562", "rpe1"]
    raw = {}
    audit = {}
    for key, cell_line, split in [("k562", "K562", "R-L1-K562"), ("rpe1", "RPE1", "R-L1-RPE1")]:
        if key not in keys:
            continue
        run, metrics, retrieval, summary, meta = load_run(key)
        raw[key] = space_block(metrics, retrieval, "gears_raw")
        audit[key] = space_block(metrics, retrieval, "audit_delta")
    df = build_rl1_summary()
    dfa = df[df["metric_space"].eq("audit_delta")].copy()
    dfr = df[df["metric_space"].eq("gears_raw")].copy()
    ordering = {
        "Norman L1": ("Norman L1 GEARS", NORMAN_ROWS[0]),
        "Norman L2": ("Norman L2 GEARS", NORMAN_ROWS[1]),
        "Norman L3": ("Norman L3 GEARS", NORMAN_ROWS[2]),
        "Replogle K562 L1": ("Replogle K562 R-L1 GEARS", raw.get("k562", {})),
        "Replogle RPE1 L1": ("Replogle RPE1 R-L1 GEARS", raw.get("rpe1", {})),
    }
    def figure_row(short: str, src: dict) -> dict:
        if "pearson_ci_low" in src:
            pearson_ci_low = src["pearson_ci_low"]
            pearson_ci_high = src["pearson_ci_high"]
        else:
            pearson_ci_low = src.get("ci_low", np.nan)
            pearson_ci_high = src.get("ci_high", np.nan)
        return {
            "short": short,
            "pearson": src["pearson"],
            "pearson_ci_low": pearson_ci_low,
            "pearson_ci_high": pearson_ci_high,
            "mrr": src["mrr"],
            "mrr_ci_low": src.get("mrr_ci_low", np.nan),
            "mrr_ci_high": src.get("mrr_ci_high", np.nan),
            "uer50": src["uer50"],
            "uer50_ci_low": src.get("uer50_ci_low", np.nan),
            "uer50_ci_high": src.get("uer50_ci_high", np.nan),
        }

    fig_rows = []
    for short, (setting, src) in ordering.items():
        if not src:
            continue
        fig_rows.append(figure_row(short, src))
    figdf = pd.DataFrame(fig_rows)
    fig1(figdf)
    build_norman_comparison()
    build_divergence_profile(audit, raw)
    build_probe_comparison_table()
    fig2()
    stats_report(raw, audit)


if __name__ == "__main__":
    main()
