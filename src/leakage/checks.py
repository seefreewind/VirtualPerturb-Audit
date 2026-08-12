from __future__ import annotations

from src.splits.builders import parse_components


def no_exact_cell_overlap(adata) -> tuple[bool, str]:
    if adata.obs_names.has_duplicates:
        return False, "obs_names contain duplicates; exact cell overlap cannot be excluded."
    return True, "obs_names are unique."


def no_forbidden_perturbation_overlap(adata, split: str) -> tuple[bool, str]:
    obs = adata.obs
    train_p = set(obs.loc[obs["split_group"].eq("train"), "perturbation"].astype(str))
    test_p = set(obs.loc[obs["split_group"].eq("test"), "perturbation"].astype(str))
    train_p.discard("ctrl")
    train_p.discard("control")
    if split == "L1":
        overlap = sorted(train_p & test_p)
        return (not overlap, f"L1 exact perturbation overlap: {overlap[:10]}")
    if split == "L2":
        train_g = {g for p in train_p for g in parse_components(p)}
        test_g = {g for p in test_p for g in parse_components(p)}
        overlap = sorted(train_g & test_g)
        return (not overlap, f"L2 component overlap: {overlap[:10]}")
    return True, f"{split} has no perturbation-forbidden rule implemented."


def no_group_overlap(adata, group_key: str = "replicate") -> tuple[bool, str]:
    obs = adata.obs
    if group_key not in obs:
        return True, f"{group_key} unavailable."
    by_group = obs.groupby(group_key)["split_group"].nunique()
    bad = by_group[by_group > 1]
    if len(bad) == 0:
        return True, f"No {group_key} group crosses split."
    return False, f"{len(bad)} {group_key} groups cross split."


def run_split_integrity_checks(adata, split: str) -> list[dict]:
    checks = [
        ("no_exact_cell_overlap", *no_exact_cell_overlap(adata)),
        ("no_forbidden_perturbation_overlap", *no_forbidden_perturbation_overlap(adata, split)),
    ]
    if split != "L0":
        checks.append(("no_group_overlap_replicate", *no_group_overlap(adata, "replicate")))
    return [
        {"check": name, "status": "PASS" if ok else "FAIL", "message": message}
        for name, ok, message in checks
    ]

