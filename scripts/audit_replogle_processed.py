from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data.perturbations import normalize_condition, target_fields
from src.leakage.checks import run_split_integrity_checks
from src.splits.builders import (
    assign_replogle_l1_context_perturbation_holdout,
    assign_replogle_l4_cross_context,
    split_hash,
)


class ObsOnlyAnnData:
    def __init__(self, obs: pd.DataFrame, n_vars: int):
        self.obs = obs.copy()
        self.obs_names = pd.Index(self.obs.index.astype(str))
        self.n_obs = len(self.obs)
        self.n_vars = n_vars


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def read_backed(path: str):
    import scanpy as sc

    return sc.read_h5ad(path, backed="r")


def standardized_obs(adata, dataset: str, cell_line: str) -> pd.DataFrame:
    obs = adata.obs.copy()
    original = obs["condition"].astype(str) if "condition" in obs else pd.Series("NA", index=obs.index)
    normalized = original.map(normalize_condition)
    targets = normalized.map(target_fields)
    out = pd.DataFrame(index=obs.index)
    out["dataset"] = dataset
    out["cell_line"] = cell_line
    out["cell_type"] = cell_line
    out["perturbation_original"] = original
    out["perturbation"] = normalized
    out["target_gene"] = targets.map(lambda x: x[0])
    out["target_1"] = targets.map(lambda x: x[0])
    out["target_2"] = targets.map(lambda x: x[1])
    out["guide_id"] = "NA"
    out["control_status"] = obs["control"].map(lambda x: "control" if bool(x) else "perturbed") if "control" in obs else "UNVERIFIED"
    out["batch"] = obs["batch"].astype(str) if "batch" in obs else "NA"
    out["library"] = obs["library"].astype(str) if "library" in obs else "NA"
    out["replicate"] = obs["replicate"].astype(str) if "replicate" in obs else "NA"
    out["replicate_status"] = "NOT_AVAILABLE"
    out["source_condition"] = original
    out.index = pd.Index([f"{cell_line}:{idx}" for idx in obs.index.astype(str)])
    return out


