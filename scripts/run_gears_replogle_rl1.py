from __future__ import annotations

import argparse
import json
import math
import os
import pickle
import shutil
import subprocess
import sys
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from scripts.audit_replogle_processed import standardized_obs
from scripts.run_gears_pilot import (
    build_filtered_go_tensors,
    evaluate_gears_batches,
    json_safe,
)
from src.hallucination.metrics import sign_flip_rate, unsupported_effect_rate_at_k
from src.metrics.expression import expression_metrics
from src.metrics.retrieval import perturbation_centroid_retrieval, perturbation_retrieval_rows
from src.splits.builders import assign_replogle_l1_context_perturbation_holdout
from src.statistics.bootstrap import bootstrap_mean_ci


DATASETS = {
    "k562": {
        "cell_line": "K562",
        "source_h5ad": "data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad",
        "dataset_label": "Replogle_K562_GEARS_filtered",
        "split": "R-L1-K562",
        "split_hash": "e9fcaf7afdb972e4",
        "config": "configs/replogle/gears_rl1_k562_seed1.yaml",
    },
    "rpe1": {
        "cell_line": "RPE1",
        "source_h5ad": "data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad",
        "dataset_label": "Replogle_RPE1_GEARS_filtered",
        "split": "R-L1-RPE1",
        "split_hash": "288d45dbeb512ce5",
        "config": "configs/replogle/gears_rl1_rpe1_seed1.yaml",
    },
}

FROZEN_SPLIT_COUNTS = {
    "R-L1-K562": {"train": 115216, "val": 15716, "test": 31819},
    "R-L1-RPE1": {"train": 122724, "val": 13185, "test": 26824},
}


class ObsLike:
    def __init__(self, obs: pd.DataFrame):
        self.obs = obs


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


def write_gears_custom_split(obs: pd.DataFrame, cell_line: str, outdir: Path, split_name: str, seed: int) -> Path:
    labels = pd.Series(
        assign_replogle_l1_context_perturbation_holdout(ObsLike(obs), cell_line, seed=seed),
        index=obs.index,
    )
    counts = {k: int((labels == k).sum()) for k in ["train", "val", "test"]}
    expected = FROZEN_SPLIT_COUNTS[split_name]
    if counts != expected:
        raise RuntimeError(
            f"Frozen split count mismatch for {split_name}: got {counts}, expected {expected}"
        )
    obs = obs.assign(vp_split_group=labels.to_numpy())
    set2conditions = {}
    for split in ["train", "val", "test"]:
        conditions = sorted(obs.loc[obs["vp_split_group"].eq(split), "condition"].astype(str).unique())
        if split == "train" and "ctrl" not in conditions:
            conditions = ["ctrl"] + conditions
        set2conditions[split] = conditions
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"virtualperturb_audit_{split_name}_seed{seed}_rl1.pkl"
    with path.open("wb") as f:
        pickle.dump(set2conditions, f)
    pd.DataFrame(
        [
            {
                "split": s,
                "n_conditions_raw_obs": len(c),
                "conditions_preview": ";".join(c[:8]),
            }
            for s, c in set2conditions.items()
        ]
    ).to_csv(outdir / f"virtualperturb_audit_{split_name}_seed{seed}_rl1.tsv", sep="\t", index=False)
    return path


def rebuild_split_dict_gears_vocabulary(
    pert_data, split_path: Path, split_name: str, seed: int, raw_conditions: dict[str, list[str]]
) -> Path:
    """Restrict the raw-obs split dict to the GEARS condition vocabulary.

    PertData.load drops cells whose condition is not representable in the
    perturbation graph (filter_pert_in_go). Conditions absent from
    pert_data.adata would crash get_dataloader; each raw condition is kept
    only if it exists in the GEARS-filtered obs. Per-cell labels are
    unchanged; GEARS filtering is condition-wise, so this is equivalent to
    per-cell alignment while avoiding AnnData view-mutation pitfalls.
    """
    valid = set(pert_data.adata.obs["condition"].astype(str))
    set2conditions = {}
    for split in ["train", "val", "test"]:
        conditions = [c for c in raw_conditions.get(split, []) if c in valid]
        if split == "train" and "ctrl" not in conditions:
            if "ctrl" not in valid:
                raise ValueError("ctrl missing from GEARS-filtered obs")
            conditions = ["ctrl"] + conditions
        if not conditions:
            raise ValueError(f"no GEARS-vocabulary conditions for {split} after GO filter")
        set2conditions[split] = conditions
    path = split_path
    with path.open("wb") as f:
        pickle.dump(set2conditions, f)
    raw_counts = {s: len(c) for s, c in raw_conditions.items()}
    kept_counts = {s: len(c) for s, c in set2conditions.items()}
    pd.DataFrame(
        [
            {
                "split": s,
                "n_conditions_raw_obs": raw_counts.get(s),
                "n_conditions_gears_vocabulary": kept_counts.get(s),
                "conditions_preview": ";".join(set2conditions[s][:8]),
            }
            for s in ["train", "val", "test"]
        ]
    ).to_csv(path.parent / (path.stem + "_gears_vocabulary.tsv"), sep="\t", index=False)
    return path


