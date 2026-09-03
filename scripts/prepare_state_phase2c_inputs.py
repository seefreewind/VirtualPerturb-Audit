#!/usr/bin/env python3
"""Prepare locked Phase 2C STATE inputs from frozen GEARS audit splits."""

from __future__ import annotations

import argparse
import json
import pickle
from dataclasses import dataclass
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    adata: Path
    split: Path
    cell_type: str
    split_label: str


DATASETS = {
    "norman_l1": DatasetSpec(
        name="norman_l1",
        adata=ROOT / "data/raw/norman/perturb_processed.h5ad",
        split=ROOT / "data/raw/norman/splits/virtualperturb_audit_L1_seed1.pkl",
        cell_type="A549",
        split_label="L1_seed1",
    ),
    "norman_l2": DatasetSpec(
        name="norman_l2",
        adata=ROOT / "data/raw/norman/perturb_processed.h5ad",
        split=ROOT / "data/raw/norman/splits/virtualperturb_audit_L2_seed1.pkl",
        cell_type="A549",
        split_label="L2_seed1",
    ),
    "replogle_k562_rl1": DatasetSpec(
        name="replogle_k562_rl1",
        adata=ROOT / "data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad",
        split=ROOT
        / "data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L1-K562_seed1_rl1.pkl",
        cell_type="K562",
        split_label="R-L1-K562_seed1",
    ),
    "replogle_k562_rl4_source": DatasetSpec(
        name="replogle_k562_rl4_source",
        adata=ROOT / "data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad",
        split=ROOT
        / "data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L4-K2R_seed1_rl4.pkl",
        cell_type="K562",
        split_label="R-L4-K2R_seed1_source",
    ),
    "replogle_rpe1_rl4_target": DatasetSpec(
        name="replogle_rpe1_rl4_target",
        adata=ROOT / "data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad",
        split=ROOT
        / "data/raw/replogle/replogle_k562_essential/splits/virtualperturb_audit_R-L4-K2R_seed1_rl4.pkl",
        cell_type="RPE1",
        split_label="R-L4-K2R_seed1_target",
    ),
}


