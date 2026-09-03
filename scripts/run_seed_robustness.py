from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.run_baseline_pilot import (
    SPLITTERS,
    additive_delta_map,
    context_matched_delta_map,
    pca_ridge_delta_map,
    summarize_delta_models,
    train_global_perturbed_mean_delta,
    train_mean_delta,
)
from src.data.loaders import normalize_norman_gears_schema, read_h5ad


def model_set(adata):
    mean_delta = train_mean_delta(adata)
    additive = additive_delta_map(adata, fallback=mean_delta)
    return [
        ("B0_no_change", np.zeros(adata.n_vars), "COMPLETED_SEED_ROBUSTNESS"),
        ("B1_global_perturbed_mean", train_global_perturbed_mean_delta(adata), "COMPLETED_SEED_ROBUSTNESS"),
        ("B2_context_matched_perturbed_mean", context_matched_delta_map(adata, fallback=mean_delta), "COMPLETED_SEED_ROBUSTNESS"),
        ("B3_additive_seen_component", additive, "COMPLETED_SEED_ROBUSTNESS"),
        ("B4_pca_ridge", pca_ridge_delta_map(adata, fallback=mean_delta), "COMPLETED_SEED_ROBUSTNESS"),
        ("B5_mean_effect", mean_delta, "COMPLETED_SEED_ROBUSTNESS"),
        (
            "FP1_perturbation_blind_mean_effect",
            mean_delta,
            "COMPLETED_SEED_ROBUSTNESS",
            "Perturbation-blind mean-effect shortcut probe",
        ),
        (
            "FP2_cell_state_blind_additive",
            additive,
            "COMPLETED_SEED_ROBUSTNESS",
            "Cell-state-blind additive perturbation identity probe",
        ),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5ad", default="data/raw/norman/perturb_processed.h5ad")
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    args = parser.parse_args()

    adata = normalize_norman_gears_schema(read_h5ad(Path(args.h5ad)))
    rows = []
    for seed in args.seeds:
        for split in ["L1", "L2", "L3"]:
            adata.obs["split_group"] = SPLITTERS[split](adata, seed=seed)
            split_rows, _ = summarize_delta_models(adata, split, model_set(adata))
            for row in split_rows:
                row["seed"] = seed
                rows.append(row)
    per_seed = pd.DataFrame(rows)
    Path("results/pilot").mkdir(parents=True, exist_ok=True)
    per_seed.to_csv("results/pilot/seed_robustness.csv", index=False)

    metric_cols = ["pearson_delta", "UER_at_50", "sign_flip_rate", "retrieval_mrr"]
    summary_rows = []
    for (model, split), sub in per_seed.groupby(["model", "split"]):
        out = {
            "dataset": "Norman2019_GEARS_processed_mirror",
            "model": model,
            "split": split,
            "n_seeds": int(sub["seed"].nunique()),
            "status": "COMPLETED_SEED_ROBUSTNESS",
        }
        for metric in metric_cols:
            vals = pd.to_numeric(sub[metric], errors="coerce").dropna()
            out[f"{metric}_mean"] = float(vals.mean()) if len(vals) else float("nan")
            out[f"{metric}_sd"] = float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")
            out[f"{metric}_min"] = float(vals.min()) if len(vals) else float("nan")
            out[f"{metric}_max"] = float(vals.max()) if len(vals) else float("nan")
        summary_rows.append(out)
    pd.DataFrame(summary_rows).to_csv("results/pilot/seed_robustness_summary.csv", index=False)


if __name__ == "__main__":
    main()
