# Norman Acquisition Report

## Status

Status: **LOCAL_ACQUISITION_COMPLETE_QC_PASS**

## Primary Source

- Original dataset accession: GSE133344
- Original source: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344
- GEARS official processed Norman URL: https://dataverse.harvard.edu/api/access/datafile/6154020
- Local target: `data/raw/norman/perturb_processed.h5ad`
- SHA256: `23ffb0fac6a847ff927cf7509d80d85052bfefbfb97610786a2dafaaefa0b6a0`

## Command-Line Access Audit

On 2026-08-12, the GEARS official Harvard Dataverse datafile endpoint returned HTTP 202 with `x-amzn-waf-action: challenge` to command-line access. This was recorded as access friction, not as a data availability failure.

## Reproducible Fallback

The LUH Seafile mirror listed in independent GEARS-format dataset documentation was reachable and was used as a fallback source:

```text
https://seafile.cloud.uni-hannover.de/d/5d6029c6eaaf410c8b01/files/?p=%2Fperturbation_data_analysis%2Fnorman%2Fperturb_processed.h5ad&dl=1
```

The final `.aria2` marker is absent and the completed file passed local checksum and AnnData load checks.

## Alternative Source Attempt

Zenodo record `14638780`, file `Norman.h5ad.gz`, was checked as a fallback. It is smaller but not the GEARS official processed file; the partial attempt was stopped because it was slower and would not satisfy GEARS reproduction as directly.

## Local Validation

- Cells: 91,205
- Genes: 5,045
- Perturbations: 284
- Controls: 7,353
- Minimum cells per perturbation: 49
- Median cells per perturbation: 272.0
- Dataset QC report: `reports/dataset_qc_report.md`
- Split integrity report: `reports/split_integrity_report.md`

Replicate and batch fields remain unverified because the processed AnnData does not expose an informative replicate label after schema normalization.
