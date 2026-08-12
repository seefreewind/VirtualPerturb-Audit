from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_table(df: pd.DataFrame, stem: str):
    out = Path("results/tables")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / f"{stem}.csv", index=False)
    df.to_csv(out / f"{stem}.tsv", sep="\t", index=False)
    (out / f"{stem}.md").write_text(df.to_markdown(index=False) + "\n")
    (out / f"{stem}.tex").write_text(df.to_latex(index=False) + "\n")


def main():
    write_table(pd.DataFrame([
        {"dataset": "Norman2019 K562 CRISPRa", "status": "BLOCKED_PENDING_DOWNLOAD", "role": "pilot"},
        {"dataset": "Replogle K562 CRISPRi", "status": "REGISTERED_NOT_STARTED", "role": "future"},
        {"dataset": "Replogle RPE1 CRISPRi", "status": "REGISTERED_NOT_STARTED", "role": "future"},
    ]), "table1_datasets")
    write_table(pd.DataFrame([
        {"model": "GEARS", "status": "REGISTERED_PENDING_REPRODUCTION", "role": "pilot"},
        {"model": "No-change", "status": "IMPLEMENTED", "role": "baseline"},
        {"model": "Context mean", "status": "IMPLEMENTED", "role": "baseline"},
        {"model": "PCA/Ridge", "status": "IMPLEMENTED", "role": "baseline"},
    ]), "table2_models")
    write_table(pd.DataFrame([
        {"code": "LKG-1", "name": "Cell leakage", "pilot_status": "CHECK_IMPLEMENTED"},
        {"code": "LKG-2", "name": "Perturbation leakage", "pilot_status": "CHECK_IMPLEMENTED_L1_L2"},
        {"code": "LKG-4", "name": "Preprocessing leakage", "pilot_status": "TRAINING_ONLY_SCALER_IMPLEMENTED"},
    ]), "table3_leakage_taxonomy")


if __name__ == "__main__":
    main()

