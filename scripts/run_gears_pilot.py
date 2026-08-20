from __future__ import annotations

import argparse
import json
import math
import os
import pickle
import shutil
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import torch
import torch.optim as optim

from src.hallucination.metrics import sign_flip_rate, unsupported_effect_rate_at_k
from src.metrics.bounds import bound_normalized_score
from src.metrics.expression import expression_metrics
from src.metrics.retrieval import perturbation_centroid_retrieval, perturbation_retrieval_rows
from src.statistics.bootstrap import bootstrap_mean_ci
from src.data.loaders import normalize_norman_gears_schema, read_h5ad
from src.splits.builders import assign_l1_perturbation_holdout, assign_l2_component_holdout, assign_l3_gene_family_holdout


SPLITTERS = {"L1": assign_l1_perturbation_holdout, "L2": assign_l2_component_holdout, "L3": assign_l3_gene_family_holdout}


def write_gears_custom_split(dataset_dir: Path, level: str, seed: int, adata=None) -> Path:
    if adata is None:
        adata = normalize_norman_gears_schema(read_h5ad(dataset_dir / "perturb_processed.h5ad"))
    else:
        adata = normalize_norman_gears_schema(adata.copy())
    adata.obs["split_group"] = SPLITTERS[level](adata, seed=seed)
    condition_key = "condition" if "condition" in adata.obs else "perturbation"
    split_key = "split_group"
    set2conditions = {}
    for split in ["train", "val", "test"]:
        vals = sorted(adata.obs.loc[adata.obs[split_key].eq(split), condition_key].astype(str).unique())
        if split == "train" and "ctrl" not in vals and "ctrl" in set(adata.obs[condition_key].astype(str)):
            vals = ["ctrl"] + vals
        set2conditions[split] = vals
    out = dataset_dir / "splits" / f"virtualperturb_audit_{level}_seed{seed}.pkl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as f:
        pickle.dump(set2conditions, f)
    pd.DataFrame([
        {"split": k, "n_conditions": len(v), "conditions_preview": ";".join(v[:8])}
        for k, v in set2conditions.items()
    ]).to_csv(dataset_dir / "splits" / f"virtualperturb_audit_{level}_seed{seed}.tsv", sep="\t", index=False)
    return out


def build_filtered_go_tensors(data_root: Path, dataset_name: str, pert_data) -> tuple[torch.Tensor, torch.Tensor]:
    go_csv = Path("data") / f"go_essential_{dataset_name}.csv"
    if not go_csv.exists():
        from gears.utils import make_GO

        make_GO(str(data_root), pert_data.pert_names, dataset_name)
    df = pd.read_csv(go_csv)
    node_map = pert_data.node_map_pert
    df = df[df["source"].isin(node_map) & df["target"].isin(node_map)].copy()
    self_edges = pd.DataFrame(
        {"source": list(node_map), "target": list(node_map), "importance": 1.0}
    )
    df = pd.concat([df, self_edges], ignore_index=True).drop_duplicates(["source", "target"])
    edge_index = torch.tensor(
        [(node_map[row.source], node_map[row.target]) for row in df.itertuples(index=False)],
        dtype=torch.long,
    ).T
    edge_weight = torch.tensor(df["importance"].astype(float).to_numpy(), dtype=torch.float32)
    return edge_index, edge_weight


def train_smoke_batches(model, max_train_batches: int) -> list[float]:
    from gears.utils import loss_fct

    model.model = model.model.to(model.device)
    model.model.train()
    optimizer = optim.Adam(model.model.parameters(), lr=1e-3, weight_decay=5e-4)
    losses = []
    for step, batch in enumerate(model.dataloader["train_loader"]):
        if step >= max_train_batches:
            break
        batch.to(model.device)
        optimizer.zero_grad()
        pred = model.model(batch)
        loss = loss_fct(
            pred,
            batch.y,
            batch.pert,
            ctrl=model.ctrl_expression,
            dict_filter=model.dict_filter,
            direction_lambda=model.config["direction_lambda"],
        )
        loss.backward()
        torch.nn.utils.clip_grad_value_(model.model.parameters(), clip_value=1.0)
        optimizer.step()
        losses.append(float(loss.item()))
    model.best_model = model.model
    return losses


