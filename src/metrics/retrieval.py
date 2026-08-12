from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def perturbation_centroid_retrieval(pred_centroids: dict[str, np.ndarray], true_centroids: dict[str, np.ndarray]) -> dict:
    labels = sorted(set(pred_centroids) & set(true_centroids))
    if not labels:
        return {"top1_accuracy": np.nan, "top5_accuracy": np.nan, "mrr": np.nan}
    true_matrix = np.vstack([true_centroids[k] for k in labels])
    ranks = []
    for label in labels:
        sims = cosine_similarity(np.asarray(pred_centroids[label])[None, :], true_matrix).ravel()
        order = np.argsort(-sims)
        rank = int(np.where(order == labels.index(label))[0][0]) + 1
        ranks.append(rank)
    ranks = np.asarray(ranks)
    return {
        "top1_accuracy": float(np.mean(ranks == 1)),
        "top5_accuracy": float(np.mean(ranks <= 5)),
        "mrr": float(np.mean(1 / ranks)),
    }