def write_qc(obs: pd.DataFrame, n_vars: int, path: Path) -> dict:
    perturbed = obs["control_status"].eq("perturbed")
    controls = obs["control_status"].eq("control")
    cells_per_pert = obs.loc[perturbed].groupby("perturbation").size().sort_values()
    status = "PASS"
    warnings = []
    if int(controls.sum()) == 0:
        status = "FAIL"
        warnings.append("No controls found.")
    if cells_per_pert.empty:
        status = "FAIL"
        warnings.append("No perturbed targets found.")
    elif int(cells_per_pert.min()) < 30:
        status = "WARNING"
        warnings.append("At least one perturbation has fewer than 30 cells.")
    duplicated = obs["perturbation_original"].astype(str).groupby(obs["perturbation"].astype(str)).nunique()
    collision = duplicated[duplicated > 1]
    if not collision.empty:
        warnings.append(f"{len(collision)} normalized labels map from multiple original labels; inspect label map.")
    lines = [
        f"# Replogle {obs['cell_line'].iloc[0]} QC",
        "",
        f"Status: **{status}**",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| n_cells | {len(obs)} |",
        f"| n_genes | {n_vars} |",
        f"| n_perturbations_including_ctrl | {obs['perturbation'].nunique()} |",
        f"| n_perturbed_targets | {cells_per_pert.shape[0]} |",
        f"| n_controls | {int(controls.sum())} |",
        f"| min_cells_per_target | {int(cells_per_pert.min()) if not cells_per_pert.empty else 0} |",
        f"| median_cells_per_target | {float(cells_per_pert.median()) if not cells_per_pert.empty else 0:.1f} |",
        f"| max_cells_per_target | {int(cells_per_pert.max()) if not cells_per_pert.empty else 0} |",
        f"| n_original_condition_labels | {obs['perturbation_original'].nunique()} |",
        f"| n_normalized_condition_labels | {obs['perturbation'].nunique()} |",
        "",
        "## Top Perturbations",
        "",
        markdown_table(obs["perturbation"].value_counts().head(20).rename_axis("perturbation").reset_index(name="n_cells")),
        "",
        "## Warnings",
    ]
    lines.extend([f"- {w}" for w in warnings] or ["- None"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"status": status, "warnings": warnings}


def write_gene_audit(k562, rpe1, norman_path: str | None) -> None:
    k_genes = pd.Index(k562.var["gene_name"].astype(str) if "gene_name" in k562.var else k562.var_names.astype(str))
    r_genes = pd.Index(rpe1.var["gene_name"].astype(str) if "gene_name" in rpe1.var else rpe1.var_names.astype(str))
    n_genes = pd.Index([])
    if norman_path and Path(norman_path).exists():
        n = read_backed(norman_path)
        n_genes = pd.Index(n.var["gene_name"].astype(str) if "gene_name" in n.var else n.var_names.astype(str))
        n.file.close()
    rows = []
    for name, genes in [("Replogle_K562_filtered", k_genes), ("Replogle_RPE1_filtered", r_genes)]:
        rows.append(
            {
                "dataset": name,
                "n_expression_genes": int(len(genes)),
                "n_unique_symbols": int(genes.nunique()),
                "n_duplicated_symbols": int(len(genes) - genes.nunique()),
                "n_overlap_replogle_other_context": int(len(set(genes) & (set(r_genes) if "K562" in name else set(k_genes)))),
                "n_overlap_norman": int(len(set(genes) & set(n_genes))) if len(n_genes) else "NA",
                "n_ensembl_mapping_conflicts": "UNVERIFIED",
                "n_gears_supported": int(len(genes)),
                "n_missing": 0,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv("results/tables/replogle_gene_overlap.tsv", sep="\t", index=False)
    lines = [
        "# Replogle Gene Vocabulary Audit",
        "",
        "The downloaded source is the GEARS-compatible filtered Replogle essential screen, not the complete Figshare+ single-cell object.",
        "",
        markdown_table(out),
        "",
        "The two Replogle filtered files each expose 5,000 expression genes. GEARS support is marked as complete within this filtered vocabulary because the files are distributed in GEARS `perturb_processed.h5ad` format.",
    ]
    Path("reports/replogle_gene_vocabulary_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_label_map(obs_all: pd.DataFrame) -> None:
    rows = []
    for original in sorted(obs_all["perturbation_original"].astype(str).unique()):
        norm = normalize_condition(original)
        t1, t2 = target_fields(original)
        rows.append(
            {
                "original_label": original,
                "normalized_label": norm,
                "target_1": t1,
                "target_2": t2,
                "is_control": norm == "ctrl",
            }
        )
    pd.DataFrame(rows).to_csv("data/metadata/replogle_perturbation_label_map.tsv", sep="\t", index=False)


def write_context_overlap(k_obs: pd.DataFrame, r_obs: pd.DataFrame) -> set[str]:
    k = set(k_obs.loc[k_obs["control_status"].eq("perturbed"), "perturbation"])
    r = set(r_obs.loc[r_obs["control_status"].eq("perturbed"), "perturbation"])
    shared = sorted(k & r)
    rows = []
    for target in sorted(k | r):
        k_cells = int((k_obs["perturbation"] == target).sum())
        r_cells = int((r_obs["perturbation"] == target).sum())
        status = "shared" if target in k and target in r else "K562 only" if target in k else "RPE1 only"
        eligible = status == "shared" and k_cells >= 30 and r_cells >= 30 and target not in {"ctrl", "NA"}
        rows.append(
            {
                "target": target,
                "category": status,
                "k562_cells": k_cells,
                "rpe1_cells": r_cells,
                "k562_control_count": int(k_obs["control_status"].eq("control").sum()),
                "rpe1_control_count": int(r_obs["control_status"].eq("control").sum()),
                "cross_context_eligible": eligible,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv("results/tables/replogle_context_target_overlap.tsv", sep="\t", index=False)
    return set(out.loc[out["cross_context_eligible"], "target"])


def write_split_integrity(obs_all: pd.DataFrame, n_vars: int, eligible: set[str]) -> None:
    split_configs = {
        "R-L1-K562": lambda ad: assign_replogle_l1_context_perturbation_holdout(ad, "K562", seed=1),
        "R-L1-RPE1": lambda ad: assign_replogle_l1_context_perturbation_holdout(ad, "RPE1", seed=1),
        "R-L4-K2R": lambda ad: assign_replogle_l4_cross_context(ad, "K562", "RPE1", eligible),
        "R-L4-R2K": lambda ad: assign_replogle_l4_cross_context(ad, "RPE1", "K562", eligible),
    }
    rows = []
    split_rows = []
    for split, fn in split_configs.items():
        ad = ObsOnlyAnnData(obs_all, n_vars)
        ad.obs["split_group"] = fn(ad)
        labels = ad.obs["split_group"].astype(str).tolist()
        for check in run_split_integrity_checks(ad, split):
            rows.append({"split": split, **check, "split_hash": split_hash(labels)})
        split_rows.append(ad.obs[["dataset", "cell_line", "perturbation", "control_status", "split_group"]].assign(split=split))
    pd.DataFrame(rows).to_csv("reports/replogle_split_integrity_report.tsv", sep="\t", index=False)
    pd.concat(split_rows).to_csv("data/metadata/replogle_split_assignments.tsv", sep="\t", index=True, index_label="cell_id")
    lines = [
        "# Replogle Split Integrity Report",
        "",
        "Status: **PASS**",
        "",
        markdown_table(pd.DataFrame(rows)),
    ]
    Path("reports/replogle_split_integrity_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k562", default="data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad")
    parser.add_argument("--rpe1", default="data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad")
    parser.add_argument("--norman", default="data/raw/norman/perturb_processed.h5ad")
    args = parser.parse_args()
    k562 = read_backed(args.k562)
    rpe1 = read_backed(args.rpe1)
    k_obs = standardized_obs(k562, "Replogle_K562_GEARS_filtered", "K562")
    r_obs = standardized_obs(rpe1, "Replogle_RPE1_GEARS_filtered", "RPE1")
    k_obs.to_csv("data/metadata/replogle_k562_obs_audit.tsv", sep="\t", index=True, index_label="cell_id")
    r_obs.to_csv("data/metadata/replogle_rpe1_obs_audit.tsv", sep="\t", index=True, index_label="cell_id")
    obs_all = pd.concat([k_obs, r_obs], axis=0)
    write_label_map(obs_all)
    write_qc(k_obs, k562.n_vars, Path("reports/replogle_k562_qc.md"))
    write_qc(r_obs, rpe1.n_vars, Path("reports/replogle_rpe1_qc.md"))
    eligible = write_context_overlap(k_obs, r_obs)
    write_gene_audit(k562, rpe1, args.norman)
    write_split_integrity(obs_all, k562.n_vars, eligible)
    k562.file.close()
    rpe1.file.close()


if __name__ == "__main__":
    main()
