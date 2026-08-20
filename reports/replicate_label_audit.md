# Replicate Label Audit

Status: **TRUE_REPLICATE_NOT_FOUND**

Audit timestamp UTC: 2026-08-14T07:31:38.308221+00:00

## Candidate Fields

| source              | column    |   n_rows |   n_unique | top_values                                                      | has_multiple_informative_values   | interpretation            |
|:--------------------|:----------|---------:|-----------:|:----------------------------------------------------------------|:----------------------------------|:--------------------------|
| GEARS_AnnData_obs   | donor     |    91205 |          1 | not_applicable_cell_line:91205                                  | False                             | TRUE_REPLICATE_UNVERIFIED |
| GEARS_AnnData_obs   | batch     |    91205 |          1 | UNVERIFIED:91205                                                | False                             | TRUE_REPLICATE_UNVERIFIED |
| GEARS_AnnData_obs   | replicate |    91205 |          1 | UNVERIFIED:91205                                                | False                             | TRUE_REPLICATE_UNVERIFIED |
| GEO_cell_identities | gemgroup  |   111445 |          8 | 1:15033;8:14266;3:14246;7:14137;6:13792;2:13787;5:13101;4:13083 | True                              | BATCH_LIKE_CANDIDATE      |

## Interpretation

The processed GEARS AnnData exposes `replicate` and `batch`, but both are uninformative in the local file. The GEO cell-identity file exposes `gemgroup`, which is suitable only as a batch-like sensitivity field and not as a verified biological replicate label. Replicate-derived BNS upper bounds therefore remain unverified.
