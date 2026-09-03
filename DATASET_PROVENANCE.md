# Dataset Provenance

## Norman et al. K562 CRISPRa

```yaml
dataset_name: Norman et al. K562 CRISPRa Perturb-seq
accession: GSE133344
source_url: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344
gears_official_processed_url: https://dataverse.harvard.edu/api/access/datafile/6154020
processed_mirror_url: https://seafile.cloud.uni-hannover.de/d/5d6029c6eaaf410c8b01/files/?p=%2Fperturbation_data_analysis%2Fnorman%2Fperturb_processed.h5ad&dl=1
publication: Exploring genetic interaction manifolds constructed from rich single-cell phenotypes
publication_date: 2019-08-23
public_release_date: 2019-06-26 GEO submission; 2020-04-23 GEO last update
organism: Homo sapiens
cell_type: K562
cell_line: K562
perturbation_type: CRISPRa
perturbation_target: gene activation, single and combinatorial
single_or_combo: both
n_cells: 91205
n_genes: 5045
n_perturbations: 284
n_controls: 7353
local_sha256: 23ffb0fac6a847ff927cf7509d80d85052bfefbfb97610786a2dafaaefa0b6a0
replicates: UNVERIFIED
batch_information: PARTIAL_LINK_PASS via GEO cell identities `gemgroup` for 88,843/91,205 GEARS cells
guide_identity_metadata: PARTIAL_LINK_PASS via GSE133344_filtered_cell_identities.csv.gz; unordered condition concordance 0.9916 among matched cells
donor_information: not_applicable_cell_line
protocol: Perturb-seq pooled CRISPR activation with scRNA-seq
raw_data_available: true
processed_data_available: true via GEARS/Dataverse processed file
license: UNVERIFIED
preprocessing_description: GEARS processed version; local audit confirms 91,205 cells, 5,045 genes, required perturbation/control fields after schema normalization, and sparse AnnData matrix. Exact upstream preprocessing remains inherited from GEARS processed file provenance.
known_model_pretraining_overlap: GEARS uses this as training/evaluation data in its original benchmark; foundation-model overlap unknown.
temporal_status: pre-2023 model benchmark dataset; not temporal-clean for later foundation models without corpus evidence.
notes: Do not use GEARS-provided splits as final audit splits without independent leakage diagnostics. Official Dataverse datafile URL returned AWS WAF challenge to command-line access on 2026-08-12; LUH Seafile mirror was used as a reproducible fallback and the local checksum is recorded above. GEO guide metadata can support batch-like sensitivity analyses through `gemgroup`, but the link is partial and must be reported.
```

## Replogle K562 CRISPRi

```yaml
dataset_name: Replogle K562 CRISPRi
accession: PRJNA831566; 10.25452/figshare.plus.20029387
source_url: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA831566; https://doi.org/10.25452/figshare.plus.20029387
publication: Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq
publication_date: 2022-07-07
public_release_date: 2022-04-24 BioProject registration; 2022-06 Figshare+ processed/manifest deposits
organism: Homo sapiens
cell_type: K562
cell_line: K562
perturbation_type: CRISPRi
CRISPR_mode: CRISPR interference
n_cells: 162751
n_genes: 5000
n_perturbations: 1093 including ctrl; 1092 perturbed targets
n_controls: 10691
n_guides: NOT_AVAILABLE_IN_GEARS_FILTERED_H5AD
replicates: NOT_AVAILABLE_FROM_SRA_RUNINFO; BNS_STATUS_UNVERIFIED
batch_structure: SRA library/lane/sample-index/pool fields available for raw sequencing provenance only; filtered h5ad obs has no replicate/batch/guide fields
source: GEARS-compatible Harvard Dataverse filtered essential screen datafile 7458695 used for executable audit; Figshare+ complete processed h5ad/GWPS remains primary complete-data source but command-line download is blocked; NCBI SRA PRJNA831566 selected as secondary validation source
raw_available: true
processed_available: true_gears_filtered_essential_downloaded; complete_figshare_processed_download_blocked_by_HTTP_403_on_2026_08_23
license: CC0 reported by Figshare+ page snippets; verify in downloaded metadata before redistribution
normalization: inherited from GEARS filtered `perturb_processed.h5ad`; exact upstream normalization not independently reconstructed
gene_id_type: gene symbols in `var.gene_name`; 5000 expression columns, 4999 unique symbols, 1 duplicate symbol
control_definition: `condition == ctrl` and `control == 1`
status: GEARS_FILTERED_H5AD_QC_SPLITS_BASELINES_COMPLETE_BNS_UNVERIFIED
local_files:
  zip: data/raw/replogle/replogle_k562_essential.zip
  h5ad: data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad
  sha256_zip: e769c89aa876061fdb3ac02a8de274f19a741a4f95decf14a52fd621d1eea319
  sha256_h5ad: 550fde89ac85c258c9fd517638fe34fb42c0e748c9305fe6355761a2bb754170
notes: SRA runinfo contains K562_day_6_essential_scale, K562_day_8_genome_scale, K562_day_8_ultima, and RPE1_day_7_essential_scale. The current executable audit uses the filtered K562 essential screen exposed by GEARS/Dataverse, not the complete genome-scale object. Minimum cells per target is 15, so QC is WARNING rather than PASS.
```

