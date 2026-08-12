from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.audit_norman_geo_metadata import canonical_condition, parse_guide_identity
from scripts.run_baseline_pilot import SPLITTERS, mean_expr, train_mean_delta
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
    rows = []
    for entry in model_preds:
        model_name, pred, status = entry[:3]
        uers = []
        for pert, true_delta in true_deltas.items():
            pred_delta = pred.get(pert, np.zeros(adata.n_vars)) if isinstance(pred, dict) else pred
            order = np.argsort(-np.abs(pred_delta))[: min(50, len(pred_delta))]
            unsupported = np.abs(true_delta[order]) <= threshold[order]
            uers.append(float(np.mean(unsupported)))
        rows.append({
            "dataset": "Norman2019_GEARS_processed_mirror",
            "model": model_name,
            "split": split,
            "sensitivity": "geo_gemgroup_control_null_q95",
            "status": "COMPLETED_SENSITIVITY_PARTIAL_GEO_LINK",
            "n_test_perturbations": len(true_deltas),
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5ad", default="data/raw/norman/perturb_processed.h5ad")
    parser.add_argument("--geo-identities", default="data/raw/norman_geo/GSE133344_filtered_cell_identities.csv.gz")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    adata = normalize_norman_gears_schema(read_h5ad(Path(args.h5ad)))
    adata = attach_geo_metadata(adata, Path(args.geo_identities))
    rows = []
    for split in ["L1", "L2"]:
        adata.obs["split_group"] = SPLITTERS[split](adata, seed=args.seed)
        threshold = control_gemgroup_null_thresholds(adata)
        model_preds = [
            ("B0_no_change", np.zeros(adata.n_vars), "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            ("B5_mean_effect", train_mean_delta(adata), "COMPLETED_BASELINE_UNVERIFIED_UPPER_BOUND"),
            (
                "FP1_perturbation_blind_mean_effect",
                train_mean_delta(adata),
                "COMPLETED_FALSIFICATION_PROBE",
            ),
            (
                "FP3_label_shuffled_mean_effect",
                shuffled_delta_map(adata, seed=args.seed),
                "COMPLETED_FALSIFICATION_PROBE",
            ),
        ]
        rows.extend(sensitivity_rows(adata, split, model_preds, threshold))
    out = Path("results/pilot/null_envelope_sensitivity.csv")
    pd.DataFrame(rows).to_csv(out, index=False)


if __name__ == "__main__":
    main()
