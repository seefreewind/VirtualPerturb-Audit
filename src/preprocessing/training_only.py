from __future__ import annotations

import numpy as np
from sklearn.preprocessing import StandardScaler


class TrainingOnlyScaler:
    """Scaler that records fit indices to audit preprocessing leakage."""

    def __init__(self):
        self.scaler = StandardScaler(with_mean=True, with_std=True)
        self.fit_indices_: list[str] | None = None

    def fit(self, X, obs_names):
        self.fit_indices_ = list(obs_names)
        self.scaler.fit(X)
        return self

    def transform(self, X):
        if self.fit_indices_ is None:
            raise RuntimeError("TrainingOnlyScaler must be fit before transform.")
        return self.scaler.transform(X)


def assert_training_only_fit(fit_indices, train_indices) -> tuple[bool, str]:
    leaked = sorted(set(fit_indices) - set(train_indices))
    if leaked:
        return False, f"Preprocessing fit used non-training observations: {leaked[:10]}"
    return True, "Preprocessing fit indices are a subset of training observations."


def matrix_to_numpy(X):
    if hasattr(X, "toarray"):
        return X.toarray()
    return np.asarray(X)