## Replogle RPE1 CRISPRi

```yaml
dataset_name: Replogle RPE1 CRISPRi
accession: PRJNA831566; 10.25452/figshare.plus.20029387
source_url: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA831566; https://doi.org/10.25452/figshare.plus.20029387
publication: Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq
publication_date: 2022-07-07
public_release_date: 2022-04-24 BioProject registration; 2022-06 Figshare+ processed/manifest deposits
organism: Homo sapiens
cell_type: RPE1
cell_line: RPE1
perturbation_type: CRISPRi
CRISPR_mode: CRISPR interference
n_cells: 162733
n_genes: 5000
n_perturbations: 1544 including ctrl; 1543 perturbed targets
n_controls: 11485
n_guides: NOT_AVAILABLE_IN_GEARS_FILTERED_H5AD
replicates: NOT_AVAILABLE_FROM_SRA_RUNINFO; BNS_STATUS_UNVERIFIED
batch_structure: SRA library/lane/sample-index fields available for raw sequencing provenance only; filtered h5ad obs has no replicate/batch/guide fields
source: GEARS-compatible Harvard Dataverse filtered essential screen datafile 7458694 used for executable audit; Figshare+ complete processed h5ad/GWPS remains primary complete-data source but command-line download is blocked; NCBI SRA PRJNA831566 selected as secondary validation source
raw_available: true
processed_available: true_gears_filtered_essential_downloaded; complete_figshare_processed_download_blocked_by_HTTP_403_on_2026_08_23
license: CC0 reported by Figshare+ page snippets; verify in downloaded metadata before redistribution
normalization: inherited from GEARS filtered `perturb_processed.h5ad`; exact upstream normalization not independently reconstructed
gene_id_type: gene symbols in `var.gene_name`; 5000 expression columns, 5000 unique symbols
control_definition: `condition == ctrl` and `control == 1`
status: GEARS_FILTERED_H5AD_QC_SPLITS_BASELINES_COMPLETE_BNS_UNVERIFIED
local_files:
  zip: data/raw/replogle/replogle_rpe1_essential.zip
  h5ad: data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad
  sha256_zip: 0b97d50a9be1ecbd8837e8425456605e4ed6121b0c7738938f1318948cb78790
  sha256_h5ad: cc3e13da13ecd3cf7fb027b8261514a2bdcfab16fe47fc685b2714f79781afba
notes: SRA runinfo exposes RPE1_day_7_essential_scale. The current executable audit uses the filtered RPE1 essential screen exposed by GEARS/Dataverse, not the complete Figshare+ object. Minimum cells per target is 13, so QC is WARNING rather than PASS.
```

## Arc Virtual Cell Challenge H1 hESC

Registered for external or temporally cleaner evaluation. Status: REGISTERED_NOT_STARTED.
