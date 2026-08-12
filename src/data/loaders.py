from __future__ import annotations

from pathlib import Path


def read_h5ad(path: str | Path):
    import scanpy as sc

    return sc.read_h5ad(path)


def normalize_norman_gears_schema(adata):
    """Map GEARS Norman fields to the audit schema without fitting transforms."""
    obs = adata.obs
    if "condition" in obs and "perturbation" not in obs:
        adata.obs["perturbation"] = obs["condition"].astype(str)
    if "control" in obs and "control_status" not in obs:
        adata.obs["control_status"] = obs["control"].map(
            lambda x: "control" if bool(x) else "perturbed"
        )
    defaults = {
        "dataset": "Norman2019_GEARS_processed",
        "perturbation_type": "CRISPRa",
        "cell_type": "K562",
        "cell_line": "K562",
        "donor": "not_applicable_cell_line",
        "batch": "UNVERIFIED",
        "replicate": "UNVERIFIED",
        "split_group": "unassigned",
    }
    for key, value in defaults.items():
        if key not in adata.obs:
            adata.obs[key] = value
    if "gene_name" in adata.var and "gene_symbol" not in adata.var:
        adata.var["gene_symbol"] = adata.var["gene_name"].astype(str)
    if "ensembl_id" not in adata.var:
        adata.var["ensembl_id"] = "UNVERIFIED"
    return adata

