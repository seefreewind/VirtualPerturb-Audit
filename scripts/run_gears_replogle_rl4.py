from __future__ import annotations

import argparse
import json
import os
import pickle
import shutil
import subprocess
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy import sparse

from scripts.audit_replogle_processed import standardized_obs
from scripts.run_gears_pilot import json_safe
from scripts.run_gears_replogle_rl1 import (
    ObsLike,
    build_trimmed_go_tensors,
    compute_space_metrics,
    parse_training_log,
    train_full,
)
from src.data.perturbations import normalize_condition


DATASETS = {
    "k2r": {
        "train_key": "k562",
        "test_key": "rpe1",
        "train_cell_line": "K562",
        "test_cell_line": "RPE1",
        "train_source_h5ad": "data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad",
        "test_target_h5ad": "data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad",
        "split": "R-L4-K2R",
        "split_hash": "1e5e924e3f4542b4",
        "config": "configs/replogle/gears_rl4_k2r_seed1.yaml",
    },
    "r2k": {
        "train_key": "rpe1",
        "test_key": "k562",
        "train_cell_line": "RPE1",
        "test_cell_line": "K562",
        "train_source_h5ad": "data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad",
        "test_target_h5ad": "data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad",
        "split": "R-L4-R2K",
        "split_hash": "c6c9c707a5710dc7",
        "config": "configs/replogle/gears_rl4_r2k_seed1.yaml",
    },
}


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return "UNKNOWN"


def sha16(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def mean_expr(x, mask: np.ndarray) -> np.ndarray:
    if int(np.asarray(mask).sum()) == 0:
        raise ValueError("Cannot compute mean expression for an empty mask")
    sub = x[mask]
    if sparse.issparse(sub):
        return np.asarray(sub.mean(axis=0)).ravel()
    return np.asarray(sub).mean(axis=0)


def condition_by_target(obs: pd.DataFrame) -> dict[str, str]:
    sub = obs[obs["control_status"].eq("perturbed")].copy()
    sub["target_norm"] = sub["perturbation"].astype(str).map(normalize_condition)
    out = {}
    for target, values in sub.groupby("target_norm")["condition"]:
        out[str(target)] = sorted(values.astype(str).unique())[0]
    return out


def write_source_split(
    obs: pd.DataFrame,
    eligible_targets: set[str],
    split_dir: Path,
    split_name: str,
    seed: int,
) -> tuple[Path, dict[str, list[str]]]:
    target2condition = condition_by_target(obs)
    train_conditions = [
        cond for target, cond in sorted(target2condition.items()) if target in eligible_targets
    ]
    if not train_conditions:
        raise ValueError(f"No eligible source conditions for {split_name}")
    rng = np.random.default_rng(seed)
    val_n = max(1, int(round(len(train_conditions) * 0.1)))
    val_conditions = sorted(rng.choice(train_conditions, size=val_n, replace=False).tolist())

    set2conditions = {
        "train": ["ctrl"] + train_conditions,
        "val": val_conditions,
        "test": val_conditions,
    }
    split_dir.mkdir(parents=True, exist_ok=True)
    path = split_dir / f"virtualperturb_audit_{split_name}_seed{seed}_rl4.pkl"
    with path.open("wb") as f:
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
    ).to_csv(path.with_suffix(".tsv"), sep="\t", index=False)
    return path, set2conditions


def restrict_split_to_gears_vocabulary(split_path: Path, pert_data, raw: dict[str, list[str]]) -> Path:
    valid = set(pert_data.adata.obs["condition"].astype(str))
    kept = {}
    for split in ["train", "val", "test"]:
        conditions = [c for c in raw[split] if c in valid]
        if split == "train" and "ctrl" not in conditions:
            conditions = ["ctrl"] + conditions
        if not conditions:
            raise ValueError(f"No GEARS-vocabulary conditions left for {split}")
        kept[split] = conditions
    with split_path.open("wb") as f:
        pickle.dump(kept, f)
    pd.DataFrame(
        [
            {
                "split": split,
                "n_conditions_raw": len(raw[split]),
                "n_conditions_gears_vocabulary": len(kept[split]),
                "conditions_preview": ";".join(kept[split][:8]),
            }
            for split in ["train", "val", "test"]
        ]
    ).to_csv(split_path.parent / (split_path.stem + "_gears_vocabulary.tsv"), sep="\t", index=False)
    return split_path


