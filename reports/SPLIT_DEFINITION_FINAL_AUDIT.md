# Split Definition Final Audit v1.3

| split_id | definition | source | construction | supported interpretation |
| --- | --- | --- | --- | --- |
| L0 | Random cell holdout | src/splits/builders.py:25-34 | cells randomly assigned to train/val/test with seed | No target-level novelty claim |
| L1 | Unseen perturbation holdout | src/splits/builders.py:37-56 | non-control perturbations held out; controls remain train | Within-context unseen-target generalization |
| L2 | Component holdout | src/splits/builders.py:59-82 | perturbations assigned by held-out component sets; mixed overlaps excluded | Component-level stress test, not post-hoc family test |
| L3 | HGNC gene-family holdout | src/splits/builders.py:85-127 | gene-family candidates from results/pilot/l3_gene_family_holdout_candidates.csv; provenance data/metadata/hgnc_perturbation_gene_groups_provenance.json | Family-level stress test |
| R-L1 | Replogle within-context target holdout | src/splits/builders.py:130-163 | single cell-line context; controls train; held-out non-control targets test | Within-context Replogle target holdout |
| R-L4 | Replogle cross-context inference adapter | src/splits/builders.py:166-190 | source-context train perturbations; target-context perturbations and controls test | Cross-context stress test with adapter limitation |
