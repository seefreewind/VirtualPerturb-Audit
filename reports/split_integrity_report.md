# Split Integrity Report

Status: **PASS**

Audit timestamp UTC: 2026-08-14T07:00:23.235669+00:00
Dataset SHA256: `23ffb0fac6a847ff927cf7509d80d85052bfefbfb97610786a2dafaaefa0b6a0`

| split   | check                             | status   | message                                                              | split_hash       |
|:--------|:----------------------------------|:---------|:---------------------------------------------------------------------|:-----------------|
| L0      | no_exact_cell_overlap             | PASS     | obs_names are unique.                                                | c23715b8e21fd38f |
| L0      | no_forbidden_perturbation_overlap | PASS     | L0 has no perturbation-forbidden rule implemented.                   | c23715b8e21fd38f |
| L1      | no_exact_cell_overlap             | PASS     | obs_names are unique.                                                | 684138a59131ff4b |
| L1      | no_forbidden_perturbation_overlap | PASS     | L1 exact perturbation overlap: []                                    | 684138a59131ff4b |
| L1      | no_group_overlap_replicate        | PASS     | replicate unavailable or uninformative; group overlap check skipped. | 684138a59131ff4b |
| L2      | no_exact_cell_overlap             | PASS     | obs_names are unique.                                                | 842eb5562637cd90 |
| L2      | no_forbidden_perturbation_overlap | PASS     | L2 component overlap: []                                             | 842eb5562637cd90 |
| L2      | no_group_overlap_replicate        | PASS     | replicate unavailable or uninformative; group overlap check skipped. | 842eb5562637cd90 |
