from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data.loaders import normalize_norman_gears_schema, read_h5ad


HGNC_URL = "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt"
HGNC_LOCAL = Path("data/interim/hgnc_complete_set.txt")
MAPPING_OUT = Path("data/metadata/hgnc_perturbation_gene_groups.csv")
PROVENANCE_OUT = Path("data/metadata/hgnc_perturbation_gene_groups_provenance.json")


def perturbation_components(perturbation: str) -> list[str]:
    return [part for part in str(perturbation).split("+") if part and part != "ctrl"]


def collect_perturbation_genes() -> list[str]:
    genes = set()
    h5ad = Path("data/raw/norman/perturb_processed.h5ad")
    if h5ad.exists():
        adata = normalize_norman_gears_schema(read_h5ad(h5ad))
        perturbations = adata.obs["perturbation"].astype(str).unique()
    else:
        retrieval = pd.read_csv("results/pilot/perturbation_retrieval.csv")
        perturbations = pd.concat([retrieval["perturbation"], retrieval["top_match"].dropna()]).astype(str).unique()
    for pert in perturbations:
        genes.update(perturbation_components(pert))
    return sorted(genes)


def ensure_hgnc_complete() -> Path:
    HGNC_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    if not HGNC_LOCAL.exists():
        with urllib.request.urlopen(HGNC_URL, timeout=120) as response:
            HGNC_LOCAL.write_bytes(response.read())
    return HGNC_LOCAL


def split_field(value: str) -> list[str]:
    if pd.isna(value) or str(value).strip() == "":
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def build_mapping() -> pd.DataFrame:
    genes = collect_perturbation_genes()
    hgnc = pd.read_csv(ensure_hgnc_complete(), sep="\t", dtype=str)
    hgnc = hgnc[hgnc["symbol"].isin(genes)].copy()
    rows = []
    for _, row in hgnc.iterrows():
        group_names = split_field(row.get("gene_group", ""))
        group_ids = split_field(row.get("gene_group_id", ""))
        if not group_names:
            rows.append({
                "symbol": row["symbol"],
                "approved_name": row.get("name", ""),
                "hgnc_id": row.get("hgnc_id", ""),
                "gene_group": "UNANNOTATED",
                "gene_group_id": "UNANNOTATED",
                "annotation_status": "UNANNOTATED_HGNC_GROUP",
            })
            continue
        for i, group_name in enumerate(group_names):
            rows.append({
                "symbol": row["symbol"],
                "approved_name": row.get("name", ""),
                "hgnc_id": row.get("hgnc_id", ""),
                "gene_group": group_name,
                "gene_group_id": group_ids[i] if i < len(group_ids) else "",
                "annotation_status": "ANNOTATED_HGNC_GROUP",
            })
    mapping = pd.DataFrame(rows)
    missing = sorted(set(genes) - set(hgnc["symbol"].astype(str)))
    for gene in missing:
        mapping = pd.concat(
            [
                mapping,
                pd.DataFrame(
                    [
                        {
                            "symbol": gene,
                            "approved_name": "",
                            "hgnc_id": "",
                            "gene_group": "NOT_FOUND_IN_HGNC",
                            "gene_group_id": "NOT_FOUND_IN_HGNC",
                            "annotation_status": "NOT_FOUND_IN_HGNC",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return mapping.sort_values(["symbol", "gene_group"]).reset_index(drop=True)


def group_lookup(mapping: pd.DataFrame) -> dict[str, set[str]]:
    usable = mapping[mapping["annotation_status"].eq("ANNOTATED_HGNC_GROUP")]
    return usable.groupby("symbol")["gene_group"].apply(lambda s: set(s.astype(str))).to_dict()


def annotate_confusion(mapping: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    retrieval = pd.read_csv("results/pilot/perturbation_retrieval.csv")
    lookup = group_lookup(mapping)
    rows = []
    for _, row in retrieval.iterrows():
        top_match = row.get("top_match")
        if pd.isna(top_match) or top_match == "UNINFORMATIVE_PREDICTION":
            continue
        true_genes = perturbation_components(row["perturbation"])
        pred_genes = perturbation_components(top_match)
        true_groups = set().union(*(lookup.get(gene, set()) for gene in true_genes)) if true_genes else set()
        pred_groups = set().union(*(lookup.get(gene, set()) for gene in pred_genes)) if pred_genes else set()
        shared = sorted(true_groups & pred_groups)
        rows.append({
            **row.to_dict(),
            "true_genes": "|".join(true_genes),
            "top_match_genes": "|".join(pred_genes),
            "true_gene_groups": "|".join(sorted(true_groups)),
            "top_match_gene_groups": "|".join(sorted(pred_groups)),
            "shared_gene_groups": "|".join(shared),
            "n_shared_gene_groups": len(shared),
            "has_shared_gene_group": len(shared) > 0,
            "same_gene_set": set(true_genes) == set(pred_genes),
        })
    annotated = pd.DataFrame(rows)
    summary_rows = []
    if not annotated.empty:
        for (model, split), sub in annotated.groupby(["model", "split"]):
            confused = sub[sub["is_confused"].astype(str).str.lower().eq("true")]
            denominator = len(confused)
            shared = int(confused["has_shared_gene_group"].sum()) if denominator else 0
            summary_rows.append({
                "dataset": "Norman2019_GEARS_processed_mirror",
                "model": model,
                "split": split,
                "n_ranked_perturbations": len(sub),
                "n_confusions": denominator,
                "n_confusions_with_shared_gene_group": shared,
                "confusion_shared_gene_group_fraction": shared / denominator if denominator else float("nan"),
                "annotation_source": "HGNC gene_group",
                "status": "COMPLETED_HGNC_FAMILY_CONFUSION_AUDIT",
            })
    return annotated, pd.DataFrame(summary_rows)


def l3_candidates(mapping: pd.DataFrame) -> pd.DataFrame:
    annotated = mapping[mapping["annotation_status"].eq("ANNOTATED_HGNC_GROUP")]
    rows = []
    for (group_id, group), sub in annotated.groupby(["gene_group_id", "gene_group"]):
        genes = sorted(sub["symbol"].astype(str).unique())
        if len(genes) >= 2:
            rows.append({
                "gene_group_id": group_id,
                "gene_group": group,
                "n_norman_perturbation_genes": len(genes),
                "norman_perturbation_genes": "|".join(genes),
                "candidate_use": "L3 gene-family/pathway holdout",
                "status": "CANDIDATE_REQUIRES_SPLIT_LOCK",
            })
    return pd.DataFrame(rows).sort_values(["n_norman_perturbation_genes", "gene_group"], ascending=[False, True])


def main():
    Path("results/pilot").mkdir(parents=True, exist_ok=True)
    Path("data/metadata").mkdir(parents=True, exist_ok=True)
    mapping = build_mapping()
    mapping.to_csv(MAPPING_OUT, index=False)
    annotated, summary = annotate_confusion(mapping)
    annotated.to_csv("results/pilot/gene_family_confusion.csv", index=False)
    summary.to_csv("results/pilot/gene_family_confusion_summary.csv", index=False)
    l3_candidates(mapping).to_csv("results/pilot/l3_gene_family_holdout_candidates.csv", index=False)
    PROVENANCE_OUT.write_text(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "HGNC complete approved dataset",
                "source_url": HGNC_URL,
                "local_interim_file": str(HGNC_LOCAL),
                "derived_mapping": str(MAPPING_OUT),
                "notes": "MSigDB pathway annotations were not used because direct downloads require registration; HGNC gene_group is public and reproducible.",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
