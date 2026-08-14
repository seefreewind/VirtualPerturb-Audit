# Norman GEO Metadata Link Audit

Status: **PARTIAL_LINK_PASS**

Audit timestamp UTC: 2026-08-14T06:47:57.399569+00:00
GEO identities SHA256: `daf30337e7f6f07096d57e0d81db784bef00c87bd1fc927f018792c2f7af81e4`

## Match Summary

- GEARS AnnData cells: 91205
- GEO identity rows: 111445
- Unique GEO barcodes: 111445
- Matched GEARS cells: 88843
- Unmatched GEARS cells: 2362
- Matched fraction of GEARS cells: 0.9741
- Exact condition concordance: 0.8288
- Unordered condition concordance: 0.9916
- gemgroup count: 8

## Interpretation

The GEO cell-identity file provides guide identity and `gemgroup`, enabling a batch-like metadata audit for most GEARS cells. The link is partial because a subset of GEARS cells do not have exact barcode matches in the GEO identities file. Use `gemgroup` for sensitivity and null-envelope analyses only with explicit partial-link reporting.

## Generated Side Tables

- `reports/norman_geo_gemgroup_counts.tsv`
- `reports/norman_geo_ctrl_by_gemgroup.tsv`
