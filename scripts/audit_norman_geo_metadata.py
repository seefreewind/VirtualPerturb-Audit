from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import scanpy as sc



def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_guide_identity(value) -> str | None:
    if pd.isna(value):
        return None
    left = str(value).split("__")[0]
    genes = [part for part in left.split("_") if not part.startswith("NegCtrl")]
    if not genes:
        return "ctrl"
    if len(genes) == 1:
        return f"{genes[0]}+ctrl"
    return "+".join(genes[:2])


def canonical_condition(value) -> tuple[str, ...] | None:
    if value is None or pd.isna(value):
        return None
    value = str(value)
    if value == "ctrl":
        return ("ctrl",)
    return tuple(sorted(value.split("+")))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5ad", default="data/raw/norman/perturb_processed.h5ad")
    parser.add_argument("--geo-identities", default="data/raw/norman_geo/GSE133344_filtered_cell_identities.csv.gz")
    args = parser.parse_args()

    h5ad = Path(args.h5ad)
    geo_path = Path(args.geo_identities)
    if not h5ad.exists():
        raise FileNotFoundError(f"Norman GEARS AnnData not found: {h5ad}")
    if not geo_path.exists():
        raise FileNotFoundError(f"Norman GEO cell identities file not found: {geo_path}")

    adata = sc.read_h5ad(h5ad, backed="r")
    geo = pd.read_csv(geo_path)
    duplicate_barcodes = int(geo["cell_barcode"].duplicated().sum())
    geo = geo.drop_duplicates("cell_barcode").set_index("cell_barcode")
    obs = adata.obs.copy()
    joined = obs.join(geo, how="left")
    matched = joined[joined["guide_identity"].notna()].copy()
    matched["guide_condition_parsed"] = matched["guide_identity"].map(parse_guide_identity)
    exact_concordance = float((matched["condition"].astype(str) == matched["guide_condition_parsed"].astype(str)).mean())
    unordered_concordance = float(
        (
            matched["condition"].astype(str).map(canonical_condition)
            == matched["guide_condition_parsed"].astype(str).map(canonical_condition)
        ).mean()
    )
    gemgroup_counts = matched["gemgroup"].value_counts(dropna=False).sort_index()
    ctrl_by_gemgroup = matched[matched["condition"].astype(str).eq("ctrl")].groupby("gemgroup").size()

    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gears_h5ad": str(h5ad),
        "geo_identities": str(geo_path),
        "geo_identities_sha256": sha256(geo_path),
        "gears_cells": int(adata.n_obs),
        "geo_rows": int(len(geo) + duplicate_barcodes),
        "geo_unique_barcodes": int(len(geo)),
        "geo_duplicate_barcodes": duplicate_barcodes,
        "matched_cells": int(joined["guide_identity"].notna().sum()),
        "unmatched_gears_cells": int(joined["guide_identity"].isna().sum()),
        "matched_fraction_of_gears": float(joined["guide_identity"].notna().mean()),
        "guide_identity_nunique": int(geo["guide_identity"].nunique()),
        "gemgroup_nunique": int(matched["gemgroup"].nunique(dropna=True)),
        "exact_condition_concordance": exact_concordance,
        "unordered_condition_concordance": unordered_concordance,
        "status": "PARTIAL_LINK_PASS" if unordered_concordance > 0.99 and joined["guide_identity"].notna().mean() > 0.95 else "PARTIAL_LINK_WARNING",
    }

    Path("data/metadata").mkdir(parents=True, exist_ok=True)
    pd.Series(metrics).to_json("data/metadata/norman_geo_metadata_link.json", indent=2)
    pd.DataFrame({"gemgroup": gemgroup_counts.index.astype(str), "matched_cells": gemgroup_counts.values}).to_csv(
        "reports/norman_geo_gemgroup_counts.tsv", sep="\t", index=False
    )
    pd.DataFrame({"gemgroup": ctrl_by_gemgroup.index.astype(str), "matched_ctrl_cells": ctrl_by_gemgroup.values}).to_csv(
        "reports/norman_geo_ctrl_by_gemgroup.tsv", sep="\t", index=False
    )

    report = [
        "# Norman GEO Metadata Link Audit",
        "",
        f"Status: **{metrics['status']}**",
        "",
        f"Audit timestamp UTC: {metrics['timestamp']}",
        f"GEO identities SHA256: `{metrics['geo_identities_sha256']}`",
        "",
        "## Match Summary",
        "",
        f"- GEARS AnnData cells: {metrics['gears_cells']}",
        f"- GEO identity rows: {metrics['geo_rows']}",
        f"- Unique GEO barcodes: {metrics['geo_unique_barcodes']}",
        f"- Matched GEARS cells: {metrics['matched_cells']}",
        f"- Unmatched GEARS cells: {metrics['unmatched_gears_cells']}",
        f"- Matched fraction of GEARS cells: {metrics['matched_fraction_of_gears']:.4f}",
        f"- Exact condition concordance: {metrics['exact_condition_concordance']:.4f}",
        f"- Unordered condition concordance: {metrics['unordered_condition_concordance']:.4f}",
        f"- gemgroup count: {metrics['gemgroup_nunique']}",
        "",
        "## Interpretation",
        "",
        "The GEO cell-identity file provides guide identity and `gemgroup`, enabling a batch-like metadata audit for most GEARS cells. The link is partial because a subset of GEARS cells do not have exact barcode matches in the GEO identities file. Use `gemgroup` for sensitivity and null-envelope analyses only with explicit partial-link reporting.",
        "",
        "## Generated Side Tables",
        "",
        "- `reports/norman_geo_gemgroup_counts.tsv`",
        "- `reports/norman_geo_ctrl_by_gemgroup.tsv`",
    ]
    Path("reports/NORMAN_GEO_METADATA_LINK_REPORT.md").write_text("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