def build_trimmed_go_tensors(data_root: Path, dataset_name: str, pert_data, k: int = 20) -> tuple[torch.Tensor, torch.Tensor]:
    """GO similarity tensor with official-style top-k trimming per target.

    The raw make_GO edge list can be extremely dense (Replogle essential:
    ~12.1M edges within the 9,853-gene perturbation node map). Official GEARS
    get_similarity_network keeps the top (k+1) neighbors per target
    (num_similar_genes_go_graph). Without that trimming, the GO GNN message
    passing cost grows ~90x versus the frozen Norman pilot and becomes the
    dominant runtime term. This builder applies the same per-target top-k
    trimming the official pipeline applies, keeping the perturbation node set
    unchanged.
    """
    go_csv = Path("data") / f"go_essential_{dataset_name}.csv"
    if not go_csv.exists():
        from gears.utils import make_GO

        make_GO(str(data_root), pert_data.pert_names, dataset_name)
    df = pd.read_csv(go_csv)
    node_map = pert_data.node_map_pert
    df = df[df["source"].isin(node_map) & df["target"].isin(node_map)].copy()
    n_before = len(df)
    df = df.groupby("target").apply(lambda x: x.nlargest(k + 1, ["importance"])).reset_index(drop=True)
    self_edges = pd.DataFrame(
        {"source": list(node_map), "target": list(node_map), "importance": 1.0}
    )
    df = pd.concat([df, self_edges], ignore_index=True).drop_duplicates(["source", "target"])
    edge_index = torch.tensor(
        [(node_map[row.source], node_map[row.target]) for row in df.itertuples(index=False)],
        dtype=torch.long,
    ).T
    edge_weight = torch.tensor(df["importance"].astype(float).to_numpy(), dtype=torch.float32)
    return n_before, edge_index, edge_weight


def audit_control_mean(pert_data) -> np.ndarray:
    try:
        ctrl_adata = pert_data.ctrl_adata
    except Exception:
        ctrl_adata = pert_data.adata[pert_data.adata.obs["condition"].astype(str).eq("ctrl")]
    if ctrl_adata is None:
        ctrl_adata = pert_data.adata[pert_data.adata.obs["condition"].astype(str).eq("ctrl")]
    if ctrl_adata is None or ctrl_adata.n_obs == 0:
        raise ValueError("No control cells available for audit-delta control mean")
    x = ctrl_adata.X
    if hasattr(x, "mean"):
        return np.asarray(x.mean(axis=0)).ravel()
    return np.asarray(np.array(x).mean(axis=0)).ravel()


def audit_control_count(pert_data) -> int:
    try:
        ctrl_adata = pert_data.ctrl_adata
    except Exception:
        ctrl_adata = None
    if ctrl_adata is None:
        ctrl_adata = pert_data.adata[pert_data.adata.obs["condition"].astype(str).eq("ctrl")]
    return int(ctrl_adata.n_obs)


