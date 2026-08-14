from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.run_baseline_pilot import SPLITTERS, additive_delta_map, summarize_delta_models, train_mean_delta, train_perturbation_deltas
from src.data.loaders import normalize_norman_gears_schema, read_h5ad


def shuffled_delta_map(adata, seed: int) -> dict[str, np.ndarray]:
    import numpy as np

    rng = np.random.default_rng(seed)
    obs = adata.obs
    control_mask = obs["control_status"].astype(str).eq("control")
    test_perts = sorted(obs.loc[(obs["split_group"] == "test") & ~control_mask, "perturbation"].astype(str).unique())
    train_deltas = train_perturbation_deltas(adata)
    train_perts = sorted(train_deltas)
    if not train_perts:
        return {pert: np.zeros(adata.n_vars) for pert in test_perts}
    assigned = rng.choice(train_perts, size=len(test_perts), replace=True)
    return {test_pert: train_deltas[train_pert] for test_pert, train_pert in zip(test_perts, assigned)}


def evaluate_falsification_split(adata, split: str, seed: int):
    blind_delta = train_mean_delta(adata)
    cell_state_blind_delta = additive_delta_map(adata, fallback=blind_delta)
    shuffled_delta = shuffled_delta_map(adata, seed=seed)
    return summarize_delta_models(
        adata,
        split,
        [
            (
                "FP1_perturbation_blind_mean_effect",
                blind_delta,
                "COMPLETED_FALSIFICATION_PROBE",
                "Perturbation-blind mean-effect shortcut probe; intentionally identical to B5 under one-context Norman pilot",
            ),
            (
                "FP2_cell_state_blind_additive",
                cell_state_blind_delta,
                "COMPLETED_FALSIFICATION_PROBE",
                "Cell-state-blind additive perturbation identity probe; uses training-set single-component deltas when seen, otherwise mean-effect fallback",
            ),
            (
                "FP3_label_shuffled_mean_effect",
                shuffled_delta,
                "COMPLETED_FALSIFICATION_PROBE",
                "Label-shuffled perturbation delta probe; assigns random training perturbation deltas to held-out test perturbations",
            ),
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5ad", default="data/raw/norman/perturb_processed.h5ad")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    h5ad = Path(args.h5ad)
    if not h5ad.exists():
        raise FileNotFoundError(f"Norman file not found: {h5ad}")
    adata = normalize_norman_gears_schema(read_h5ad(h5ad))
    rows = []
    retrieval_rows = []
    for split in ["L1", "L2"]:
        adata.obs["split_group"] = SPLITTERS[split](adata, seed=args.seed)
        split_rows, split_retrieval = evaluate_falsification_split(adata, split, seed=args.seed)
        rows.extend(split_rows)
        retrieval_rows.extend(split_retrieval)
    out = Path("results/pilot/pilot_summary.csv")
    falsification = pd.DataFrame(rows)
    if out.exists():
        existing = pd.read_csv(out)
        existing = existing[
            ~existing["model"].astype(str).isin(
                ["FP1_perturbation_blind_mean_effect", "FP2_cell_state_blind_additive", "FP3_label_shuffled_mean_effect"]
            )
        ]
        falsification = pd.concat([existing, falsification], ignore_index=True)
    falsification.to_csv(out, index=False)
    retrieval_out = Path("results/pilot/perturbation_retrieval.csv")
    retrieval = pd.DataFrame(retrieval_rows)
    if retrieval_out.exists():
        existing_retrieval = pd.read_csv(retrieval_out)
        existing_retrieval = existing_retrieval[
            ~existing_retrieval["model"].astype(str).isin(
                ["FP1_perturbation_blind_mean_effect", "FP2_cell_state_blind_additive", "FP3_label_shuffled_mean_effect"]
            )
        ]
        retrieval = pd.concat([existing_retrieval, retrieval], ignore_index=True)
    retrieval.to_csv(retrieval_out, index=False)


if __name__ == "__main__":
    main()
