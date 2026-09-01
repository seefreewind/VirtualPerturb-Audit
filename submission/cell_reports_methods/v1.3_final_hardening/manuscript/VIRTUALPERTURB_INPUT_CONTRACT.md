# VirtualPerturb-Audit Input Contract v1.3

Accepted data levels supported by the current code:

1. Cell-level AnnData objects with expression matrix, gene identifiers, perturbation labels, control labels, and optional context labels.
2. Target-level pseudobulk matrices with observed and predicted expression or response centroids.
3. Precomputed prediction matrices or centroid dictionaries with a declared gene and target universe.

| field | required/optional/conditional | definition |
| --- | --- | --- |
| target_id | required | Canonical perturbation target identifier after label normalization |
| context_id | conditional | Cell line, tissue, batch, or state label; required for context-transfer audits |
| gene_id | required | Ordered gene identifier defining the vector space |
| observed_expression | required | Observed cell-level matrix, pseudobulk vector, or true centroid |
| predicted_expression | required | Model-predicted cell-level matrix, pseudobulk vector, or predicted centroid |
| control_expression | required | Control/basal expression used to construct audit deltas |
| split_id | required | L0/L1/L2/L3/R-L1/R-L4 or declared custom split |
| candidate_universe | required for retrieval | Perturbation targets eligible as retrieval candidates |
| model_id | optional | Model/checkpoint identifier |
| preprocessing_id | optional | Frozen preprocessing or gene-vocabulary identifier |