def compute_space_metrics(
    pred_mean: dict,
    truth_mean: dict,
    space: str,
    control: np.ndarray | None,
    seed: int,
    n_resamples: int,
) -> tuple[list[dict], list[dict], dict]:
    shared = sorted(set(pred_mean) & set(truth_mean) - {"ctrl"})
    metric_rows = []
    retrieval_rows = []
    pred_deltas = {}
    truth_deltas = {}
    ctrl_pred = pred_mean.get("ctrl")
    ctrl_truth = truth_mean.get("ctrl")
    for pert in shared:
        pred = np.asarray(pred_mean[pert]).ravel()
        truth = np.asarray(truth_mean[pert]).ravel()
        if space == "audit_delta":
            if control is None:
                raise ValueError("audit_delta space requires an audit control mean")
            pred_delta = pred - control
            truth_delta = truth - control
        elif space == "gears_raw":
            pred_delta = pred - ctrl_pred if ctrl_pred is not None else pred
            truth_delta = truth - ctrl_truth if ctrl_truth is not None else truth
        else:
            raise ValueError(space)
        if not np.isfinite(pred_delta).all() or not np.isfinite(truth_delta).all():
            raise RuntimeError(f"non-finite values for {pert} in {space}")
        pred_deltas[pert] = pred_delta
        truth_deltas[pert] = truth_delta
        expr = expression_metrics(truth_delta, pred_delta)
        null_threshold = float(np.nanpercentile(np.abs(truth_delta), 50))
        support_threshold = float(np.nanpercentile(np.abs(truth_delta), 95))
        uer20 = unsupported_effect_rate_at_k(pred_delta, truth_delta, null_threshold, k=min(20, len(truth_delta)))
        uer50 = unsupported_effect_rate_at_k(pred_delta, truth_delta, null_threshold, k=min(50, len(truth_delta)))
        uer100 = unsupported_effect_rate_at_k(pred_delta, truth_delta, null_threshold, k=min(100, len(truth_delta)))
        sfr = sign_flip_rate(pred_delta, truth_delta, support_threshold=support_threshold)["sign_flip_rate"]
        metric_rows.append(
            {
                "space": space,
                "perturbation": pert,
                "pearson_delta": expr["pearson"],
                "spearman_delta": expr["spearman"],
                "rmse_delta": expr["rmse"],
                "cosine_delta": expr["cosine_similarity"],
                "uer20": uer20,
                "uer50": uer50,
                "uer100": uer100,
                "sign_flip_rate": sfr,
                "null_source": "median_abs_audit_delta",
                "null_status": "sensitivity_only",
            }
        )
    for rr in perturbation_retrieval_rows(pred_deltas, truth_deltas):
        retrieval_rows.append({"space": space, **rr})
    pearsons = [r["pearson_delta"] for r in metric_rows]
    uers50 = [r["uer50"] for r in metric_rows]
    sfrs = [r["sign_flip_rate"] for r in metric_rows]
    retrieval = perturbation_centroid_retrieval(pred_deltas, truth_deltas)
    ci = {
        "pearson": bootstrap_mean_ci(pearsons, n_resamples=n_resamples, seed=seed),
        "uer50": bootstrap_mean_ci(uers50, n_resamples=n_resamples, seed=seed),
        "sign_flip": bootstrap_mean_ci(sfrs, n_resamples=n_resamples, seed=seed),
    }
    summary = {
        "space": space,
        "n_test_perturbations": len(shared),
        "pearson_delta": ci["pearson"]["mean"],
        "pearson_ci95_low": ci["pearson"]["ci95_low"],
        "pearson_ci95_high": ci["pearson"]["ci95_high"],
        "spearman_delta_mean": float(np.nanmean([r["spearman_delta"] for r in metric_rows])),
        "rmse_delta_mean": float(np.nanmean([r["rmse_delta"] for r in metric_rows])),
        "cosine_delta_mean": float(np.nanmean([r["cosine_delta"] for r in metric_rows])),
        "retrieval_top1_accuracy": retrieval["top1_accuracy"],
        "retrieval_top5_accuracy": retrieval["top5_accuracy"],
        "retrieval_mrr": retrieval["mrr"],
        "uer20_mean": float(np.nanmean([r["uer20"] for r in metric_rows])),
        "uer50_mean": ci["uer50"]["mean"],
        "uer50_ci95_low": ci["uer50"]["ci95_low"],
        "uer50_ci95_high": ci["uer50"]["ci95_high"],
        "uer100_mean": float(np.nanmean([r["uer100"] for r in metric_rows])),
        "sign_flip_rate": ci["sign_flip"]["mean"],
        "sign_flip_ci95_low": ci["sign_flip"]["ci95_low"],
        "sign_flip_ci95_high": ci["sign_flip"]["ci95_high"],
        "uncertainty_status": ci["pearson"]["ci_status"],
        "null_status": "sensitivity_only",
        "bns_status": "UNVERIFIED",
    }
    return metric_rows, retrieval_rows, summary


def train_full(model, epochs: int, run_log_path: Path) -> None:
    """Run the official GEARS train loop while capturing stderr telemetry."""
    with open(run_log_path, "w") as log:
        with redirect_stderr(log), redirect_stdout(log):
            model.train(epochs=epochs)


