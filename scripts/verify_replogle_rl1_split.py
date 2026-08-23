from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")


def main() -> None:
    import scanpy as sc

    from scripts.audit_replogle_processed import standardized_obs
    from src.splits.builders import assign_replogle_l1_context_perturbation_holdout, split_hash


    class ObsOnly:
        def __init__(self, obs: pd.DataFrame, n_vars: int = 5000):
            self.obs = obs
            self.n_vars = n_vars

    frozen = {
        "R-L1-K562": "e9fcaf7afdb972e4",
        "R-L1-RPE1": "288d45dbeb512ce5",
    }
    k = sc.read_h5ad("data/raw/replogle/replogle_k562_essential/perturb_processed.h5ad", backed="r")
    r = sc.read_h5ad("data/raw/replogle/replogle_rpe1_essential/perturb_processed.h5ad", backed="r")
    k_obs = standardized_obs(k, "Replogle_K562_GEARS_filtered", "K562")
    r_obs = standardized_obs(r, "Replogle_RPE1_GEARS_filtered", "RPE1")
    k.file.close()
    r.file.close()
    obs_all = pd.concat([k_obs, r_obs], axis=0)
    rows = []
    for split, cell_line, expected in [
        ("R-L1-K562", "K562", frozen["R-L1-K562"]),
        ("R-L1-RPE1", "RPE1", frozen["R-L1-RPE1"]),
    ]:
        labels = [str(x) for x in assign_replogle_l1_context_perturbation_holdout(ObsOnly(obs_all), cell_line, seed=1)]
        observed = split_hash(labels)
        counts = {k: labels.count(k) for k in ["train", "val", "test", "exclude_other_context"]}
        rows.append(
            {
                "split": split,
                "frozen_split_hash": expected,
                "recomputed_split_hash": observed,
                "match": expected == observed,
                "counts": counts,
            }
        )
    out = pd.DataFrame(rows)
    out_path = Path("results/replogle/rl1_split_reproducibility.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(out.to_string(index=False))
    ok = bool(out["match"].all())
    print("STATUS:", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()