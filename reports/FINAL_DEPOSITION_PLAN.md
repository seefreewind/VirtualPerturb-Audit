# Final Deposition Plan v1.3

| artifact | location | size | restricted data | GitHub | other archive | required before submission | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Source code/configs/tests | src/, scripts/, configs/, tests/ | small | No | Yes | Zenodo snapshot | Yes | READY_LOCAL |
| Frozen splits and registries | results/tables/*registry*, split metadata | small | No | Yes | Zenodo | Yes | READY_LOCAL |
| Small result tables | results/tables/ | small | No | Yes | Zenodo | Yes | READY_LOCAL |
| Figure source data and outputs | figures/, results/tables/ | small | No | Yes | Zenodo | Yes | READY_LOCAL |
| STATE target-level outputs | results/state/full_phase2c_20260829T131235Z/ | medium/large | No | Optional | Zenodo or separate archive | Yes | READY_LOCAL_SIZE_CHECK_NEEDED |
| GEARS target-level outputs | results/tables/ and frozen GEARS result dirs | medium/large | No | Optional | Zenodo or separate archive | Yes | READY_LOCAL_SIZE_CHECK_NEEDED |
| Environment manifest | environment/, requirements files | small | No | Yes | Zenodo | Yes | READY_LOCAL |
| Minimal example | examples/minimal_audit/ | small | No | Yes | Zenodo | Recommended | PASS |
| README/LICENSE/CITATION | README.md, LICENSE, CITATION.cff | small | No | Yes | Zenodo snapshot | Yes | READY_LOCAL |
| Original public datasets | Norman/Replogle public sources | large | Respect source licenses | No copies by default | Cite/accession only unless redistribution allowed | No | EXTERNAL_PUBLIC_DATA |

Preferred deposition: GitHub for source/config/tests/small metadata; Zenodo for a tagged source snapshot, frozen splits, result tables, figure source data, environment manifest, and any compressed prediction archive. Use `[ZENODO_DOI_PENDING]` only in working files until a real DOI exists.
