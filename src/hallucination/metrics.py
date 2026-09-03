from __future__ import annotations

import numpy as np


def unsupported_effect_rate_at_k(pred_delta, true_delta, null_abs_threshold, k: int = 50) -> float:
    pred_delta = np.asarray(pred_delta)
    true_delta = np.asarray(true_delta)
    order = np.argsort(-np.abs(pred_delta))[:k]
    unsupported = np.abs(true_delta[order]) <= null_abs_threshold
    return float(np.mean(unsupported)) if len(order) else np.nan


def sign_flip_rate(pred_delta, true_delta, support_threshold) -> dict:
    pred_delta = np.asarray(pred_delta)
    true_delta = np.asarray(true_delta)
    supported = np.abs(true_delta) > support_threshold
    if supported.sum() == 0:
        return {"sign_flip_rate": np.nan, "major_sign_flip_rate": np.nan, "n_supported_genes": 0}
    flips = np.sign(pred_delta[supported]) != np.sign(true_delta[supported])
    major = flips & (np.abs(pred_delta[supported]) > support_threshold)
    return {
        "sign_flip_rate": float(np.mean(flips)),
        "major_sign_flip_rate": float(np.mean(major)),
        "n_supported_genes": int(supported.sum()),
    }

