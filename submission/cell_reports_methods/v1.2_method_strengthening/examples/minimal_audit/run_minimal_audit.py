#!/usr/bin/env python3
import numpy as np
import pandas as pd


def corr(a, b):
    if np.std(a) == 0 or np.std(b) == 0:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


df = pd.read_csv("toy_predictions.csv")
true = df.pivot(index="perturbation", columns="gene", values="true_delta")
pred = df.pivot(index="perturbation", columns="gene", values="pred_delta")

rows = []
for p in pred.index:
    scores = {cand: corr(pred.loc[p].values, true.loc[cand].values) for cand in true.index}
    ranked = sorted(scores, key=scores.get, reverse=True)
    rank = ranked.index(p) + 1
    order = pred.loc[p].abs().sort_values(ascending=False).index[:2]
    unsupported = (true.loc[p, order].abs() <= 0.20).mean()
    supported = true.loc[p].abs() > 0.50
    flips = (np.sign(pred.loc[p, supported]) != np.sign(true.loc[p, supported])).mean()
    rows.append({
        "perturbation": p,
        "audit_delta_pearson": corr(true.loc[p].values, pred.loc[p].values),
        "retrieval_rank": rank,
        "mrr_contribution": 1.0 / rank,
        "uer_at_2": float(unsupported),
        "sign_flip_rate": float(flips),
    })

out = pd.DataFrame(rows)
out.to_csv("minimal_audit_table.csv", index=False)
print(out.to_string(index=False))
