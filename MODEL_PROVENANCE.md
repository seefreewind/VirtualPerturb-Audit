# Model Provenance

## HISTORICAL STATUS

## GEARS

```yaml
model: GEARS
repository: https://github.com/snap-stanford/GEARS
paper: Predicting transcriptional outcomes of novel multigene perturbations with GEARS
publication: Nature Biotechnology
publication_year: 2023
doi: 10.1038/s41587-023-01905-6
release_date: UNVERIFIED
checkpoint: trained per dataset; no foundation checkpoint in initial pilot
pretraining_corpus: not_applicable_for_standard_GEARS
corpus_release_date: not_applicable
training_cutoff: not_applicable
explicit_datasets: Norman, Adamson, Dixit, Replogle K562/RPE1 are supported by official loader according to repository documentation
possible_overlap: documented benchmark dataset use, not pretraining contamination
exact_accession_overlap: Norman/GSE133344 possible through processed GEARS data
cellxgene_overlap: UNVERIFIED
publication_overlap: documented model-paper benchmark overlap with Norman-style Perturb-seq datasets
fine_tuning_overlap: model trained on pilot train split only if reproduced locally
evidence_level: A for benchmark dataset use; not a foundation pretraining contamination claim
phase2a_replogle_status: PREMODEL_GATE_CONDITIONAL_GO_ON_GEARS_FILTERED_ESSENTIAL_DATA; K562_R-L1_BOUNDED_SMOKE_COMPLETE_NOT_PERFORMANCE; GEARS_REPLOGLE_FULL_TRAINING_NOT_STARTED
phase2a_allowed_order: source/provenance/metadata/replicate/QC/split/baseline before GEARS smoke or full training
phase2a_required_caveat: Replogle GEARS runs must be labeled filtered essential-screen, not complete Figshare+ genome-scale; BNS remains UNVERIFIED.
```

## scGPT

Status: REGISTERED_NOT_STARTED. Pretraining corpus and perturbation tutorial provenance require separate audit before model inclusion.

## scFoundation

Status: REGISTERED_NOT_STARTED.

## STATE

Status: REGISTERED_NOT_STARTED.


## CURRENT SUBMISSION STATUS

GEARS evaluation completed for the frozen manuscript-facing Norman and GEARS-compatible filtered Replogle tasks. STATE locked audit completed for Norman L1/L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4. Current authoritative manuscript-facing outputs are `results/tables/FINAL_MANUSCRIPT_NUMERIC_REGISTRY.tsv`, compact frozen tables in `results/tables/`, and the public repository plus Zenodo DOI declared in the manuscript.

Historical fields above record earlier planning states and are not authoritative for the final submission state.
