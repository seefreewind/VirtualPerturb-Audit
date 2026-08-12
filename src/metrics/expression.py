from __future__ import annotations

import numpy as np
from scipy.spatial.distance import cosine
from scipy.stats import pearsonr, spearmanr


def _safe_corr(fn, x, y):
    if np.std(x) == 0 or np.std(y) == 0:
        return np.nan
    return float(fn(x, y).statistic)


def expression_metrics(y_true, y_pred) -> dict:
    yt = np.asarray(y_true).ravel()
    yp = np.asarray(y_pred).ravel()
    return {
        "pearson": _safe_corr(pearsonr, yt, yp),
        "spearman": _safe_corr(spearmanr, yt, yp),
        "rmse": float(np.sqrt(np.mean((yt - yp) ** 2))),
        "mae": float(np.mean(np.abs(yt - yp))),
        "cosine_similarity": float(1 - cosine(yt, yp)) if np.linalg.norm(yt) and np.linalg.norm(yp) else np.nan,
    }


def delta(control, perturbed):
    return np.asarray(perturbed).mean(axis=0) - np.asarray(control).mean(axis=0)

