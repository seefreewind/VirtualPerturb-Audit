from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.run_baseline_pilot import SPLITTERS, summarize_delta_models
from scripts.run_falsification_pilot import shuffled_delta_map
from src.data.loaders import normalize_norman_gears_schema, read_h5ad


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5ad", default="data/raw/norman/perturb_processed.h5ad")
    parser.add_argument("--split-seed", type=int, default=1)
    parser.add_argument("--permutations", type=int, default=20)
    args = parser.parse_args()

    adata = normalize_norman_gears_schema(read_h5ad(Path(args.h5ad)))
    rows = []
    for split in ["L1", "L2"]:
        adata.obs["split_group"] = SPLITTERS[split](adata, seed=args.split_seed)
        for perm_seed in range(1, args.permutations + 1):
            shuffled = shuffled_delta_map(adata, seed=perm_seed)
            split_rows, _ = summarize_delta_models(
                adata,
                split,
                [
                    (
                        "FP3_label_shuffled_mean_effect",
                        shuffled,
                        "COMPLETED_FALSIFICATION_PERMUTATION",
                        f"Label-shuffled perturbation delta probe permutation {perm_seed}",
                    )
                ],
            )
            row = split_rows[0]
            row["permutation_seed"] = perm_seed
            rows.append(row)
    per_perm = pd.DataFrame(rows)
    Path("results/pilot").mkdir(parents=True, exist_ok=True)
    per_perm.to_csv("results/pilot/fp3_label_shuffle_permutations.csv", index=False)

    metric_cols = ["pearson_delta", "UER_at_50", "sign_flip_rate", "retrieval_mrr"]
    summary_rows = []
    for split, sub in per_perm.groupby("split"):
        out = {
            "dataset": "Norman2019_GEARS_processed_mirror",
            "probe": "FP3_label_shuffled_mean_effect",
            "split": split,
            "permutations": int(len(sub)),
            "status": "COMPLETED_FALSIFICATION_PERMUTATIONS",
        }
        for metric in metric_cols:
            vals = pd.to_numeric(sub[metric], errors="coerce").dropna()
            out[f"{metric}_mean"] = float(vals.mean()) if len(vals) else float("nan")
            out[f"{metric}_sd"] = float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")
            out[f"{metric}_q025"] = float(vals.quantile(0.025)) if len(vals) else float("nan")
            out[f"{metric}_q975"] = float(vals.quantile(0.975)) if len(vals) else float("nan")
        summary_rows.append(out)
    pd.DataFrame(summary_rows).to_csv("results/pilot/fp3_label_shuffle_permutation_summary.csv", index=False)


if __name__ == "__main__":
    main()
