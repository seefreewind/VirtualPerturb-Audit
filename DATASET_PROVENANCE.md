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

Registered for later phases. Public processed AnnData files are reported through Figshare+ for Replogle et al. 2022, DOI 10.1016/j.cell.2022.05.013. Status: REGISTERED_NOT_STARTED.

## Replogle RPE1 CRISPRi

Registered for later phases. Status: REGISTERED_NOT_STARTED.

## Arc Virtual Cell Challenge H1 hESC

Registered for external or temporally cleaner evaluation. Status: REGISTERED_NOT_STARTED.
