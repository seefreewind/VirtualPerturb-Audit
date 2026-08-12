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
        ax.table(cellText=df.values, colLabels=df.columns, loc="center")
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

