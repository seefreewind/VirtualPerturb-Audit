# GEARS Model Card

## Identity

- Official repository: https://github.com/snap-stanford/GEARS
- Paper: Predicting transcriptional outcomes of novel multigene perturbations with GEARS
- DOI: 10.1038/s41587-023-01905-6
- Pilot role: complex model comparator for Norman L0/L1/L2

## Reproduction Status

Status: BATCH_SMOKE_VERIFIED_FULL_EVALUATION_PENDING.

The project records GEARS as an official-code reproduction target. `cell-gears==0.1.2` and `torch-geometric==2.6.1` were installed in the isolated project environment `environment/gears-venv`; `from gears import PertData, GEARS` was verified on 2026-08-12. First import takes about 35 seconds on the local Apple Silicon Mac because Scanpy/SciPy import is slow.

The official package import is verified, the Norman processed file checksum is recorded, and a bounded L1 batch-smoke run completed on 2026-08-12 at `results/pilot/gears_20260812T152223Z/`. This run verified initialization, dataloading, forward/backward training for 5 batches, filtered GO tensor injection, checkpoint save, strict JSON metadata writing, and bounded prediction summary export. It is not a performance benchmark.

## Prior Fallbacks

The default GEARS GO graph tarball at Harvard Dataverse datafile `6934319` returned a WAF/empty-file failure under command-line access. The runner therefore supports `--pert-graph essential`, which uses the official GEARS `gene_set_path` code path with `essential_all_data_pert_genes.pkl`, and `--pert-graph dynamic`, which uses `default_pert_graph=False`. These are not source-code modifications, but they may differ from the official precomputed default graph and must be treated as documented prior-provenance differences.

`--pert-graph dynamic` successfully constructed a GO graph but failed at training with a perturbation-index mismatch against cached cell graphs. It should not be used for reported GEARS results unless the cache and perturbation node map are rebuilt consistently and documented.

`--pert-graph essential` now injects a filtered GO tensor for non-default graph modes. The completed L1 batch smoke used 133,961 filtered GO edges over 9,853 perturbation graph nodes.

## Modification Log

No GEARS source modifications have been made. Local wrapper modifications are limited to `scripts/run_gears_pilot.py`.

## Information Access

GEARS uses perturbation identity and graph/gene priors according to the official method. Exact prior files, versions, and filtering behavior must be recorded before pilot claims.
