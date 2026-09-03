from __future__ import annotations

import argparse
import json
import pickle
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from scripts.audit_replogle_processed import standardized_obs
from scripts.run_gears_pilot import evaluate_gears_batches, json_safe
from scripts.run_gears_replogle_rl1 import (
    DATASETS,
    FROZEN_SPLIT_COUNTS,
    ObsLike,
    audit_control_count,
    audit_control_mean,
    compute_space_metrics,
    parse_training_log,
    rebuild_split_dict_gears_vocabulary,
    write_gears_custom_split,
)
from src.splits.builders import assign_replogle_l1_context_perturbation_holdout


def recover_export(dataset_key: str, run_dir: Path, bootstrap_resamples: int) -> None:
    cfg = DATASETS[dataset_key]
    dataset_dir = Path(cfg["source_h5ad"]).parent
    data_root = dataset_dir.parent
    gene_set_path = str(Path("data/raw") / "essential_all_data_pert_genes.pkl")
    metadata_path = run_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
    metadata["recovery_timestamp"] = datetime.now(timezone.utc).isoformat()
    metadata["recovery_reason"] = "recover post-training GEARS evaluation/export after ctrl_adata None failure"
    metadata["bootstrap_resamples"] = bootstrap_resamples
    started = time.perf_counter()

    import scanpy as sc
    from gears import GEARS, PertData

    adata = sc.read_h5ad(cfg["source_h5ad"])
    obs = standardized_obs(adata, cfg["dataset_label"], cfg["cell_line"])
    obs = obs.assign(condition=adata.obs["condition"].astype(str).to_numpy())
    labels = pd.Series(
        assign_replogle_l1_context_perturbation_holdout(ObsLike(obs), cfg["cell_line"], seed=metadata.get("seed", 1)),
        index=obs.index,
    )
    counts = {k: int((labels == k).sum()) for k in ["train", "val", "test"]}
    expected = FROZEN_SPLIT_COUNTS[cfg["split"]]
    if counts != expected:
        raise RuntimeError(f"Frozen split count mismatch during recovery: {counts} != {expected}")
    split_dir = dataset_dir / "splits"
    split_path = write_gears_custom_split(obs, cfg["cell_line"], split_dir, cfg["split"], metadata.get("seed", 1))
    raw_conditions = pickle.loads(split_path.read_bytes())
    del adata, obs, labels

    pert_data = PertData(str(data_root), gene_set_path=gene_set_path, default_pert_graph=False)
    pert_data.load(data_path=str(dataset_dir))
    split_path = rebuild_split_dict_gears_vocabulary(
        pert_data, split_path, cfg["split"], metadata.get("seed", 1), raw_conditions
    )
    pert_data.prepare_split(split="custom", seed=metadata.get("seed", 1), split_dict_path=str(split_path))
    pert_data.get_dataloader(
        batch_size=int(metadata.get("batch_size", 16)),
        test_batch_size=int(metadata.get("test_batch_size", 16)),
    )

    model = GEARS(pert_data, device=metadata.get("device", "cpu"), weight_bias_track=False)
    model.load_pretrained(str(run_dir / "model"))
    pred_mean, truth_mean = evaluate_gears_batches(model, int(metadata.get("max_eval_batches", 0)))
    metadata["eval_predicted_perturbations"] = int(len(pred_mean))
    metadata["eval_truth_perturbations"] = int(len(truth_mean))

    control = audit_control_mean(pert_data)
    metadata["n_ctrl_cells_audit"] = audit_control_count(pert_data)

    all_metric_rows = []
    all_retrieval_rows = []
    summaries = {}
    for space in ["gears_raw", "audit_delta"]:
        metric_rows, retrieval_rows, summary = compute_space_metrics(
            pred_mean,
            truth_mean,
            space,
            control if space == "audit_delta" else None,
            int(metadata.get("seed", 1)),
            bootstrap_resamples,
        )
        all_metric_rows.extend(metric_rows)
        all_retrieval_rows.extend(retrieval_rows)
        summaries[space] = summary
        metadata[f"n_test_targets_gears_vocabulary_{space}"] = summary["n_test_perturbations"]

    pd.DataFrame(all_metric_rows).to_csv(run_dir / "gears_metrics.csv", index=False)
    pd.DataFrame(
        [
            {k: v for k, v in r.items() if k != "space"}
            | {"space": r["space"], "UER_at_20": r["uer20"], "UER_at_50": r["uer50"], "UER_at_100": r["uer100"]}
            for r in all_metric_rows
        ]
    ).to_csv(run_dir / "hallucination_metrics.csv", index=False)
    pd.DataFrame(all_retrieval_rows).to_csv(run_dir / "gears_perturbation_retrieval.csv", index=False)

    centroids = {}
    for space in ["gears_raw", "audit_delta"]:
        shared = sorted(set(pred_mean) & set(truth_mean) - {"ctrl"})
        ctrl_mean = control if space == "audit_delta" else None
        ctrl_pred = pred_mean.get("ctrl")
        ctrl_truth = truth_mean.get("ctrl")
        p = {}
        t = {}
        for pert in shared:
            pred = np.asarray(pred_mean[pert]).ravel()
            truth = np.asarray(truth_mean[pert]).ravel()
            if space == "audit_delta":
                p[pert] = torch.as_tensor(pred - ctrl_mean)
                t[pert] = torch.as_tensor(truth - ctrl_mean)
            else:
                p[pert] = torch.as_tensor(pred - ctrl_pred) if ctrl_pred is not None else torch.as_tensor(pred)
                t[pert] = torch.as_tensor(truth - ctrl_truth) if ctrl_truth is not None else torch.as_tensor(truth)
        centroids[space] = {"perturbations": shared, "pred_delta": p, "truth_delta": t}
    torch.save(centroids, run_dir / "gears_delta_centroids.pt")

    pd.DataFrame([summaries["gears_raw"], summaries["audit_delta"]]).to_csv(run_dir / "gears_summary.csv", index=False)
    if (run_dir / "raw_train_telemetry.log").exists():
        parse_training_log(run_dir / "raw_train_telemetry.log", run_dir / "training_log.csv")
    metadata["summary"] = summaries
    metadata["status"] = "COMPLETED"
    metadata["run_status"] = "COMPLETED_GEARS"
    metadata["performance_eligible"] = True
    metadata["recovery_elapsed_seconds"] = round(time.perf_counter() - started, 3)
    metadata.pop("error", None)
    metadata.pop("error_type", None)
    metadata_path.write_text(json.dumps(json_safe(metadata), indent=2) + "\n")
    if (run_dir / "traceback.txt").exists():
        shutil.copy2(run_dir / "traceback.txt", run_dir / "traceback.failed_export.txt")
        (run_dir / "traceback.txt").unlink()
    (run_dir / "run.log").write_text(
        f"RUN: {cfg['dataset_label']} split {cfg['split']} status COMPLETED_GEARS "
        f"recovered_export_elapsed {metadata['recovery_elapsed_seconds']} s\n"
        "-- GEARS telemetry --\n"
        + (run_dir / "raw_train_telemetry.log").read_text(errors="ignore")
    )
    print(json.dumps(json_safe(summaries), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    args = parser.parse_args()
    recover_export(args.dataset, args.run_dir, args.bootstrap_resamples)


if __name__ == "__main__":
    main()
