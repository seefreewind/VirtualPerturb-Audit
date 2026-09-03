from __future__ import annotations

import numpy as np


def paired_bootstrap_diff(a, b, n_resamples: int = 2000, seed: int = 1) -> dict:
    a = np.asarray(a)
    b = np.asarray(b)
    if len(a) != len(b):
        raise ValueError("Paired arrays must have the same length.")
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_resamples):
        idx = rng.integers(0, len(a), len(a))
        diffs.append(float(np.nanmean(a[idx] - b[idx])))
    lo, hi = np.nanpercentile(diffs, [2.5, 97.5])
    return {"difference": float(np.nanmean(a - b)), "ci95_low": float(lo), "ci95_high": float(hi)}


def bootstrap_mean_ci(values, n_resamples: int = 200, seed: int = 1) -> dict:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return {"mean": np.nan, "ci95_low": np.nan, "ci95_high": np.nan, "ci_status": "NO_FINITE_VALUES"}
    if len(values) == 1:
        value = float(values[0])
        return {"mean": value, "ci95_low": np.nan, "ci95_high": np.nan, "ci_status": "INSUFFICIENT_UNITS"}
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n_resamples):
        idx = rng.integers(0, len(values), len(values))
        means.append(float(np.nanmean(values[idx])))
    lo, hi = np.nanpercentile(means, [2.5, 97.5])
    return {
        "mean": float(np.nanmean(values)),
        "ci95_low": float(lo),
        "ci95_high": float(hi),
        "ci_status": "BOOTSTRAP_PERTURBATION_LEVEL",
    }
