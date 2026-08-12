from __future__ import annotations

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline


class NoChangeBaseline:
    name = "B0_no_change"

    def fit(self, X_train, y_train=None, meta_train=None):
        return self

    def predict(self, X_control, perturbations=None, contexts=None):
        return np.asarray(X_control)


class GlobalPerturbedMeanBaseline:
    name = "B1_global_perturbed_mean"

    def fit(self, X_train, y_train, meta_train=None):
        self.mean_ = np.asarray(y_train).mean(axis=0)
        return self

    def predict(self, X_control, perturbations=None, contexts=None):
        return np.repeat(self.mean_[None, :], len(X_control), axis=0)


class ContextMatchedMeanBaseline:
    name = "B2_context_matched_perturbed_mean"

    def fit(self, X_train, y_train, meta_train):
        self.global_mean_ = np.asarray(y_train).mean(axis=0)
        self.context_means_ = {}
        contexts = meta_train.get("context")
        if contexts is not None:
            for ctx in sorted(set(contexts)):
                mask = np.asarray(contexts) == ctx
                self.context_means_[ctx] = np.asarray(y_train)[mask].mean(axis=0)
        return self

    def predict(self, X_control, perturbations=None, contexts=None):
        rows = []
        for ctx in contexts:
            rows.append(self.context_means_.get(ctx, self.global_mean_))
        return np.vstack(rows)


class PCARidgeBaseline:
    name = "B4_pca_ridge"

    def __init__(self, n_components: int = 20, alpha: float = 1.0):
        self.n_components = n_components
        self.alpha = alpha

    def fit(self, X_features, y_delta, meta_train=None):
        n_components = min(self.n_components, min(X_features.shape) - 1)
        n_components = max(1, n_components)
        self.pipe_ = make_pipeline(PCA(n_components=n_components), Ridge(alpha=self.alpha))
        self.pipe_.fit(X_features, y_delta)
        return self

    def predict_delta(self, X_features):
        return self.pipe_.predict(X_features)

