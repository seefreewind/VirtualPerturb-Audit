from __future__ import annotations

import argparse
import hashlib
from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_URLS = {
    "publication": "https://doi.org/10.1016/j.cell.2022.05.013",
    "pubmed": "https://pubmed.ncbi.nlm.nih.gov/35688146/",
    "bioproject": "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA831566",
    "sra_runinfo": "https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/runinfo?acc=PRJNA831566",
    "gwps": "https://gwps.wi.mit.edu/",
    "figshare_processed": "https://doi.org/10.25452/figshare.plus.20029387",
    "figshare_manifest": "https://doi.org/10.25452/figshare.plus.20022944",
    "figshare_mtx": "https://doi.org/10.25452/figshare.plus.20127869",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_library(name: str) -> dict[str, str]:
    text = str(name)
    parts = text.split("_")
    modality = "sgRNA" if "sgRNA" in parts else "mRNA" if "mRNA" in parts else "UNKNOWN"
    lane = "UNKNOWN"
    sample_index = "UNKNOWN"
    pool = "UNKNOWN"
    for i, part in enumerate(parts):
        if part == "lane" and i + 1 < len(parts):
            lane = parts[i + 1]
        if part.startswith("S") and part[1:].isdigit():
            sample_index = part
        if part.startswith("p") and part[1:].isdigit():
            pool = part
    return {"library_modality": modality, "lane": lane, "sample_index": sample_index, "pool": pool}


def summarize_runinfo(runinfo: Path) -> pd.DataFrame:
    df = pd.read_csv(runinfo)
    parsed = pd.DataFrame([classify_library(x) for x in df["LibraryName"].fillna("UNKNOWN")])
    merged = pd.concat([df, parsed], axis=1)
    merged.to_csv("data/metadata/replogle_sra_runinfo_parsed.tsv", sep="\t", index=False)
    summary = (
        merged.groupby(["SampleName", "library_modality"], dropna=False)
        .agg(
            n_runs=("Run", "count"),
            n_experiments=("Experiment", "nunique"),
            n_libraries=("LibraryName", "nunique"),
            n_lanes=("lane", "nunique"),
            n_sample_indices=("sample_index", "nunique"),
            n_biosamples=("BioSample", "nunique"),
            total_size_mb=("size_MB", "sum"),
        )
        .reset_index()
    )
    summary.to_csv("data/metadata/replogle_sra_runinfo_summary.tsv", sep="\t", index=False)
    return summary


def source_audit_md(summary: pd.DataFrame) -> str:
    today = date.today().isoformat()
    summary_table = summary.to_markdown(index=False)
    return f"""# Replogle Source Audit

Audit date: {today}

## Executive Selection

`PRIMARY_SOURCE = Figshare+ processed Perturb-seq datasets / GWPS processed browser, linked from Replogle et al. 2022`

`SECONDARY_VALIDATION_SOURCE = NCBI SRA BioProject PRJNA831566 run manifest`

The primary source is selected because the paper states that processed single-cell and pseudobulk populations are available through the GWPS browser and the Figshare+ processed-data deposit. The secondary source is selected because raw sequencing data are deposited in SRA under BioProject `PRJNA831566`.

Command-line access to Figshare+ returned HTTP 403 during this audit, so processed `.h5ad` files have not yet been downloaded. The SRA run manifest was downloaded successfully from NCBI and is used only for provenance and raw-library metadata audit; it is not sufficient for model training, per-cell perturbation labels, target overlap, or baseline evaluation.

## Candidate Resources

```yaml
publication:
  resource_name: Replogle et al. Cell 2022
  url: {PROJECT_URLS['publication']}
  accession: PMID 35688146
  official_or_mirror: official_publication
  linked_publication: Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq
  publication_year: 2022
  downloadable: no
  format: article
  contains_k562: true
  contains_rpe1: true
  contains_raw_counts: no
  contains_processed_expression: no
  contains_perturbation_labels: methods_only
  contains_guide_labels: methods_only
  contains_replication_metadata: methods_only
  license: publisher_article
  selected: evidence_source
  reason: Defines the biological system, experiments, and official deposited-data links.

gwps_browser:
  resource_name: Genome-Wide Perturb-Seq browser
  url: {PROJECT_URLS['gwps']}
  accession: not_applicable
  official_or_mirror: official_processed_browser
  linked_publication: {PROJECT_URLS['publication']}
  publication_year: 2022
  downloadable: partially
  format: interactive Dash browser
  contains_k562: true
  contains_rpe1: true
  contains_raw_counts: no
  contains_processed_expression: true
  contains_perturbation_labels: true
  contains_guide_labels: likely
  contains_replication_metadata: unverified
  license: unverified
  selected: primary_evidence_source
  reason: Paper-linked official browser for processed single-cell and pseudobulk populations.

figshare_processed:
  resource_name: Replogle et al. 2022 processed Perturb-seq datasets
  url: {PROJECT_URLS['figshare_processed']}
  accession: 10.25452/figshare.plus.20029387
  official_or_mirror: paper_linked_archive
  linked_publication: {PROJECT_URLS['publication']}
  publication_year: 2022
  downloadable: yes_but_command_line_403_on_2026_08_23
  format: h5ad
  contains_k562: true
  contains_rpe1: true
  contains_raw_counts: true
  contains_processed_expression: true
  contains_perturbation_labels: true
  contains_guide_labels: true
  contains_replication_metadata: unverified_until_h5ad_obs_audit
  license: CC0 reported by Figshare+ page snippets
  selected: primary_download_target
  reason: Official processed AnnData deposit with K562 and RPE1 data.

figshare_manifest:
  resource_name: Replogle et al. 2022 SRA and GEO file manifest
  url: {PROJECT_URLS['figshare_manifest']}
  accession: 10.25452/figshare.plus.20022944
  official_or_mirror: paper_linked_archive
  linked_publication: {PROJECT_URLS['publication']}
  publication_year: 2022
  downloadable: yes_but_command_line_403_on_2026_08_23
  format: csv_manifest
  contains_k562: true
  contains_rpe1: true
  contains_raw_counts: raw_fastq_mapping
  contains_processed_expression: no
  contains_perturbation_labels: no
  contains_guide_labels: no
  contains_replication_metadata: library_level_only
  license: CC0 reported by Figshare+ page snippets
  selected: metadata_target_when_accessible
  reason: Paper-linked file manifest mapping libraries to SRA/GEO raw files.

ncbi_sra:
  resource_name: NCBI SRA BioProject PRJNA831566
  url: {PROJECT_URLS['bioproject']}
  accession: PRJNA831566
  official_or_mirror: official_raw_archive
  linked_publication: {PROJECT_URLS['publication']}
  publication_year: 2022
  downloadable: yes
  format: SRA runinfo csv / raw sequence reads
  contains_k562: true
  contains_rpe1: true
  contains_raw_counts: raw_reads
  contains_processed_expression: no
  contains_perturbation_labels: no_per_cell_label_in_runinfo
  contains_guide_labels: library_name_modality_only
  contains_replication_metadata: library_lane_biosample_only
  license: public
  selected: secondary_validation_source
  reason: Official raw sequencing archive; runinfo was downloaded successfully.
```

## Downloaded Metadata Summary

{summary_table}

## Current Access Result

- SRA runinfo: downloaded successfully to `data/raw/replogle/PRJNA831566_sra_runinfo.csv`.
- Figshare+ API and whole-article download endpoints: HTTP 403 from command line on 2026-08-23.
- GWPS Dash layout: accessible and confirms an official processed browser, but it is not a training-ready matrix export.

## Immediate Consequence

The project can proceed through source provenance and SRA-level library audit. It cannot legally proceed to per-cell QC, target overlap, split design, baselines, or GEARS until the processed h5ad objects or an equivalent official expression/metadata matrix are downloaded.
"""


def replicate_audit(runinfo: Path) -> tuple[pd.DataFrame, str]:
    df = pd.read_csv(runinfo)
    parsed = pd.DataFrame([classify_library(x) for x in df["LibraryName"].fillna("UNKNOWN")])
    df = pd.concat([df, parsed], axis=1)
    candidates = [
        "BioProject",
        "SampleName",
        "BioSample",
        "Sample",
        "Experiment",
        "LibraryName",
        "library_modality",
        "lane",
        "sample_index",
        "pool",
        "Run",
        "Submission",
        "CenterName",
        "Model",
        "Platform",
    ]
    rows = []
    for field in candidates:
        if field not in df:
            continue
        vc = df[field].fillna("NA").astype(str).value_counts()
        top = "; ".join([f"{k}:{v}" for k, v in vc.head(8).items()])
        meaning = {
            "BioProject": "NCBI project accession, shared by all Replogle raw runs.",
            "SampleName": "SRA sample-level experiment label: K562/RPE1 context and day/library class.",
            "BioSample": "NCBI BioSample identifier; one BioSample per broad dataset in runinfo.",
            "Sample": "SRA sample identifier; one SRA sample per broad dataset in runinfo.",
            "Experiment": "SRA experiment accession; sequencing experiment/run-level metadata.",
            "LibraryName": "Sequencing library name encoding day/context/modality/lane/sample index.",
            "library_modality": "Parsed mRNA/sgRNA modality from LibraryName.",
            "lane": "Parsed sequencing lane or library shard from LibraryName.",
            "sample_index": "Parsed sample index token from LibraryName.",
            "pool": "Parsed pool token such as p1/p2/p3 for KD8 genome-scale libraries.",
            "Run": "SRA run accession.",
            "Submission": "SRA submission accession.",
            "CenterName": "Submitting center.",
            "Model": "Sequencer model.",
            "Platform": "Sequencing platform.",
        }.get(field, "SRA metadata field.")
        biological = "no"
        technical = "yes" if field in {"Experiment", "LibraryName", "Run", "lane", "sample_index", "pool"} else "no"
        batch_like = "yes" if field in {"Experiment", "LibraryName", "Run", "lane", "sample_index", "pool", "Submission"} else "no"
        usable = "no"
        confidence = "HIGH" if field in {"SampleName", "BioSample", "LibraryName", "lane", "Run"} else "MODERATE"
        evidence = "SRA runinfo only; no source evidence that the levels are independent biological realizations of the same perturbation/context."
        if field in {"SampleName", "BioSample", "Sample"}:
            technical = "no"
            batch_like = "context_or_dataset_label"
        rows.append(
            {
                "field": field,
                "unique_values": int(vc.shape[0]),
                "distribution": top,
                "meaning_from_source": meaning,
                "biological_replication?": biological,
                "technical_replication?": technical,
                "batch_like?": batch_like,
                "usable_for_upper_bound?": usable,
                "confidence": confidence,
                "evidence": evidence,
            }
        )
    audit = pd.DataFrame(rows)
    md = f"""# Replogle Replicate Label Audit

Audit date: {date.today().isoformat()}

## Status

`REPLICATE_STATUS = NOT_AVAILABLE`

`BNS_STATUS = UNVERIFIED`

## Interpretation

The downloaded SRA run manifest exposes dataset/context labels, BioSample identifiers, run accessions, library names, sequencing lanes, sample indices, modality labels, and pool tokens. These fields are useful for provenance and batch-like sensitivity planning, but none is documented in the downloaded metadata as an independent biological experimental realization of the same perturbation/context.

This audit therefore does not validate a biological replicate-derived empirical upper bound. The decision can be revisited only after the processed h5ad `obs` fields and the original Figshare manifest/README are available and directly inspected.

## Candidate Fields

{audit.to_markdown(index=False)}

## Rule Applied

Multiple levels in `lane`, `library`, `Run`, `Experiment`, `BioSample`, or `SampleName` were not treated as biological replicates. They remain technical, batch-like, or dataset/context labels unless the paper methods or metadata dictionary explicitly states independent biological replication.
"""
    return audit, md


def write_checksums(paths: list[Path]) -> None:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        rows.append(
            {
                "filename": str(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "download_url": PROJECT_URLS["sra_runinfo"] if "runinfo" in path.name else "UNVERIFIED",
                "download_date": date.today().isoformat(),
            }
        )
    pd.DataFrame(rows).to_csv("data/metadata/replogle_checksums.tsv", sep="\t", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runinfo", default="data/raw/replogle/PRJNA831566_sra_runinfo.csv")
    args = parser.parse_args()
    runinfo = Path(args.runinfo)
    if not runinfo.exists():
        raise FileNotFoundError(runinfo)
    Path("reports").mkdir(exist_ok=True)
    Path("data/metadata").mkdir(parents=True, exist_ok=True)
    summary = summarize_runinfo(runinfo)
    write_checksums([runinfo])
    Path("reports/REPLOGLE_SOURCE_AUDIT.md").write_text(source_audit_md(summary), encoding="utf-8")
    audit, md = replicate_audit(runinfo)
    audit.to_csv("reports/replogle_replicate_label_audit.tsv", sep="\t", index=False)
    Path("reports/replogle_replicate_label_audit.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
