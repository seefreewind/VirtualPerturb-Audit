from __future__ import annotations

import argparse
import json
import os
import pickle
import shutil
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.audit_replogle_processed import standardized_obs
from scripts.run_gears_pilot import (
    build_filtered_go_tensors,
    evaluate_gears_batches,
    json_safe,
    train_smoke_batches,
)
from src.splits.builders import assign_replogle_l1_context_perturbation_holdout


DATASETS = {
    "k562": {
        "cell_line": "K562",
        "source_h5ad": "data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad",
        "dataset_label": "Replogle_K562_GEARS_filtered",
        "split": "R-L1-K562",
    },
    "rpe1": {
        "cell_line": "RPE1",
        "source_h5ad": "data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad",
        "dataset_label": "Replogle_RPE1_GEARS_filtered",
        "split": "R-L1-RPE1",
    },
}


def prepare_smoke_dataset(
    source_h5ad: Path,
    outdir: Path,
    dataset_label: str,
    cell_line: str,
    seed: int,
    max_train_conditions: int,
    max_val_conditions: int,
    max_test_conditions: int,
    max_cells_per_condition: int,
) -> Path:
    import scanpy as sc

    split_path = outdir / "splits" / f"virtualperturb_audit_{DATASETS[cell_line.lower()]['split']}_seed{seed}_smoke.pkl"
    if (outdir / "perturb_processed.h5ad").exists() and split_path.exists():
        return split_path

    adata = sc.read_h5ad(source_h5ad)
    obs = standardized_obs(adata, dataset_label, cell_line)
    labels = pd.Series(
        assign_replogle_l1_context_perturbation_holdout(ObsLike(obs), cell_line, seed=seed),
        index=obs.index,
    )
    working = adata.copy()
    working.obs["vp_split_group"] = labels.reindex(obs.index).to_numpy()
    rng = np.random.default_rng(seed)
    selected_idx = []
    set2conditions = {}
    for split, max_conditions in [
        ("train", max_train_conditions),
        ("val", max_val_conditions),
        ("test", max_test_conditions),
    ]:
        conditions = sorted(working.obs.loc[working.obs["vp_split_group"].eq(split), "condition"].astype(str).unique())
        if split == "train":
            conditions = ["ctrl"] + [condition for condition in conditions if condition != "ctrl"]
        conditions = conditions[:max_conditions]
        set2conditions[split] = conditions
        for condition in conditions:
            idx = np.flatnonzero(working.obs["condition"].astype(str).to_numpy() == condition)
            if len(idx) > max_cells_per_condition:
                idx = rng.choice(idx, size=max_cells_per_condition, replace=False)
            selected_idx.extend(idx.tolist())
    subset = working[np.array(sorted(set(selected_idx))), :].copy()
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    subset.write_h5ad(outdir / "perturb_processed.h5ad")
    split_dir = outdir / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    with split_path.open("wb") as f:
        pickle.dump(set2conditions, f)
    pd.DataFrame(
        [
            {
                "split": split,
                "n_conditions": len(conditions),
                "conditions_preview": ";".join(conditions[:8]),
            }
            for split, conditions in set2conditions.items()
        ]
    ).to_csv(split_dir / (split_path.stem + ".tsv"), sep="\t", index=False)
    return split_path


def summarize_smoke(pred_mean: dict, truth_mean: dict, metadata: dict, outdir: Path) -> None:
    shared = sorted(set(pred_mean) & set(truth_mean) - {"ctrl"})
    rows = []
    for pert in shared:
        rows.append(
            {
                "perturbation": pert,
                "n_pred_cells_or_batches": len(pred_mean[pert]) if hasattr(pred_mean[pert], "__len__") else "NA",
                "status": "SMOKE_EVALUATED_NOT_PERFORMANCE",
            }
        )
    pd.DataFrame(rows).to_csv(outdir / "gears_smoke_evaluated_perturbations.csv", index=False)
    metadata["n_evaluated_noncontrol_perturbations"] = len(shared)


def rebuild_split_dict_gears_vocabulary(pert_data, split_path: Path, cell_line: str, seed: int) -> Path:
    """Rebuild the custom split dict from GEARS-filtered conditions.

    PertData.load drops cells whose condition is not representable in the
    perturbation graph (filter_pert_in_go). The raw-obs split dict may contain
    such conditions, which would raise KeyError inside get_dataloader. Rebuild
    the dict from pert_data.adata.obs so every split condition exists in the
    GEARS vocabulary. This mirrors the Norman custom-split convention of
    writing splits inside the GEARS-run vocabulary.
    """
    obs = pert_data.adata.obs
    set2conditions = {}
    for split in ["train", "val", "test"]:
        conditions = sorted(obs.loc[obs["vp_split_group"].eq(split), "condition"].astype(str).unique())
        if split == "train" and "ctrl" not in conditions:
            if "ctrl" not in set(obs["condition"].astype(str)):
                raise ValueError("ctrl condition missing from GEARS-filtered obs")
            conditions = ["ctrl"] + conditions
        if not conditions:
            raise ValueError(f"no GEARS-vocabulary conditions remain for {split} after GO filtering")
        set2conditions[split] = conditions
    with split_path.open("wb") as f:
        pickle.dump(set2conditions, f)
    pd.DataFrame(
        [
            {
                "split": split,
                "n_conditions_gears_vocabulary": len(conditions),
                "conditions_preview": ";".join(conditions[:8]),
            }
            for split, conditions in set2conditions.items()
        ]
    ).to_csv(split_path.parent / (split_path.stem + "_gears_vocabulary.tsv"), sep="\t", index=False)
    return split_path