def evaluate_gears_batches(model, max_eval_batches: int) -> tuple[dict, dict]:
    pred_by_pert = {}
    truth_by_pert = {}
    model.best_model = model.best_model.to(model.device)
    model.best_model.eval()
    for step, batch in enumerate(model.dataloader["test_loader"]):
        if max_eval_batches > 0 and step >= max_eval_batches:
            break
        batch.to(model.device)
        with torch.no_grad():
            pred = model.best_model(batch).detach().cpu().numpy()
        truth = batch.y.detach().cpu().numpy()
        for pert, pred_row, truth_row in zip(batch.pert, pred, truth):
            pred_by_pert.setdefault(str(pert), []).append(pred_row)
            truth_by_pert.setdefault(str(pert), []).append(truth_row)
    pred_mean = {k: pd.DataFrame(v).mean(axis=0).to_numpy() for k, v in pred_by_pert.items()}
    truth_mean = {k: pd.DataFrame(v).mean(axis=0).to_numpy() for k, v in truth_by_pert.items()}
    return pred_mean, truth_mean


def append_gears_summary(
    pred_mean: dict,
    truth_mean: dict,
    outdir: Path,
    split: str,
    status: str,
    max_train_batches: int,
    max_eval_batches: int,
) -> dict:
    shared = sorted(set(pred_mean) & set(truth_mean) - {"ctrl"})
    pearsons = []
    uers = []
    sfrs = []
    metric_rows = []
    pred_deltas = {}
    truth_deltas = {}
    ctrl_pred = pred_mean.get("ctrl")
    ctrl_truth = truth_mean.get("ctrl")
    for pert in shared:
        pred = pred_mean[pert]
        truth = truth_mean[pert]
        pred_delta = pred - ctrl_pred if ctrl_pred is not None else pred
        truth_delta = truth - ctrl_truth if ctrl_truth is not None else truth
        pred_deltas[pert] = pred_delta
        truth_deltas[pert] = truth_delta
        expr = expression_metrics(truth_delta, pred_delta)
        null_threshold = float(pd.Series(abs(truth_delta)).quantile(0.50))
        support_threshold = float(pd.Series(abs(truth_delta)).quantile(0.95))
        halluc = sign_flip_rate(pred_delta, truth_delta, support_threshold=support_threshold)
        uer = unsupported_effect_rate_at_k(pred_delta, truth_delta, null_threshold, k=min(50, len(truth_delta)))
        pearsons.append(expr["pearson"])
        uers.append(uer)
        sfrs.append(halluc["sign_flip_rate"])
        metric_rows.append({
            "perturbation": pert,
            "pearson_delta": expr["pearson"],
            "rmse_delta": expr["rmse"],
            "UER_at_50": uer,
            "sign_flip_rate": halluc["sign_flip_rate"],
        })
    pd.DataFrame(metric_rows).to_csv(outdir / "gears_metrics.csv", index=False)
    if shared:
        torch.save(
            {
                "perturbations": shared,
                "pred_delta": {pert: torch.as_tensor(pred_deltas[pert]) for pert in shared},
                "truth_delta": {pert: torch.as_tensor(truth_deltas[pert]) for pert in shared},
            },
            outdir / "gears_delta_centroids.pt",
        )
    pearson_ci = bootstrap_mean_ci(pearsons, seed=1)
    uer_ci = bootstrap_mean_ci(uers, seed=1)
    sfr_ci = bootstrap_mean_ci(sfrs, seed=1)
    mean_pearson = pearson_ci["mean"]
    bns, bns_status = bound_normalized_score(mean_pearson, float("nan"), float("nan"))
    retrieval = perturbation_centroid_retrieval(pred_deltas, truth_deltas)
    retrieval_rows = []
    for retrieval_row in perturbation_retrieval_rows(pred_deltas, truth_deltas):
        retrieval_rows.append({
            "dataset": "Norman2019_GEARS_processed_mirror",
            "model": "GEARS_cell_gears_0.1.2",
            "split": split,
            **retrieval_row,
        })
    pd.DataFrame(retrieval_rows).to_csv(outdir / "gears_perturbation_retrieval.csv", index=False)
    row = {
        "dataset": "Norman2019_GEARS_processed_mirror",
        "model": "GEARS_cell_gears_0.1.2",
        "split": split,
        "status": status,
        "n_test_perturbations": len(shared),
        "pearson_delta": mean_pearson,
        "pearson_delta_ci95_low": pearson_ci["ci95_low"],
        "pearson_delta_ci95_high": pearson_ci["ci95_high"],
        "bns": bns,
        "bns_status": bns_status,
        "UER_at_50": uer_ci["mean"],
        "UER_at_50_ci95_low": uer_ci["ci95_low"],
        "UER_at_50_ci95_high": uer_ci["ci95_high"],
        "sign_flip_rate": sfr_ci["mean"],
        "sign_flip_rate_ci95_low": sfr_ci["ci95_low"],
        "sign_flip_rate_ci95_high": sfr_ci["ci95_high"],
        "retrieval_top1_accuracy": retrieval["top1_accuracy"],
        "retrieval_top5_accuracy": retrieval["top5_accuracy"],
        "retrieval_mrr": retrieval["mrr"],
        "uncertainty_status": pearson_ci["ci_status"],
        "notes": (
            "GEARS bounded development run; not a full performance benchmark. "
            f"train_batches={max_train_batches}; eval_batches={max_eval_batches}; "
            "replicate upper bound not yet verified."
        ),
    }
    summary_path = Path("results/pilot/pilot_summary.csv")
    if summary_path.exists():
        summary = pd.read_csv(summary_path)
        summary = summary[
            ~(
                summary["model"].eq(row["model"])
                & summary["split"].eq(row["split"])
                & summary["status"].eq(row["status"])
            )
        ]
        summary = pd.concat([summary, pd.DataFrame([row])], ignore_index=True)
    else:
        summary = pd.DataFrame([row])
    summary.to_csv(summary_path, index=False)
    retrieval_path = Path("results/pilot/perturbation_retrieval.csv")
    retrieval_df = pd.DataFrame(retrieval_rows)
    if retrieval_path.exists():
        existing = pd.read_csv(retrieval_path)
        existing = existing[
            ~(
                existing["model"].eq(row["model"])
                & existing["split"].eq(row["split"])
                & existing["perturbation"].isin(retrieval_df["perturbation"] if not retrieval_df.empty else [])
            )
        ]
        retrieval_df = pd.concat([existing, retrieval_df], ignore_index=True)
    retrieval_df.to_csv(retrieval_path, index=False)
    return row


