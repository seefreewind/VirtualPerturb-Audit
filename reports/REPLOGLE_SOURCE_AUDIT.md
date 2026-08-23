# Replogle Source Audit

Audit date: 2026-08-23

## Executive Selection

`PRIMARY_SOURCE = Figshare+ processed Perturb-seq datasets / GWPS processed browser, linked from Replogle et al. 2022`

`SECONDARY_VALIDATION_SOURCE = NCBI SRA BioProject PRJNA831566 run manifest`

The primary source is selected because the paper states that processed single-cell and pseudobulk populations are available through the GWPS browser and the Figshare+ processed-data deposit. The secondary source is selected because raw sequencing data are deposited in SRA under BioProject `PRJNA831566`.

Command-line access to Figshare+ returned HTTP 403 during this audit, so processed `.h5ad` files have not yet been downloaded. The SRA run manifest was downloaded successfully from NCBI and is used only for provenance and raw-library metadata audit; it is not sufficient for model training, per-cell perturbation labels, target overlap, or baseline evaluation.

## Candidate Resources

```yaml
publication:
  resource_name: Replogle et al. Cell 2022
  url: https://doi.org/10.1016/j.cell.2022.05.013
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
  url: https://gwps.wi.mit.edu/
  accession: not_applicable
  official_or_mirror: official_processed_browser
  linked_publication: https://doi.org/10.1016/j.cell.2022.05.013
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
  url: https://doi.org/10.25452/figshare.plus.20029387
  accession: 10.25452/figshare.plus.20029387
  official_or_mirror: paper_linked_archive
  linked_publication: https://doi.org/10.1016/j.cell.2022.05.013
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
  url: https://doi.org/10.25452/figshare.plus.20022944
  accession: 10.25452/figshare.plus.20022944
  official_or_mirror: paper_linked_archive
  linked_publication: https://doi.org/10.1016/j.cell.2022.05.013
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
  url: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA831566
  accession: PRJNA831566
  official_or_mirror: official_raw_archive
  linked_publication: https://doi.org/10.1016/j.cell.2022.05.013
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

| SampleName                 | library_modality   |   n_runs |   n_experiments |   n_libraries |   n_lanes |   n_sample_indices |   n_biosamples |   total_size_mb |
|:---------------------------|:-------------------|---------:|----------------:|--------------:|----------:|-------------------:|---------------:|----------------:|
| K562_day_6_essential_scale | UNKNOWN            |       48 |              48 |            48 |         1 |                  1 |              1 |          475519 |
| K562_day_6_essential_scale | mRNA               |      384 |             384 |           384 |        48 |                 72 |              1 |          685909 |
| K562_day_6_essential_scale | sgRNA              |      192 |             192 |           192 |        48 |                 48 |              1 |           50124 |
| K562_day_8_genome_scale    | UNKNOWN            |      273 |             273 |           273 |         1 |                  1 |              1 |         2715794 |
| K562_day_8_genome_scale    | mRNA               |     2296 |            2296 |          2296 |         1 |                 96 |              1 |         4495797 |
| K562_day_8_genome_scale    | sgRNA              |     2296 |            2296 |          2296 |         1 |                 96 |              1 |          367595 |
| K562_day_8_ultima          | UNKNOWN            |      546 |             546 |           546 |         1 |                  2 |              1 |         9930775 |
| RPE1_day_7_essential_scale | UNKNOWN            |       56 |              56 |            56 |         1 |                  1 |              1 |          517135 |
| RPE1_day_7_essential_scale | mRNA               |      896 |             896 |           896 |         1 |                112 |              1 |          724751 |
| RPE1_day_7_essential_scale | sgRNA              |      896 |             896 |           896 |         1 |                112 |              1 |          116870 |

## Current Access Result

- SRA runinfo: downloaded successfully to `data/raw/replogle/PRJNA831566_sra_runinfo.csv`.
- Figshare+ API and whole-article download endpoints: HTTP 403 from command line on 2026-08-23.
- GWPS Dash layout: accessible and confirms an official processed browser, but it is not a training-ready matrix export.

## Immediate Consequence

The project can proceed through source provenance and SRA-level library audit. It cannot legally proceed to per-cell QC, target overlap, split design, baselines, or GEARS until the processed h5ad objects or an equivalent official expression/metadata matrix are downloaded.
