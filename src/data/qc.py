from __future__ import annotations

import pandas as pd


def dataset_qc_summary(adata) -> dict:
    obs = adata.obs
    control_mask = obs["control_status"].astype(str).str.lower().eq("control")
    cells_per_pert = obs.groupby("perturbation").size().sort_values()
    batch_pert = (
        obs.groupby(["batch", "perturbation"]).size().rename("n_cells").reset_index()
        if "batch" in obs
        else pd.DataFrame()
    )
    status = "PASS"
    warnings = []
    if cells_per_pert.empty:
        status = "FAIL"
        warnings.append("No perturbation labels found.")
    elif cells_per_pert.min() < 10:
        status = "WARNING"
        warnings.append("At least one perturbation has fewer than 10 cells.")
    if control_mask.sum() == 0:
        status = "FAIL"
        warnings.append("No controls found.")
    return {
        "status": status,
        "n_cells": int(adata.n_obs),
        "n_genes": int(adata.n_vars),
        "n_perturbations": int(obs["perturbation"].nunique()),
        "n_controls": int(control_mask.sum()),
        "min_cells_per_perturbation": int(cells_per_pert.min()) if len(cells_per_pert) else 0,
        "median_cells_per_perturbation": float(cells_per_pert.median()) if len(cells_per_pert) else 0.0,
        "batch_perturbation_rows": int(len(batch_pert)),
        "warnings": warnings,
    }


def write_qc_report(summary: dict, path):
    lines = [
        "# Dataset QC Report",
        "",
        f"Status: **{summary['status']}**",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key in [
        "n_cells",
        "n_genes",
        "n_perturbations",
        "n_controls",
        "min_cells_per_perturbation",
        "median_cells_per_perturbation",
        "batch_perturbation_rows",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.extend(["", "## Warnings"])
    lines.extend([f"- {w}" for w in summary["warnings"]] or ["- None"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

