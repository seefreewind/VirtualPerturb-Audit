from __future__ import annotations

import numpy as np
import pandas as pd

from src.hallucination.metrics import sign_flip_rate, unsupported_effect_rate_at_k
from src.leakage.checks import run_split_integrity_checks
from src.metrics.bounds import bound_normalized_score
from src.splits.builders import assign_l1_perturbation_holdout, assign_l2_component_holdout


class ToyAnnData:
    def __init__(self, obs):
        self.obs = obs
        self.obs_names = pd.Index([f"cell{i}" for i in range(len(obs))])
        self.n_obs = len(obs)
        self.n_vars = 3


def toy():
    obs = pd.DataFrame({
        "perturbation": ["ctrl", "ctrl", "A", "A", "B", "B", "A+B", "A+B", "C", "C"],
        "control_status": ["control", "control"] + ["perturbed"] * 8,
        "replicate": [f"r{i}" for i in range(10)],
    })
    return ToyAnnData(obs)


def test_l1_has_no_exact_test_perturbation_in_train():
    adata = toy()
    adata.obs["split_group"] = assign_l1_perturbation_holdout(adata, seed=2, test_fraction=0.3)
    checks = run_split_integrity_checks(adata, "L1")
    assert all(c["status"] == "PASS" for c in checks), checks


def test_l2_has_no_component_overlap():
    adata = toy()
    adata.obs["split_group"] = assign_l2_component_holdout(adata, seed=4, test_fraction=0.4)
    checks = run_split_integrity_checks(adata, "L2")
    assert all(c["status"] == "PASS" for c in checks), checks


def test_bns_marks_uninformative_assay():
    score, status = bound_normalized_score(0.4, 0.5, 0.5)
    assert score is None
    assert status == "UNINFORMATIVE_ASSAY"


def test_hallucination_metrics_are_defined():
    pred = np.array([5, 4, 0.1, -3])
    true = np.array([0.01, 4.2, 0.0, 3.1])
    assert unsupported_effect_rate_at_k(pred, true, 0.05, k=2) == 0.5
    sfr = sign_flip_rate(pred, true, support_threshold=1)
    assert sfr["n_supported_genes"] == 2
    assert sfr["sign_flip_rate"] == 0.5

