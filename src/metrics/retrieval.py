from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def perturbation_centroid_retrieval(pred_centroids: dict[str, np.ndarray], true_centroids: dict[str, np.ndarray]) -> dict:
    rows = perturbation_retrieval_rows(pred_centroids, true_centroids)
    ranks = np.asarray([row["true_target_rank"] for row in rows if np.isfinite(row["true_target_rank"])])
    if len(ranks) == 0:
        return {"top1_accuracy": np.nan, "top5_accuracy": np.nan, "mrr": np.nan}
    return {
        "top1_accuracy": float(np.mean(ranks == 1)),
        "top5_accuracy": float(np.mean(ranks <= 5)),
        "mrr": float(np.mean(1 / ranks)),
    }


def perturbation_retrieval_rows(pred_centroids: dict[str, np.ndarray], true_centroids: dict[str, np.ndarray]) -> list[dict]:
    labels = sorted(set(pred_centroids) & set(true_centroids))
    if not labels:
        return []
    true_matrix = np.vstack([true_centroids[k] for k in labels])
    rows = []
    for label in labels:
        pred = np.asarray(pred_centroids[label]).ravel()
        if np.linalg.norm(pred) == 0:
            rows.append({
                "perturbation": label,
                "true_target_rank": np.nan,
                "top_match": "UNINFORMATIVE_PREDICTION",
                "top_match_similarity": np.nan,
                "true_target_similarity": np.nan,
                "is_confused": np.nan,
            })
            continue
        sims = cosine_similarity(pred[None, :], true_matrix).ravel()
        order = np.argsort(-sims)
        rank = int(np.where(order == labels.index(label))[0][0]) + 1
        top_label = labels[int(order[0])]
        rows.append({
            "perturbation": label,
            "true_target_rank": rank,
            "top_match": top_label,
            "top_match_similarity": float(sims[order[0]]),
            "true_target_similarity": float(sims[labels.index(label)]),
            "is_confused": bool(top_label != label),
        })
    return rows
