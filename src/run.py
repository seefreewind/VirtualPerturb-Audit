from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import yaml

from src.data.loaders import normalize_norman_gears_schema, read_h5ad
from src.data.qc import dataset_qc_summary, write_qc_report
from src.leakage.checks import run_split_integrity_checks
from src.splits.builders import assign_l0_random_cells, assign_l1_perturbation_holdout, assign_l2_component_holdout, split_hash


SPLITTERS = {
    "L0": assign_l0_random_cells,
    "L1": assign_l1_perturbation_holdout,
    "L2": assign_l2_component_holdout,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg_path = Path(args.config)
    cfg = yaml.safe_load(cfg_path.read_text())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    dataset_path = Path(cfg["dataset"]["path"])
    split_name = cfg["split"]["level"]
    outdir = Path(cfg.get("output_dir", "results/pilot")) / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    outdir.mkdir(parents=True, exist_ok=True)

    if not dataset_path.exists():
        metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "BLOCKED",
            "reason": f"Dataset not found: {dataset_path}",
            "config": cfg,
        }
        (outdir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        raise FileNotFoundError(metadata["reason"])

    adata = normalize_norman_gears_schema(read_h5ad(dataset_path))
    adata.obs["split_group"] = SPLITTERS[split_name](adata, seed=int(cfg["seed"]))
    checks = run_split_integrity_checks(adata, split_name)
    (outdir / "split_integrity.json").write_text(json.dumps(checks, indent=2) + "\n")
    write_qc_report(dataset_qc_summary(adata), Path("reports/dataset_qc_report.md"))
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETED",
        "config": cfg,
        "split_hash": split_hash(adata.obs["split_group"].astype(str).tolist()),
        "n_cells": int(adata.n_obs),
        "n_genes": int(adata.n_vars),
    }
    (outdir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()

