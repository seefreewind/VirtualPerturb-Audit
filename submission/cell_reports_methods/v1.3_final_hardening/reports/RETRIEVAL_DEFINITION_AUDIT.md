# Retrieval Definition Audit v1.3

Status: COMPLETE.

The frozen implementation uses cosine similarity between predicted perturbation-response centroids and candidate observed perturbation-response centroids. Vectors are not additionally standardized or centered inside the retrieval function; they are used in the metric space supplied by upstream code, such as audit-delta centroids or raw/control-subtracted STATE centroids. The gene universe is the ordered vector dimension of the saved centroids after upstream model-compatible gene intersection. Controls are not retrieval candidates. Candidate perturbations are the sorted intersection of available predicted and true perturbation labels. Unavailable targets are excluded from that endpoint. For exact score ties, the generic retrieval code relies on NumPy descending argsort order; the v1.3 STATE common-candidate sensitivity uses Python stable sorting after descending cosine score.

Top1 is the fraction of evaluated targets for which the correct perturbation has rank 1. Top5 is the fraction with rank <= 5. MRR is the mean of 1/rank over finite ranks. Native-candidate retrieval uses each run's own candidate universe. Common-candidate retrieval restricts compared runs to the same matched target universe and is labelled exploratory when recomputed from frozen centroids.