class ObsLike:
    def __init__(self, obs: pd.DataFrame):
        self.obs = obs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=sorted(DATASETS), default="k562")
    parser.add_argument("--data-root", default="data/raw")
    parser.add_argument("--smoke-root", default="data/processed")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--test-batch-size", type=int, default=8)
    parser.add_argument("--max-train-batches", type=int, default=1)
    parser.add_argument("--max-eval-batches", type=int, default=1)
    parser.add_argument("--max-train-conditions", type=int, default=48)
    parser.add_argument("--max-val-conditions", type=int, default=8)
    parser.add_argument("--max-test-conditions", type=int, default=8)
    parser.add_argument("--max-cells-per-condition", type=int, default=6)
    args = parser.parse_args()

    cfg = DATASETS[args.dataset]
    smoke_dataset_dir = Path(args.smoke_root) / f"replogle_{args.dataset}_gears_smoke"
    outdir = Path("results/replogle/gears") / datetime.now(timezone.utc).strftime(
        f"gears_replogle_{args.dataset}_smoke_%Y%m%dT%H%M%SZ"
    )
    outdir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "STARTED",
        "dataset": cfg["dataset_label"],
        "source_h5ad": cfg["source_h5ad"],
        "smoke_dataset_dir": str(smoke_dataset_dir),
        "split": cfg["split"],
        "scope": "bounded_smoke_not_performance",
        "bns_status": "UNVERIFIED",
        "device": args.device,
        "seed": args.seed,
        "batch_size": args.batch_size,
        "test_batch_size": args.test_batch_size,
        "max_train_batches": args.max_train_batches,
        "max_eval_batches": args.max_eval_batches,
        "gears_env": os.environ.get("VIRTUAL_ENV", "UNVERIFIED"),
    }
    started = time.perf_counter()
    try:
        split_path = prepare_smoke_dataset(
            Path(cfg["source_h5ad"]),
            smoke_dataset_dir,
            cfg["dataset_label"],
            cfg["cell_line"],
            args.seed,
            args.max_train_conditions,
            args.max_val_conditions,
            args.max_test_conditions,
            args.max_cells_per_condition,
        )
        metadata["split_dict_path"] = str(split_path)
        from gears import GEARS, PertData

        pert_data = PertData(
            args.data_root,
            gene_set_path=str(Path(args.data_root) / "essential_all_data_pert_genes.pkl"),
            default_pert_graph=False,
        )
        pert_data.load(data_path=str(smoke_dataset_dir))
        split_path = rebuild_split_dict_gears_vocabulary(
            pert_data,
            split_path,
            cfg["cell_line"],
            args.seed,
        )
        pert_data.prepare_split(split="custom", seed=args.seed, split_dict_path=str(split_path))
        pert_data.get_dataloader(batch_size=args.batch_size, test_batch_size=args.test_batch_size)
        model = GEARS(pert_data, device=args.device, weight_bias_track=False)
        G_go, G_go_weight = build_filtered_go_tensors(Path(args.data_root), pert_data.dataset_name, pert_data)
        metadata["filtered_go_edges"] = int(G_go.shape[1])
        metadata["filtered_go_nodes"] = int(len(pert_data.node_map_pert))
        (Path(args.data_root) / pert_data.dataset_name).mkdir(parents=True, exist_ok=True)
        model.model_initialize(G_go=G_go, G_go_weight=G_go_weight)
        losses = train_smoke_batches(model, args.max_train_batches)
        metadata["train_batches_completed"] = len(losses)
        metadata["train_loss_first"] = losses[0] if losses else None
        metadata["train_loss_last"] = losses[-1] if losses else None
        model.save_model(str(outdir / "model"))
        pred_mean, truth_mean = evaluate_gears_batches(model, args.max_eval_batches)
        summarize_smoke(pred_mean, truth_mean, metadata, outdir)
        metadata["status"] = "COMPLETED_GEARS_REPLOGLE_BATCH_SMOKE_NOT_PERFORMANCE"
        metadata["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        (outdir / "metadata.json").write_text(json.dumps(json_safe(metadata), indent=2) + "\n")
    except Exception as exc:
        metadata["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        metadata["status"] = "FAILED_GEARS_REPLOGLE_SMOKE"
        metadata["error_type"] = type(exc).__name__
        metadata["error"] = str(exc)
        (outdir / "metadata.json").write_text(json.dumps(json_safe(metadata), indent=2) + "\n")
        (outdir / "traceback.txt").write_text(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