RUNS = {
    "S1_norman_l1": {
        "train_dataset": "norman_l1",
        "predict_dataset": "norman_l1",
        "description": "Norman L1 within-context STATE audit",
    },
    "S2_norman_l2": {
        "train_dataset": "norman_l2",
        "predict_dataset": "norman_l2",
        "description": "Norman L2 within-context STATE audit",
    },
    "S3_replogle_k562_rl1": {
        "train_dataset": "replogle_k562_rl1",
        "predict_dataset": "replogle_k562_rl1",
        "description": "Replogle K562 R-L1 within-context STATE audit",
    },
    "S4_replogle_k562_to_rpe1_rl4": {
        "train_dataset": "replogle_k562_rl4_source",
        "predict_dataset": "replogle_rpe1_rl4_target",
        "description": "Replogle K562-to-RPE1 R-L4 cross-context STATE audit",
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


def read_conditions(spec: DatasetSpec) -> pd.Series:
    obs = ad.read_h5ad(spec.adata, backed="r").obs
    return obs["condition"].astype(str)


def write_toml(path: Path, dataset_name: str, h5ad_dir: Path, cell_type: str, val: list[str], test: list[str]) -> None:
    h5ad_dir_abs = h5ad_dir.resolve()
    lines = [
        "[datasets]",
        f'{dataset_name} = "{h5ad_dir_abs}"',
        "",
        "[training]",
        f'{dataset_name} = "train"',
        "",
        "[zeroshot]",
        "",
        "[fewshot]",
        f'[fewshot."{dataset_name}.{cell_type}"]',
        f"val = {val!r}",
        f"test = {test!r}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def prepare_dataset(spec: DatasetSpec, mode: str, max_cells_per_condition: int, seed: int) -> dict:
    split = load_split(spec.split)
    wanted = set(split["train"]) | set(split["val"]) | set(split["test"]) | {"ctrl"}
    if mode == "smoke":
        wanted = {"ctrl"}
        wanted.update(split["train"][:4])
        wanted.update(split["val"][:2])
        wanted.update(split["test"][:2])

    out_base = ROOT / "data/processed/state_phase2c" / mode / spec.name
    h5ad_dir = out_base / "h5ad"
    h5ad_dir.mkdir(parents=True, exist_ok=True)
    h5ad_path = h5ad_dir / f"{spec.name}.h5ad"
    toml_path = out_base / f"{spec.name}.toml"

    adata = ad.read_h5ad(spec.adata)
    conditions = adata.obs["condition"].astype(str)
    subset = adata[conditions.isin(wanted).to_numpy()].copy()
    if subset.n_obs == 0:
        raise RuntimeError(f"No cells matched frozen split conditions for {spec.name}")

    subset.obs["condition"] = subset.obs["condition"].astype(str)
    subset.obs["gene"] = subset.obs["condition"].map(condition_to_state_label).astype(str)
    subset.obs["cell_type"] = spec.cell_type
    subset.obs["gem_group"] = spec.name
    subset.obs["state_task"] = spec.name
    subset.obs["state_mode"] = mode

    if mode == "smoke" or max_cells_per_condition > 0:
        rng = np.random.default_rng(seed)
        keep_idx = []
        for _, group in subset.obs.groupby("condition", observed=False):
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

    subset.write_h5ad(h5ad_path)
    write_toml(toml_path, spec.name, h5ad_dir, spec.cell_type, val_labels, test_labels)

    return {
        "dataset": spec.name,
        "split": spec.split_label,
        "mode": mode,
        "h5ad": str(h5ad_path.relative_to(ROOT)),
        "toml": str(toml_path.relative_to(ROOT)),
        "n_cells": int(subset.n_obs),
        "n_genes": int(subset.n_vars),
        "n_conditions": int(subset.obs["condition"].nunique()),
        "n_train_conditions": len(split["train"]),
        "n_val_conditions": len(split["val"]),
        "n_test_conditions": len(split["test"]),
        "max_cells_per_condition": int(max_cells_per_condition),
    }


def write_run_manifest(dataset_rows: list[dict], mode: str) -> pd.DataFrame:
    by_dataset = {row["dataset"]: row for row in dataset_rows}
    rows = []
    for run_id, cfg in RUNS.items():
        train = by_dataset[cfg["train_dataset"]]
        pred = by_dataset[cfg["predict_dataset"]]
        rows.append(
            {
                "run_id": run_id,
                "mode": mode,
                "description": cfg["description"],
                "train_dataset": cfg["train_dataset"],
                "predict_dataset": cfg["predict_dataset"],
                "train_toml": train["toml"],
                "predict_toml": pred["toml"],
                "train_h5ad": train["h5ad"],
                "predict_h5ad": pred["h5ad"],
            }
        )
    df = pd.DataFrame(rows)
    out = ROOT / "results/tables/state_phase2c_run_manifest.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return df


def write_alignment(mode: str) -> pd.DataFrame:
    rows = []
    for key, spec in DATASETS.items():
        split = load_split(spec.split)
        available = set(read_conditions(spec))
        state_train = set(split["train"])
        state_test = set(split["test"])
        for target in sorted(set(split["train"]) | set(split["test"])):
            in_gears_train = target in split["train"]
            in_gears_test = target in split["test"]
            in_state_train = target in state_train and target in available
            in_state_test = target in state_test and target in available
            if (in_gears_train == in_state_train) and (in_gears_test == in_state_test):
                status = "ALIGNED"
                reason = ""
            elif target not in available:
                status = "MISSING_FROM_STATE_H5AD_SOURCE"
                reason = "target condition absent from source AnnData"
            else:
                status = "SPLIT_ROLE_MISMATCH"
                reason = "GEARS and STATE split membership differ"
            rows.append(
                {
                    "dataset": key,
                    "split": spec.split_label,
                    "target": condition_to_state_label(target),
                    "gears_condition": target,
                    "in_gears_train": in_gears_train,
                    "in_gears_test": in_gears_test,
                    "in_state_train": in_state_train,
                    "in_state_test": in_state_test,
                    "alignment_status": status,
                    "reason_if_not_aligned": reason,
                }
            )
    df = pd.DataFrame(rows)
    out = ROOT / "results/tables/state_gears_split_alignment.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, sep="\t", index=False)

    summary = (
        df.groupby(["dataset", "split", "alignment_status"], dropna=False)
        .size()
        .reset_index(name="n_targets")
        .sort_values(["dataset", "alignment_status"])
    )
    total = len(df)
    bad = int((df["alignment_status"] != "ALIGNED").sum())
    warn = bad / total > 0.10 if total else False
    report = ROOT / "reports/STATE_SPLIT_ALIGNMENT_AUDIT.md"
    report.write_text(
        "# STATE-GEARS Split Alignment Audit\n\n"
        f"- mode_prepared: {mode}\n"
        f"- total_rows: {total}\n"
        f"- non_aligned_rows: {bad}\n"
        f"- exclusion_warning_gt_10pct: {str(warn).lower()}\n\n"
        "## Summary\n\n"
        + summary.to_markdown(index=False)
        + "\n\nAll rows are derived from frozen GEARS split pickle files and source AnnData condition labels.\n",
        encoding="utf-8",
    )
    return df


def write_gene_universe() -> pd.DataFrame:
    rows = []
    genes_by_dataset = {}
    for key, spec in DATASETS.items():
        adata = ad.read_h5ad(spec.adata, backed="r")
        genes = pd.Index(adata.var_names.astype(str))
        genes_by_dataset[key] = set(genes)
        rows.append({"dataset": key, "n_genes": len(genes), "first_gene": genes[0], "last_gene": genes[-1]})
    common = set.intersection(*genes_by_dataset.values())
    union = set.union(*genes_by_dataset.values())
    rows.append({"dataset": "COMMON_ALL_PHASE2C", "n_genes": len(common), "first_gene": "", "last_gene": ""})
    rows.append({"dataset": "UNION_ALL_PHASE2C", "n_genes": len(union), "first_gene": "", "last_gene": ""})
    df = pd.DataFrame(rows)
    out = ROOT / "results/tables/state_gears_gene_universe.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, sep="\t", index=False)
    return df


def write_reports(dataset_df: pd.DataFrame, run_df: pd.DataFrame, alignment_df: pd.DataFrame, gene_df: pd.DataFrame) -> None:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "STATE_ADAPTER_AUDIT.md").write_text(
        "# STATE Adapter Audit\n\n"
        "The Phase 2C adapter maps frozen GEARS perturbation conditions into STATE-compatible AnnData/TOML inputs without changing split membership.\n\n"
        "- control label: `ctrl`\n"
        "- perturbation label mapping: trailing `+ctrl` is removed for STATE `gene`; raw GEARS condition is retained in `obs.condition`.\n"
        "- cell type fields: Norman `A549`, Replogle `K562` or `RPE1`.\n"
        "- batch/context field: `gem_group`, set to the locked Phase 2C dataset key.\n"
        "- split source: frozen GEARS pickle files only.\n"
        "- BNS status: UNVERIFIED; not used as a primary endpoint.\n\n"
        "## Prepared Datasets\n\n"
        + dataset_df.to_markdown(index=False)
        + "\n\n## Run Manifest\n\n"
        + run_df.to_markdown(index=False)
        + "\n",
        encoding="utf-8",
    )
    (reports / "STATE_CONFIG_DEVIATIONS.md").write_text(
        "# STATE Configuration Deviations\n\n"
        "Allowed compute-only adaptations are recorded here before model runs.\n\n"
        "| item | value | rationale | performance_eligibility |\n"
        "|---|---:|---|---|\n"
        "| training.train_seed | 1 | Locked Phase 2C seed | eligible |\n"
        "| training.devices | 1 | Single RTX 4090 server | eligible |\n"
        "| training.batch_size | benchmarked per run | Fit within 24 GB VRAM | eligible if unchanged after benchmark |\n"
        "| training.gradient_accumulation_steps | benchmarked per run | Preserve effective batch when needed | eligible |\n"
        "| data.kwargs.num_workers | 4 | Avoid oversubscribing shared server CPU during I/O | eligible |\n"
        "| precision / mixed precision | STATE default unless benchmark requires change | Compute adaptation only | eligible if recorded |\n"
        "| smoke max_steps | 1-5 | Load/train/predict verification only | not performance-eligible |\n\n"
        "No test-guided tuning is permitted. Any full-run hyperparameter adjustment must be justified by memory/runtime diagnostics rather than metric feedback.\n",
        encoding="utf-8",
    )
    (reports / "STATE_INPUT_PREP_SUMMARY.md").write_text(
        "# STATE Phase 2C Input Preparation Summary\n\n"
        "## Dataset Manifest\n\n"
        + dataset_df.to_markdown(index=False)
        + "\n\n## Alignment Snapshot\n\n"
        + alignment_df["alignment_status"].value_counts().rename_axis("status").reset_index(name="n").to_markdown(index=False)
        + "\n\n## Gene Universe Snapshot\n\n"
        + gene_df.to_markdown(index=False)
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    parser.add_argument("--dataset", choices=sorted(DATASETS), action="append")
    parser.add_argument("--max-cells-per-condition", type=int, default=20)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    selected = args.dataset or sorted(DATASETS)
    rows = [prepare_dataset(DATASETS[key], args.mode, args.max_cells_per_condition, args.seed) for key in selected]
    dataset_df = pd.DataFrame(rows)
    out = ROOT / "results/tables/state_phase2c_dataset_manifest.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    dataset_df.to_csv(out, index=False)

    run_df = write_run_manifest(rows, args.mode) if set(selected) == set(DATASETS) else pd.DataFrame()
    alignment_df = write_alignment(args.mode)
    gene_df = write_gene_universe()
    if not run_df.empty:
        write_reports(dataset_df, run_df, alignment_df, gene_df)

    print(json.dumps({"dataset_manifest": str(out.relative_to(ROOT)), "n_datasets": len(rows)}, indent=2))
    print(dataset_df.to_string(index=False))


if __name__ == "__main__":
    main()
