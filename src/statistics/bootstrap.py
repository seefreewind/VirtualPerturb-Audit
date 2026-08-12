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

