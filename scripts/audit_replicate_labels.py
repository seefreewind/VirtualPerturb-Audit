from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data.loaders import normalize_norman_gears_schema, read_h5ad


CANDIDATE_TOKENS = ("rep", "batch", "gem", "lane", "library", "sample", "well", "plate", "donor")
UNINFORMATIVE_VALUES = {"UNVERIFIED", "UNKNOWN", "NA", "nan", "not_applicable_cell_line", "None", ""}


def summarize_series(source: str, column: str, series: pd.Series) -> dict:
    values = series.astype(str)
    counts = values.value_counts(dropna=False)
    informative = [v for v in counts.index.astype(str) if v not in UNINFORMATIVE_VALUES]
    return {
        "source": source,
        "column": column,
        "n_rows": int(len(series)),
        "n_unique": int(values.nunique(dropna=False)),
        "top_values": ";".join(f"{idx}:{int(val)}" for idx, val in counts.head(8).items()),
        "has_multiple_informative_values": len(informative) > 1,
        "interpretation": "BATCH_LIKE_CANDIDATE" if column.lower() == "gemgroup" else "TRUE_REPLICATE_UNVERIFIED",
    }


def candidate_columns(df: pd.DataFrame) -> list[str]:
    return [col for col in df.columns if any(token in col.lower() for token in CANDIDATE_TOKENS)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5ad", default="data/raw/norman/perturb_processed.h5ad")
    parser.add_argument("--geo-identities", default="data/raw/norman_geo/GSE133344_filtered_cell_identities.csv.gz")
    args = parser.parse_args()

    rows = []
    adata = normalize_norman_gears_schema(read_h5ad(Path(args.h5ad)))
    for col in candidate_columns(adata.obs):
        rows.append(summarize_series("GEARS_AnnData_obs", col, adata.obs[col]))

    geo_path = Path(args.geo_identities)
    if geo_path.exists():
        geo = pd.read_csv(geo_path)
        for col in candidate_columns(geo):
            rows.append(summarize_series("GEO_cell_identities", col, geo[col]))

    df = pd.DataFrame(rows)
    Path("reports").mkdir(parents=True, exist_ok=True)
    Path("data/metadata").mkdir(parents=True, exist_ok=True)
    df.to_csv("reports/replicate_label_audit.tsv", sep="\t", index=False)

    has_true_replicate = bool(
        df[
            df["has_multiple_informative_values"]
            & df["column"].str.lower().str.contains("rep|sample|well|plate|library|lane", regex=True)
        ].shape[0]
    )
    status = "TRUE_REPLICATE_CANDIDATE_FOUND" if has_true_replicate else "TRUE_REPLICATE_NOT_FOUND"
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "h5ad": args.h5ad,
        "geo_identities": args.geo_identities,
        "candidate_columns": rows,
        "interpretation": "GEO gemgroup is retained as batch-like sensitivity metadata only; no true biological replicate label is verified.",
    }
    Path("data/metadata/replicate_label_audit.json").write_text(json.dumps(metadata, indent=2) + "\n")

    lines = [
        "# Replicate Label Audit",
        "",
        f"Status: **{status}**",
        "",
        f"Audit timestamp UTC: {metadata['timestamp']}",
        "",
        "## Candidate Fields",
        "",
        df.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "The processed GEARS AnnData exposes `replicate` and `batch`, but both are uninformative in the local file. The GEO cell-identity file exposes `gemgroup`, which is suitable only as a batch-like sensitivity field and not as a verified biological replicate label. Replicate-derived BNS upper bounds therefore remain unverified.",
        "",
    ]
    Path("reports/replicate_label_audit.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
