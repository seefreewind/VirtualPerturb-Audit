from __future__ import annotations

import argparse
from pathlib import Path

import json
import numpy as np
import pandas as pd
import torch

from scripts.audit_norman_geo_metadata import canonical_condition, parse_guide_identity
from scripts.run_baseline_pilot import (
    SPLITTERS,
    additive_delta_map,
    context_matched_delta_map,
    mean_expr,
    pca_ridge_delta_map,
    train_global_perturbed_mean_delta,
    train_mean_delta,
)
from scripts.run_falsification_pilot import shuffled_delta_map
from src.data.loaders import normalize_norman_gears_schema, read_h5ad
from src.hallucination.metrics import unsupported_effect_rate_at_k


def attach_geo_metadata(adata, geo_path: Path):
    geo = pd.read_csv(geo_path).drop_duplicates("cell_barcode").set_index("cell_barcode")
    geo["guide_condition_parsed"] = geo["guide_identity"].map(parse_guide_identity)
    obs = adata.obs.join(geo[["guide_identity", "gemgroup", "guide_condition_parsed"]], how="left")
    matched = obs["guide_identity"].notna()
    concordant = (
        obs.loc[matched, "perturbation"].astype(str).map(canonical_condition)
        == obs.loc[matched, "guide_condition_parsed"].astype(str).map(canonical_condition)
    )
    usable = matched.copy()
    usable.loc[matched] = concordant.to_numpy()
    adata.obs["geo_gemgroup"] = obs["gemgroup"]
    adata.obs["geo_metadata_usable"] = usable.to_numpy()
    return adata


def control_gemgroup_null_thresholds(adata, quantile: float = 0.95) -> np.ndarray:
    obs = adata.obs
    usable_ctrl = (
        obs["control_status"].astype(str).eq("control")
        & obs["geo_metadata_usable"].astype(bool)
        & obs["geo_gemgroup"].notna()
    )
    ctrl_all = mean_expr(adata, usable_ctrl)
    deltas = []
    for gemgroup in sorted(obs.loc[usable_ctrl, "geo_gemgroup"].dropna().unique()):
        mask = usable_ctrl & obs["geo_gemgroup"].eq(gemgroup)
        if int(mask.sum()) > 1:
            deltas.append(mean_expr(adata, mask) - ctrl_all)
    if not deltas:
        return np.full(adata.n_vars, np.nan)
    return np.nanquantile(np.abs(np.vstack(deltas)), quantile, axis=0)


def sensitivity_rows(adata, split: str, model_preds, threshold: np.ndarray):
    true_deltas, _ = summarize_truth(adata)
    canonical_truth = {canonical_condition(pert): pert for pert in true_deltas}
    rows = []
    for entry in model_preds:
        model_name, pred, status = entry[:3]
        pred_lookup = None
        if isinstance(pred, dict):
            pred_lookup = {canonical_condition(k): v for k, v in pred.items()}
        uers = []
        n_covered = 0
        for pert, true_delta in true_deltas.items():
            key = canonical_condition(pert)
            if pred_lookup is not None:
                if key not in pred_lookup:
                    continue
                pred_delta = pred_lookup[key]
                n_covered += 1
            else:
                pred_delta = pred
                n_covered += 1
            order = np.argsort(-np.abs(pred_delta))[: min(50, len(pred_delta))]
            unsupported = np.abs(true_delta[order]) <= threshold[order]
            uers.append(float(np.mean(unsupported)))
        rows.append({
            "dataset": "Norman2019_GEARS_processed_mirror",
            "model": model_name,
            "split": split,
            "sensitivity": "geo_gemgroup_control_null_q95",
            "status": "COMPLETED_SENSITIVITY_PARTIAL_GEO_LINK",
            "n_test_perturbations": n_covered,
            "UER_at_50_gemgroup_null_q95": float(np.nanmean(uers)) if uers else np.nan,
            "notes": "Control-control gemgroup null envelope; partial GEO metadata link, not replicate-derived BNS upper bound.",
        })
    return rows


def summarize_truth(adata):
    obs = adata.obs
    control_mask = obs["control_status"].astype(str).eq("control")
    ctrl = mean_expr(adata, control_mask)
    out = {}
    for pert in sorted(obs.loc[(obs["split_group"] == "test") & ~control_mask, "perturbation"].astype(str).unique()):
        mask = (obs["split_group"] == "test") & obs["perturbation"].astype(str).eq(pert)
        out[pert] = mean_expr(adata, mask) - ctrl
    return out, ctrl