def parse_training_log(raw: Path, out: Path) -> None:
    rows = []
    last_epoch = 0
    for line in raw.read_text(errors="ignore").splitlines():
        stripped = line.strip()
        if "Train Loss:" in stripped:
            parts = stripped.split()
            try:
                epoch = int(parts[1])
                step = int(parts[3])
                loss = float(parts[6])
            except (ValueError, IndexError):
                continue
            rows.append({"epoch": epoch, "step": step, "event": "train_loss", "value": loss})
        elif "Overall MSE:" in stripped:
            epoch = last_epoch
            v = {}
            try:
                for i, tok in enumerate(parts2 := stripped.split()):
                    if tok.startswith("Epoch") or tok == "Epoch":
                        nxt = parts2[i + 1].rstrip(":")
                        if nxt.isdigit():
                            epoch = int(nxt)
                    if tok in ("Train", "Validation") and i + 2 < len(parts2) and parts2[i + 1] == "Overall":
                        v[tok] = float(parts2[i + 3])
            except (ValueError, IndexError):
                continue
            if epoch:
                last_epoch = epoch
            for k, val in v.items():
                rows.append({"epoch": epoch, "step": None, "event": "epoch_mse_" + k.lower(), "value": val})
        elif "DE MSE:" in stripped:
            v = {}
            try:
                for i, tok in enumerate(parts3 := stripped.split()):
                    if tok in ("Train", "Validation") and i + 2 < len(parts3) and parts3[i + 1] == "Top":
                        v[tok] = float(parts3[i + 5])
            except (ValueError, IndexError):
                continue
            for k, val in v.items():
                rows.append({"epoch": last_epoch, "step": None, "event": "epoch_mse_de_" + k.lower(), "value": val})
    pd.DataFrame(rows).to_csv(out, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--test-batch-size", type=int, default=16)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--max-train-batches", type=int, default=0)
    parser.add_argument("--max-eval-batches", type=int, default=0)
    args = parser.parse_args()

    cfg = DATASETS[args.dataset]
    dataset_dir = Path(cfg["source_h5ad"]).parent
    data_root = dataset_dir.parent
    gene_set_path = str(Path("data/raw") / "essential_all_data_pert_genes.pkl")
    gene2go_dst = data_root / "gene2go_all.pkl"
    if not gene2go_dst.exists():
        shutil.copy2(Path("data/raw/gene2go_all.pkl"), gene2go_dst)
    if not (data_root / "gene2go_all.pkl").exists():
        raise FileNotFoundError("gene2go_all.pkl not present under data/raw")

    outdir = Path("results/replogle/gears") / datetime.now(timezone.utc).strftime(
        f"rl1_{args.dataset}_%Y%m%dT%H%M%SZ"
    )
    outdir.mkdir(parents=True, exist_ok=True)
    config_path = Path(cfg["config"])
    if config_path.exists():
        shutil.copy2(config_path, outdir / "config.yaml")
    else:
        (outdir / "config.yaml").write_text(f"# config not found at {config_path}\n")

    import scanpy as sc

    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "STARTED",
        "dataset": cfg["dataset_label"],
        "filtered_data": True,
        "data_completeness_caveat": "GEARS-compatible filtered essential-screen data; NOT the complete Figshare+ processed objects",
        "split": cfg["split"],
        "seed": args.seed,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "test_batch_size": args.test_batch_size,
        "device": args.device,
        "pert_graph": "essential",
        "gene_set_path": gene_set_path,
        "prior_hash": sha16(Path(gene_set_path)),
        "split_hash": cfg["split_hash"],
        "split_hash_source": "reports/replogle_split_integrity_report.md",
        "git_commit": git_commit(),
        "gears_version": "0.1.2",
        "performance_eligible": True,
        "bns_status": "UNVERIFIED",
        "bns_role": "sensitivity_only",
        "bootstrap_resamples": args.bootstrap_resamples,
        "bootstrap_unit": "perturbation",
        "gears_env": os.environ.get("VIRTUAL_ENV", "UNVERIFIED"),
        "max_train_batches": args.max_train_batches,
        "max_eval_batches": args.max_eval_batches,
        "hardware": "UNKNOWN",
    }
    try:
        import platform

        metadata["hardware"] = f"{platform.machine()} CPU"
        metadata["n_cpu_cores"] = os.cpu_count()
    except Exception:
        pass
    started = time.perf_counter()

    try:
        adata = sc.read_h5ad(cfg["source_h5ad"])
        obs = standardized_obs(adata, cfg["dataset_label"], cfg["cell_line"])
        obs = obs.assign(condition=adata.obs["condition"].astype(str).to_numpy())
        metadata["n_source_cells"] = int(len(obs))
        obs_all = None  # split counts are checked per context below
        labels = pd.Series(
            assign_replogle_l1_context_perturbation_holdout(ObsLike(obs), cfg["cell_line"], seed=args.seed),
            index=obs.index,
        )
        obs["vp_split_group"] = labels.to_numpy()
        counts = {k: int((labels == k).sum()) for k in ["train", "val", "test"]}
        expected = FROZEN_SPLIT_COUNTS[cfg["split"]]
        if counts != expected:
            raise RuntimeError(f"Frozen split count mismatch: {counts} != {expected}")
        metadata["n_train_cells"] = counts["train"]
        metadata["n_val_cells"] = counts["val"]
        metadata["n_test_cells"] = counts["test"]
        metadata["n_train_targets"] = int(
            obs.loc[obs["vp_split_group"].eq("train") & obs["control_status"].eq("perturbed"), "perturbation"].nunique()
        )
        metadata["n_test_targets_audit_vocabulary"] = int(
            obs.loc[obs["vp_split_group"].eq("test") & obs["control_status"].eq("perturbed"), "perturbation"].nunique()
        )
        split_dir = dataset_dir / "splits"
        split_dir.mkdir(parents=True, exist_ok=True)
        split_path = write_gears_custom_split(obs, cfg["cell_line"], split_dir, cfg["split"], args.seed)
        metadata["split_dict_path"] = str(split_path)
        raw_conditions = pickle.loads(split_path.read_bytes())
        del obs, adata, labels

        from gears import GEARS, PertData

        pert_data = PertData(
            str(data_root),
            gene_set_path=gene_set_path,
            default_pert_graph=False,
        )
        pert_data.load(data_path=str(dataset_dir))
        metadata["dataset_name_gears"] = pert_data.dataset_name
        metadata["gears_vocabulary_cells"] = int(pert_data.adata.n_obs)
        split_path = rebuild_split_dict_gears_vocabulary(pert_data, split_path, cfg["split"], args.seed, raw_conditions)
        del raw_conditions
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
        metadata["performance_eligible"] = args.max_train_batches == 0
        model.save_model(str(outdir / "model"))
        parse_training_log(outdir / "raw_train_telemetry.log", outdir / "training_log.csv")

        pred_mean, truth_mean = evaluate_gears_batches(model, args.max_eval_batches)
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
                args.seed,
                args.bootstrap_resamples,
            )
            all_metric_rows.extend(metric_rows)
            all_retrieval_rows.extend(retrieval_rows)
            summaries[space] = summary
            subset = summary["n_test_perturbations"]
            metadata[f"n_test_targets_gears_vocabulary_{space}"] = subset
        pd.DataFrame(all_metric_rows).to_csv(outdir / "gears_metrics.csv", index=False)
        pd.DataFrame(
            [
                {k: v for k, v in r.items() if k != "space"}
                | {"space": r["space"], "UER_at_20": r["uer20"], "UER_at_50": r["uer50"], "UER_at_100": r["uer100"]}
                for r in all_metric_rows
            ]
        ).to_csv(outdir / "hallucination_metrics.csv", index=False)
        pd.DataFrame(all_retrieval_rows).to_csv(outdir / "gears_perturbation_retrieval.csv", index=False)
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
        torch.save(centroids, outdir / "gears_delta_centroids.pt")

        pd.DataFrame([summaries["gears_raw"], summaries["audit_delta"]]).to_csv(
            outdir / "gears_summary.csv", index=False
        )
        metadata["summary"] = summaries
        metadata["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        metadata["status"] = "COMPLETED"
        telemetry = (
            (outdir / "raw_train_telemetry.log").read_text(errors="ignore")
            if (outdir / "raw_train_telemetry.log").exists()
            else ""
        )
        (outdir / "run.log").write_text(
            "RUN: " + cfg["dataset_label"] + " split " + cfg["split"]
            + " status " + metadata["run_status"]
            + " elapsed " + str(metadata["elapsed_seconds"]) + " s\n"
            + "-- GEARS telemetry (stderr redirected during official train) --\n"
            + telemetry
        )
        (outdir / "metadata.json").write_text(json.dumps(json_safe(metadata), indent=2) + "\n")
        print(json.dumps(json_safe(metadata["summary"]), indent=2))
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
