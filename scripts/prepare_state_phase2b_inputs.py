#!/usr/bin/env python3
"""Prepare STATE-compatible Phase 2B inputs from frozen audit h5ad/split files."""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

TASKS = {
    "norman_l1": {
        "adata": ROOT / "data/raw/norman/perturb_processed.h5ad",
        "split": ROOT / "data/raw/norman/splits/virtualperturb_audit_L1_seed1.pkl",
        "cell_type": "A549",
    },
    "norman_l2": {
        "adata": ROOT / "data/raw/norman/perturb_processed.h5ad",
        "split": ROOT / "data/raw/norman/splits/virtualperturb_audit_L2_seed1.pkl",
        "cell_type": "A549",
    },
    "replogle_k562_rl1": {
        "adata": ROOT / "data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad",
        "split": ROOT
        / "data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L1-K562_seed1_rl1.pkl",
        "cell_type": "K562",
    },
    "replogle_k2r_rl4_source": {
        "adata": ROOT / "data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad",
        "split": ROOT
        / "data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L4-K2R_seed1_rl4.pkl",
        "cell_type": "K562",
    },
    "replogle_k2r_rl4_target": {
        "adata": ROOT / "data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad",
        "split": ROOT
        / "data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L4-K2R_seed1_rl4.pkl",
        "cell_type": "RPE1",
    },
}


def load_split(path: Path) -> dict[str, list[str]]:
    with path.open("rb") as handle:
        split = pickle.load(handle)
    return {k: [str(x) for x in v] for k, v in split.items()}


def condition_to_state_label(condition: str) -> str:
    condition = str(condition)
    if condition == "ctrl":
        return "ctrl"
    if condition.endswith("+ctrl"):
        return condition[: -len("+ctrl")]
    return condition


def prepare_task(task: str, mode: str, max_cells_per_condition: int, seed: int) -> tuple[Path, Path, dict]:
    cfg = TASKS[task]
    out_base = ROOT / "data/processed/state_phase2b" / mode / task
    out_base.mkdir(parents=True, exist_ok=True)
    h5ad_dir = out_base / "h5ad"
    h5ad_dir.mkdir(parents=True, exist_ok=True)
    toml_path = out_base / f"{task}.toml"
    h5ad_path = h5ad_dir / f"{task}.h5ad"

    split = load_split(cfg["split"])
    wanted_conditions = set(split["train"]) | set(split["val"]) | set(split["test"]) | {"ctrl"}
    if mode == "smoke":
        wanted_conditions = {"ctrl"}
        for key, limit in [("train", 4), ("val", 2), ("test", 2)]:
            wanted_conditions.update(split[key][:limit])

    adata = ad.read_h5ad(cfg["adata"])
    obs_condition = adata.obs["condition"].astype(str)
    mask = obs_condition.isin(wanted_conditions).to_numpy()
    if not mask.any():
        raise RuntimeError(f"No cells matched frozen conditions for {task}")

    subset = adata[mask].copy()
    subset.obs["condition"] = subset.obs["condition"].astype(str)
    subset.obs["gene"] = subset.obs["condition"].map(condition_to_state_label).astype(str)
    subset.obs["cell_type"] = cfg["cell_type"]
    subset.obs["gem_group"] = task
    subset.obs["state_task"] = task
    subset.obs["state_mode"] = mode

    if mode == "smoke" or max_cells_per_condition > 0:
        rng = np.random.default_rng(seed)
        keep_idx = []
        for condition, group in subset.obs.groupby("condition", observed=False):
            idx = group.index.to_numpy()
            if len(idx) > max_cells_per_condition:
                idx = rng.choice(idx, size=max_cells_per_condition, replace=False)
            keep_idx.extend(idx.tolist())
        subset = subset[keep_idx].copy()

    val_labels = [condition_to_state_label(x) for x in split["val"]]
    test_labels = [condition_to_state_label(x) for x in split["test"]]
    if mode == "smoke":
        val_labels = val_labels[:2]
        test_labels = test_labels[:2]

    dataset_name = task
    cell_type = cfg["cell_type"]
    toml = [
        "[datasets]",
        f'{dataset_name} = "{h5ad_dir}"',
        "",
        "[training]",
        f'{dataset_name} = "train"',
        "",
        "[zeroshot]",
        "",
        "[fewshot]",
        f'[fewshot."{dataset_name}.{cell_type}"]',
        f"val = {val_labels!r}",
        f"test = {test_labels!r}",
        "",
    ]
    toml_path.write_text("\n".join(toml), encoding="utf-8")
    subset.write_h5ad(h5ad_path)

    meta = {
        "task": task,
        "mode": mode,
        "h5ad": str(h5ad_path.relative_to(ROOT)),
        "toml": str(toml_path.relative_to(ROOT)),
        "n_cells": int(subset.n_obs),
        "n_genes": int(subset.n_vars),
        "n_conditions": int(subset.obs["condition"].nunique()),
        "n_train_conditions": len(split["train"]),
        "n_val_labels": len(val_labels),
        "n_test_labels": len(test_labels),
        "max_cells_per_condition": max_cells_per_condition,
    }
    return h5ad_path, toml_path, meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    parser.add_argument("--task", choices=sorted(TASKS), action="append")
    parser.add_argument("--max-cells-per-condition", type=int, default=20)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    tasks = args.task or (["norman_l1"] if args.mode == "smoke" else sorted(TASKS))
    rows = []
    for task in tasks:
        _, _, meta = prepare_task(task, args.mode, args.max_cells_per_condition, args.seed)
        rows.append(meta)

    out = ROOT / "results/tables/state_phase2b_input_manifest.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
