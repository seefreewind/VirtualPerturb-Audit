from __future__ import annotations

import hashlib
import json

import numpy as np


def split_hash(labels: list[str]) -> str:
    payload = json.dumps(labels, sort_keys=False).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def parse_components(perturbation: str) -> set[str]:
    p = str(perturbation)
    if p.lower() in {"ctrl", "control", "non-targeting", "ntc"}:
        return set()
    for sep in ["+", "_", "|"]:
        if sep in p:
            return {x for x in p.split(sep) if x and x.lower() not in {"ctrl", "control"}}
    return {p}


def assign_l0_random_cells(adata, seed: int = 1, test_fraction: float = 0.2, val_fraction: float = 0.1):
    rng = np.random.default_rng(seed)
    n = adata.n_obs
    order = rng.permutation(n)
    labels = np.array(["train"] * n, dtype=object)
    n_test = int(round(n * test_fraction))
    n_val = int(round(n * val_fraction))
    labels[order[:n_test]] = "test"
    labels[order[n_test : n_test + n_val]] = "val"
    return labels.tolist()


def assign_l1_perturbation_holdout(adata, seed: int = 1, test_fraction: float = 0.2, val_fraction: float = 0.1):
    obs = adata.obs
    perturbs = np.array(sorted(obs.loc[obs["control_status"] != "control", "perturbation"].astype(str).unique()))
    rng = np.random.default_rng(seed)
    rng.shuffle(perturbs)
    n_test = max(1, int(round(len(perturbs) * test_fraction))) if len(perturbs) else 0
    n_val = max(1, int(round(len(perturbs) * val_fraction))) if len(perturbs) else 0
    test_p = set(perturbs[:n_test])
    val_p = set(perturbs[n_test : n_test + n_val])
    labels = []
    for p, c in zip(obs["perturbation"].astype(str), obs["control_status"].astype(str)):
        if c == "control":
            labels.append("train")
        elif p in test_p:
            labels.append("test")
        elif p in val_p:
            labels.append("val")
        else:
            labels.append("train")
    return labels


def assign_l2_component_holdout(adata, seed: int = 1, test_fraction: float = 0.2, val_fraction: float = 0.1):
    obs = adata.obs
    perturbs = sorted(obs.loc[obs["control_status"] != "control", "perturbation"].astype(str).unique())
    components = sorted({g for p in perturbs for g in parse_components(p)})
    rng = np.random.default_rng(seed)
    rng.shuffle(components)
    n_test = max(1, int(round(len(components) * test_fraction))) if len(components) else 0
    n_val = max(1, int(round(len(components) * val_fraction))) if len(components) else 0
    test_g = set(components[:n_test])
    val_g = set(components[n_test : n_test + n_val])
    labels = []
    for p, c in zip(obs["perturbation"].astype(str), obs["control_status"].astype(str)):
        comps = parse_components(p)
        if c == "control":
            labels.append("train")
        elif comps and comps <= test_g:
            labels.append("test")
        elif comps and comps <= val_g:
            labels.append("val")
        elif comps & (test_g | val_g):
            labels.append("exclude_component_overlap")
        else:
            labels.append("train")
    return labels
