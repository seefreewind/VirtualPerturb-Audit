from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data.loaders import normalize_norman_gears_schema, read_h5ad
from src.data.qc import dataset_qc_summary, write_qc_report
from src.data.schema import validate_anndata_schema
from src.leakage.checks import run_split_integrity_checks
from src.splits.builders import (
    assign_l0_random_cells,
    assign_l1_perturbation_holdout,
    assign_l2_component_holdout,
    split_hash,
)


SPLITTERS = {
    "L0": assign_l0_random_cells,
    "L1": assign_l1_perturbation_holdout,
    "L2": assign_l2_component_holdout,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5ad", default="data/raw/norman/perturb_processed.h5ad")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    h5ad = Path(args.h5ad)
    if not h5ad.exists():
        raise FileNotFoundError(f"Norman file not found: {h5ad}")

    adata = normalize_norman_gears_schema(read_h5ad(h5ad))
    schema_problems = validate_anndata_schema(adata)
    qc = dataset_qc_summary(adata)
    qc["schema_problems"] = schema_problems
    write_qc_report(qc, Path("reports/dataset_qc_report.md"))

    rows = []
    for split, fn in SPLITTERS.items():
        adata.obs["split_group"] = fn(adata, seed=args.seed)
        checks = run_split_integrity_checks(adata, split)
        for c in checks:
            rows.append({
                "split": split,
                "check": c["check"],
                "status": c["status"],
                "message": c["message"],
                "split_hash": split_hash(adata.obs["split_group"].astype(str).tolist()),
            })
    df = pd.DataFrame(rows)
    df.to_csv("reports/split_integrity_report.tsv", sep="\t", index=False)
    lines = [
        "# Split Integrity Report",
        "",
        f"Status: **{'PASS' if (df['status'] == 'PASS').all() else 'FAIL'}**",
        "",
        f"Audit timestamp UTC: {datetime.now(timezone.utc).isoformat()}",
        f"Dataset SHA256: `{sha256(h5ad)}`",
        "",
        df.to_markdown(index=False),
        "",
    ]
    Path("reports/split_integrity_report.md").write_text("\n".join(lines), encoding="utf-8")

    meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(h5ad),
        "dataset_sha256": sha256(h5ad),
        "n_cells": int(adata.n_obs),
        "n_genes": int(adata.n_vars),
        "qc": qc,
        "split_checks": rows,
    }
    Path("data/metadata/norman_local_audit.json").write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    main()

