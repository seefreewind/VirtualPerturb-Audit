from __future__ import annotations

import numpy as np


def bound_normalized_score(s_model: float, s_lower: float, s_upper: float) -> tuple[float | None, str]:
    if not np.isfinite([s_model, s_lower, s_upper]).all():
        return None, "UNVERIFIED"
    if s_upper <= s_lower:
        return None, "UNINFORMATIVE_ASSAY"
    return float((s_model - s_lower) / (s_upper - s_lower)), "OK"