def json_safe(value):
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="data/raw")
    parser.add_argument("--dataset-dir", default="data/raw/norman")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--test-batch-size", type=int, default=16)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--audit-split", choices=["official_simulation", "L1", "L2", "L3"], default="L1")
    parser.add_argument("--pert-graph", choices=["default", "essential", "dynamic"], default="essential")
    parser.add_argument("--max-train-batches", type=int, default=0)
    parser.add_argument("--max-eval-batches", type=int, default=0)
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    h5ad = dataset_dir / "perturb_processed.h5ad"
    if not h5ad.exists() or (dataset_dir / "perturb_processed.h5ad.aria2").exists():
        raise FileNotFoundError(
            f"Complete GEARS Norman file is not available at {h5ad}. "
            "If .aria2 exists, the download is incomplete."
        )

    from gears import GEARS, PertData

    outdir = Path("results/pilot") / datetime.now(timezone.utc).strftime("gears_%Y%m%dT%H%M%SZ")
    outdir.mkdir(parents=True, exist_ok=True)

    gene_set_path = None
    if args.pert_graph == "essential":
        gene_set_path = str(Path(args.data_root) / "essential_all_data_pert_genes.pkl")
    pert_data = PertData(
        args.data_root,
        gene_set_path=gene_set_path,
        default_pert_graph=(args.pert_graph == "default"),
    )
    if not (Path(args.data_root) / "norman").exists():
        shutil.copytree(dataset_dir, Path(args.data_root) / "norman")
    pert_data.load(data_path=str(Path(args.data_root) / "norman"))
    if args.audit_split == "official_simulation":
        pert_data.prepare_split(split="simulation", seed=args.seed)
    else:
        split_path = write_gears_custom_split(Path(args.data_root) / "norman", args.audit_split, args.seed, adata=pert_data.adata)
        pert_data.prepare_split(split="custom", seed=args.seed, split_dict_path=str(split_path))
    pert_data.get_dataloader(batch_size=args.batch_size, test_batch_size=args.test_batch_size)

    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "STARTED",
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "test_batch_size": args.test_batch_size,
        "device": args.device,
        "seed": args.seed,
        "audit_split": args.audit_split,
        "pert_graph": args.pert_graph,
        "max_train_batches": args.max_train_batches,
        "max_eval_batches": args.max_eval_batches,
        "gears_env": os.environ.get("VIRTUAL_ENV", "UNVERIFIED"),
    }
    run_started = time.perf_counter()
    try:
        model = GEARS(pert_data, device=args.device, weight_bias_track=False)
        if args.pert_graph == "default":
            model.model_initialize()
        else:
            G_go, G_go_weight = build_filtered_go_tensors(Path(args.data_root), pert_data.dataset_name, pert_data)
            metadata["filtered_go_edges"] = int(G_go.shape[1])
            metadata["filtered_go_nodes"] = int(len(pert_data.node_map_pert))
            model.model_initialize(G_go=G_go, G_go_weight=G_go_weight)
        if args.max_train_batches > 0:
            losses = train_smoke_batches(model, args.max_train_batches)
            metadata["status"] = "COMPLETED_GEARS_BATCH_SMOKE"
            metadata["train_batches_completed"] = len(losses)
            metadata["train_loss_first"] = losses[0] if losses else None
            metadata["train_loss_last"] = losses[-1] if losses else None
        else:
            model.train(epochs=args.epochs)
            metadata["status"] = "COMPLETED_GEARS_SMOKE" if args.epochs <= 1 else "COMPLETED_GEARS"
        model.save_model(str(outdir / "model"))
        if args.max_eval_batches != 0 or args.max_train_batches > 0:
            pred_mean, truth_mean = evaluate_gears_batches(model, args.max_eval_batches)
            metadata["eval_predicted_perturbations"] = int(len(pred_mean))
            metadata["eval_truth_perturbations"] = int(len(truth_mean))
            summary_row = append_gears_summary(
                pred_mean,
                truth_mean,
                outdir,
                args.audit_split,
                "COMPLETED_GEARS_BATCH_SMOKE_NOT_PERFORMANCE",
                args.max_train_batches,
                args.max_eval_batches,
            )
            metadata["summary_row"] = summary_row
        metadata["elapsed_seconds"] = round(time.perf_counter() - run_started, 3)
        (outdir / "metadata.json").write_text(json.dumps(json_safe(metadata), indent=2) + "\n")
    except Exception as exc:
        metadata["elapsed_seconds"] = round(time.perf_counter() - run_started, 3)
        metadata["status"] = "FAILED_GEARS"
        metadata["error_type"] = type(exc).__name__
        metadata["error"] = str(exc)
        (outdir / "metadata.json").write_text(json.dumps(json_safe(metadata), indent=2) + "\n")
        (outdir / "traceback.txt").write_text(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