def completed_gears_pred_deltas(results_dir: Path = Path("results/pilot")) -> dict:
    preds = {}
    for run_dir in sorted(results_dir.glob("gears_*")):
        meta_path = run_dir / "metadata.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        summary_row = meta.get("summary_row") or {}
        if summary_row.get("status") != "COMPLETED_GEARS_EVALUATION":
            continue
        split = meta.get("audit_split")
        centroids_path = run_dir / "gears_delta_centroids.pt"
        if not split or not centroids_path.exists():
            continue
        centroids = torch.load(centroids_path, map_location="cpu", weights_only=False)
        preds[split] = {
            "pred_delta": {
                pert: vec.detach().cpu().numpy()
                for pert, vec in centroids["pred_delta"].items()
            },
            "truth_delta": {
                pert: vec.detach().cpu().numpy()
                for pert, vec in centroids["truth_delta"].items()
            },
        }
    return preds


def gears_sensitivity_rows(adata, split: str, gears_deltas: dict, threshold: np.ndarray) -> list[dict]:
    pred_raw = gears_deltas["pred_delta"]
    truth_raw = gears_deltas["truth_delta"]
    ctrl = mean_expr(adata, adata.obs["control_status"].astype(str).eq("control"))
    shared = sorted(set(pred_raw) & set(truth_raw) - {"ctrl"})
    uers = []
    for pert in shared:
        pred_delta = np.asarray(pred_raw[pert]) - ctrl
        true_delta = np.asarray(truth_raw[pert]) - ctrl
        order = np.argsort(-np.abs(pred_delta))[: min(50, len(pred_delta))]
        unsupported = np.abs(true_delta[order]) <= threshold[order]
        uers.append(float(np.mean(unsupported)))
    return [{
        "dataset": "Norman2019_GEARS_processed_mirror",
        "model": "GEARS_cell_gears_0.1.2",
        "split": split,
        "sensitivity": "geo_gemgroup_control_null_q95",
        "status": "COMPLETED_SENSITIVITY_GEARS_EVALUATION",
        "n_test_perturbations": len(shared),
        "UER_at_50_gemgroup_null_q95": float(np.nanmean(uers)) if uers else np.nan,
        "notes": "Control-control gemgroup null envelope; GEARS raw predictions and truth converted to audit-delta space via audit control mean; GEARS-run test vocabulary; partial GEO metadata link, not replicate-derived BNS upper bound.",
    }]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5ad", default="data/raw/norman/perturb_processed.h5ad")
    parser.add_argument("--geo-identities", default="data/raw/norman_geo/GSE133344_filtered_cell_identities.csv.gz")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    adata = normalize_norman_gears_schema(read_h5ad(Path(args.h5ad)))
    adata = attach_geo_metadata(adata, Path(args.geo_identities))
    gears_preds = completed_gears_pred_deltas()
    rows = []
    for split in ["L1", "L2", "L3"]:
        adata.obs["split_group"] = SPLITTERS[split](adata, seed=args.seed)
        mean_delta = train_mean_delta(adata)
        threshold = control_gemgroup_null_thresholds(adata)
        model_preds = [
            ("B0_no_change", np.zeros(adata.n_vars), "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            (
                "B1_global_perturbed_mean",
                train_global_perturbed_mean_delta(adata),
                "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND",
            ),
            (
                "B2_context_matched_perturbed_mean",
                context_matched_delta_map(adata, fallback=mean_delta),
                "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND",
            ),
            (
                "B3_additive_seen_component",
                additive_delta_map(adata, fallback=mean_delta),
                "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND",
            ),
            (
                "B4_pca_ridge",
                pca_ridge_delta_map(adata, fallback=mean_delta),
                "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND",
            ),
            ("B5_mean_effect", mean_delta, "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            (
                "FP1_perturbation_blind_mean_effect",
                mean_delta,
                "COMPLETED_FALSIFICATION_PROBE",
            ),
            (
                "FP2_cell_state_blind_additive",
                additive_delta_map(adata, fallback=mean_delta),
                "COMPLETED_FALSIFICATION_PROBE",
            ),
            (
                "FP3_label_shuffled_mean_effect",
                shuffled_delta_map(adata, seed=args.seed),
                "COMPLETED_FALSIFICATION_PROBE",
            ),
        ]
        rows.extend(sensitivity_rows(adata, split, model_preds, threshold))
        if split in gears_preds:
            rows.extend(gears_sensitivity_rows(adata, split, gears_preds[split], threshold))
    out = Path("results/pilot/null_envelope_sensitivity.csv")
    pd.DataFrame(rows).to_csv(out, index=False)


if __name__ == "__main__":
    main()
