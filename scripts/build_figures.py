from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_all(fig, stem: Path):
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=600, bbox_inches="tight")


def leakage_ladder():
    fig, ax = plt.subplots(figsize=(6.5, 2.4))
    levels = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
    ax.plot(range(len(levels)), [0] * len(levels), color="#2b6cb0", lw=2)
    ax.scatter(range(len(levels)), [0] * len(levels), s=80, color="#2b6cb0")
    for i, label in enumerate(levels):
        ax.text(i, 0.04, label, ha="center", va="bottom", fontsize=9)
    ax.set_ylim(-0.2, 0.3)
    ax.set_axis_off()
    ax.set_title("Pilot leakage ladder framework; verified scores pending Norman acquisition", fontsize=10)
    save_all(fig, Path("figures/main/pilot_leakage_ladder"))
    plt.close(fig)


def blocked_metric_figure(stem: str, title: str):
    summary = Path("results/pilot/pilot_summary.csv")
    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    if summary.exists():
        df = pd.read_csv(summary)
        value_cols = [c for c in ["pearson_delta", "bns", "UER_at_50", "sign_flip_rate"] if c in df]
        numeric = df[value_cols].apply(pd.to_numeric, errors="coerce") if value_cols else pd.DataFrame()
        if not numeric.empty and numeric.notna().any().any():
            plot_col = "UER_at_50" if "hallucination" in stem else "pearson_delta"
            for model, sub in df.groupby("model"):
                sub = sub.copy()
                sub[plot_col] = pd.to_numeric(sub[plot_col], errors="coerce")
                ax.plot(sub["split"], sub[plot_col], marker="o", label=model)
            ax.set_ylabel(plot_col)
            ax.set_xlabel("Audit split")
            ax.legend(frameon=False, fontsize=7)
        else:
            ax.table(cellText=df[["dataset", "model", "split", "status"]].values,
                     colLabels=["dataset", "model", "split", "status"], loc="center")
            ax.axis("off")
    else:
        ax.text(0.5, 0.5, "BLOCKED: no verified Norman/GEARS pilot results yet", ha="center", va="center")
        ax.axis("off")
    ax.set_title(title, fontsize=10)
    save_all(fig, Path(f"figures/main/{stem}"))
    plt.close(fig)


def main():
    leakage_ladder()
    blocked_metric_figure("pilot_truthfulness", "Pilot truthfulness endpoints")
    blocked_metric_figure("pilot_hallucination", "Pilot hallucination endpoints")


if __name__ == "__main__":
    main()