def target_truth_means(target_adata, target_obs: pd.DataFrame, targets: list[str]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ctrl_mask = target_obs["control_status"].eq("control").to_numpy()
    control = mean_expr(target_adata.X, ctrl_mask)
    means = {}
    perturbed = target_obs["control_status"].eq("perturbed").to_numpy()
    for target in targets:
        mask = perturbed & target_obs["perturbation"].astype(str).map(normalize_condition).eq(target).to_numpy()
        if int(mask.sum()) > 0:
            means[target] = mean_expr(target_adata.X, mask)
    return control, means


def predict_target_control_basal(model, target_adata, targets: list[str]) -> dict[str, np.ndarray]:
    model.adata = target_adata
    model.ctrl_adata = target_adata[target_adata.obs["condition"].astype(str).eq("ctrl")]
    model.saved_pred = {}
    pred = model.predict([[target] for target in targets])
    return {target: np.asarray(pred[target]).ravel() for target in targets if target in pred}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direction", choices=sorted(DATASETS), required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--test-batch-size", type=int, default=16)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--max-train-batches", type=int, default=0)
    parser.add_argument("--max-eval-perturbations", type=int, default=0)
    args = parser.parse_args()

    cfg = DATASETS[args.direction]
    source_dir = Path(cfg["train_source_h5ad"]).parent
    data_root = source_dir.parent
    gene_set_path = Path("data/raw/essential_all_data_pert_genes.pkl")
    gene2go_dst = data_root / "gene2go_all.pkl"
    if not gene2go_dst.exists():
        shutil.copy2(Path("data/raw/gene2go_all.pkl"), gene2go_dst)

    outdir = Path("results/replogle/gears") / datetime.now(timezone.utc).strftime(
        f"rl4_{args.direction}_%Y%m%dT%H%M%SZ"
    )
    outdir.mkdir(parents=True, exist_ok=True)
    config_path = Path(cfg["config"])
    shutil.copy2(config_path, outdir / "config.yaml")

    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "STARTED",
        "run_status": "STARTED",
        "dataset": "Replogle_GEARS_filtered",
        "filtered_data": True,
        "data_completeness_caveat": "GEARS-compatible filtered essential-screen data; NOT the complete Figshare+ processed objects",
        "direction": args.direction,
        "train_cell_line": cfg["train_cell_line"],
        "test_cell_line": cfg["test_cell_line"],
        "split": cfg["split"],
        "split_hash": cfg["split_hash"],
        "split_hash_source": "reports/replogle_split_integrity_report.md",
        "evaluation_adapter": "source_context_train_target_context_control_basal_prediction",
        "internal_validation": "source-context validation conditions are also present in train; target context is never used for training or model selection",
        "seed": args.seed,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "test_batch_size": args.test_batch_size,
        "device": args.device,
        "pert_graph": "essential",
        "gene_set_path": str(gene_set_path),
        "prior_hash": sha16(gene_set_path),
        "git_commit": git_commit(),
        "gears_version": "0.1.2",
        "performance_eligible": args.max_train_batches == 0 and args.max_eval_perturbations == 0,
        "bns_status": "UNVERIFIED",
        "bns_role": "sensitivity_only",
        "bootstrap_resamples": args.bootstrap_resamples,
        "bootstrap_unit": "perturbation",
        "gears_env": os.environ.get("VIRTUAL_ENV", "UNVERIFIED"),
        "max_train_batches": args.max_train_batches,
        "max_eval_perturbations": args.max_eval_perturbations,
        "hardware": "UNKNOWN",
    }
    try:
        import platform

        metadata["hardware"] = f"{platform.machine()} CPU"
        metadata["n_cpu_cores"] = os.cpu_count()
    except Exception:
        pass
    started = time.perf_counter()
    (outdir / "metadata.json").write_text(json.dumps(json_safe(metadata), indent=2) + "\n")

    try:
        import scanpy as sc
        from gears import GEARS, PertData

        source_adata = sc.read_h5ad(cfg["train_source_h5ad"])
        source_obs = standardized_obs(
            source_adata, f"Replogle_{cfg['train_cell_line']}_GEARS_filtered", cfg["train_cell_line"]
        )
        source_obs = source_obs.assign(condition=source_adata.obs["condition"].astype(str).to_numpy())
        target_adata = sc.read_h5ad(cfg["test_target_h5ad"])
        target_obs = standardized_obs(
            target_adata, f"Replogle_{cfg['test_cell_line']}_GEARS_filtered", cfg["test_cell_line"]
        )
        target_obs = target_obs.assign(condition=target_adata.obs["condition"].astype(str).to_numpy())
        overlap = pd.read_csv("results/tables/replogle_context_target_overlap.tsv", sep="\t")
        eligible = set(overlap.loc[overlap["cross_context_eligible"], "target"].astype(str).map(normalize_condition))
        split_path, raw_split = write_source_split(source_obs, eligible, source_dir / "splits", cfg["split"], args.seed)
        metadata["split_dict_path"] = str(split_path)
        metadata["n_source_cells"] = int(source_adata.n_obs)
        metadata["n_target_cells"] = int(target_adata.n_obs)
        metadata["n_cross_context_eligible_targets"] = int(len(eligible))
        del source_adata

        pert_data = PertData(str(data_root), gene_set_path=str(gene_set_path), default_pert_graph=False)
        pert_data.load(data_path=str(source_dir))
        metadata["dataset_name_gears"] = pert_data.dataset_name
        metadata["gears_vocabulary_cells"] = int(pert_data.adata.n_obs)
        split_path = restrict_split_to_gears_vocabulary(split_path, pert_data, raw_split)
        metadata["split_dict_path_gears_vocabulary"] = str(split_path)
        pert_data.prepare_split(split="custom", seed=args.seed, split_dict_path=str(split_path))
        pert_data.get_dataloader(batch_size=args.batch_size, test_batch_size=args.test_batch_size)

        model = GEARS(pert_data, device=args.device, weight_bias_track=False)
        go_edges_before, G_go, G_go_weight = build_trimmed_go_tensors(data_root, pert_data.dataset_name, pert_data)
        metadata["go_edges_before_trim"] = int(go_edges_before)
        metadata["go_edges_after_trim"] = int(G_go.shape[1])
        metadata["go_trim_k"] = 20
        metadata["filtered_go_nodes"] = int(len(pert_data.node_map_pert))
        model.model_initialize(G_go=G_go, G_go_weight=G_go_weight)

        if args.max_train_batches > 0:
            from scripts.run_gears_pilot import train_smoke_batches

            losses = train_smoke_batches(model, args.max_train_batches)
            metadata["train_batches_completed"] = len(losses)
            metadata["train_loss_first"] = losses[0] if losses else None
            metadata["run_status"] = "COMPLETED_GEARS_BATCH_SMOKE_NOT_PERFORMANCE"
        else:
            train_full(model, args.epochs, outdir / "raw_train_telemetry.log")
            metadata["run_status"] = "COMPLETED_GEARS"
        model.save_model(str(outdir / "model"))
        if (outdir / "raw_train_telemetry.log").exists():
            parse_training_log(outdir / "raw_train_telemetry.log", outdir / "training_log.csv")
        else:
            pd.DataFrame(columns=["epoch", "step", "event", "value"]).to_csv(
                outdir / "training_log.csv", index=False
            )

        source_valid = set(pert_data.adata.obs["condition"].astype(str).map(normalize_condition))
        target_valid = set(target_obs.loc[target_obs["control_status"].eq("perturbed"), "perturbation"].astype(str).map(normalize_condition))
        targets = sorted(t for t in eligible if t in source_valid and t in target_valid and t in model.pert_list)
        if args.max_eval_perturbations > 0:
            targets = targets[: args.max_eval_perturbations]
        if not targets:
            raise ValueError("No eligible target perturbations remain after GEARS vocabulary filtering")
        target_control, truth_mean = target_truth_means(target_adata, target_obs, targets)
        pred_mean = predict_target_control_basal(model, target_adata, targets)
        pred_mean["ctrl"] = target_control
        truth_mean["ctrl"] = target_control
        metadata["n_eval_targets_requested"] = int(len(targets))
        metadata["eval_predicted_perturbations"] = int(len(pred_mean) - 1)
        metadata["eval_truth_perturbations"] = int(len(truth_mean) - 1)
        metadata["n_ctrl_cells_target_audit"] = int(target_obs["control_status"].eq("control").sum())

        metric_rows, retrieval_rows, summary = compute_space_metrics(
            pred_mean,
            truth_mean,
            "audit_delta",
            target_control,
            args.seed,
            args.bootstrap_resamples,
        )
        for row in metric_rows:
            row.update(
                {
                    "direction": args.direction,
                    "train_cell_line": cfg["train_cell_line"],
                    "test_cell_line": cfg["test_cell_line"],
                    "split": cfg["split"],
                }
            )
        for row in retrieval_rows:
            row.update(
                {
                    "direction": args.direction,
                    "train_cell_line": cfg["train_cell_line"],
                    "test_cell_line": cfg["test_cell_line"],
                    "split": cfg["split"],
                }
            )
        summary.update(
            {
                "direction": args.direction,
                "train_cell_line": cfg["train_cell_line"],
                "test_cell_line": cfg["test_cell_line"],
                "split": cfg["split"],
                "metric_space": "target_control_audit_delta",
                "evaluation_adapter": metadata["evaluation_adapter"],
            }
        )
        pd.DataFrame(metric_rows).to_csv(outdir / "gears_metrics.csv", index=False)
        pd.DataFrame(retrieval_rows).to_csv(outdir / "gears_perturbation_retrieval.csv", index=False)
        pd.DataFrame([summary]).to_csv(outdir / "gears_summary.csv", index=False)
        torch.save(
            {
                "targets": targets,
                "pred_expression": {k: torch.as_tensor(v) for k, v in pred_mean.items() if k != "ctrl"},
                "truth_expression": {k: torch.as_tensor(v) for k, v in truth_mean.items() if k != "ctrl"},
                "target_control": torch.as_tensor(target_control),
            },
            outdir / "gears_delta_centroids.pt",
        )
        metadata["summary"] = summary
        metadata["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        metadata["status"] = "COMPLETED"
        telemetry = (
            (outdir / "raw_train_telemetry.log").read_text(errors="ignore")
            if (outdir / "raw_train_telemetry.log").exists()
            else ""
        )
        (outdir / "run.log").write_text(
            f"RUN: {cfg['split']} {cfg['train_cell_line']}->{cfg['test_cell_line']} "
            f"status {metadata['run_status']} elapsed {metadata['elapsed_seconds']} s\n"
            "-- GEARS telemetry (stderr redirected during official train) --\n"
            + telemetry
        )
        (outdir / "metadata.json").write_text(json.dumps(json_safe(metadata), indent=2) + "\n")
        print(json.dumps(json_safe(summary), indent=2))
    except Exception as exc:
        metadata["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        metadata["status"] = "FAILED"
        metadata["run_status"] = "FAILED_GEARS"
        metadata["error_type"] = type(exc).__name__
        metadata["error"] = str(exc)
        (outdir / "metadata.json").write_text(json.dumps(json_safe(metadata), indent=2) + "\n")
        (outdir / "traceback.txt").write_text(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
