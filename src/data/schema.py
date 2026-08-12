from __future__ import annotations

REQUIRED_OBS = [
    "dataset",
    "perturbation",
    "perturbation_type",
    "cell_type",
    "cell_line",
    "donor",
    "batch",
    "replicate",
    "control_status",
    "split_group",
]

REQUIRED_VAR = ["gene_symbol", "ensembl_id"]


def validate_anndata_schema(adata) -> list[str]:
    """Return schema problems without mutating the AnnData object."""
    problems: list[str] = []
    for key in REQUIRED_OBS:
        if key not in adata.obs:
            problems.append(f"missing obs.{key}")
    for key in REQUIRED_VAR:
        if key not in adata.var:
            problems.append(f"missing var.{key}")
    return problems

