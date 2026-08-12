# Model Provenance

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
```

## scGPT

Status: REGISTERED_NOT_STARTED. Pretraining corpus and perturbation tutorial provenance require separate audit before model inclusion.

## scFoundation

Status: REGISTERED_NOT_STARTED.

## STATE

Status: REGISTERED_NOT_STARTED.

