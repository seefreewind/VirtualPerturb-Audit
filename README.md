# VirtualPerturb-Audit

Leakage-aware and biology-grounded auditing of virtual perturbation models.

This repository is organized around falsification tests rather than leaderboard ranking. The pilot target is Norman et al. K562 CRISPRa with GEARS and strong baselines under L0/L1/L2 splits.

Current state: repository scaffold, analysis lock, provenance registries, split checks, baseline adapters, core metrics, hallucination metrics, and pilot figure/table builders are implemented. Verified Norman/GEARS biological results are pending public data acquisition and official-model reproduction.

Run from this directory:

```bash
python3 -m pytest tests
python3 scripts/build_figures.py
python3 scripts/build_tables.py
python3 scripts/acquire_norman.py
python3 -m src.run --config configs/norman_gears_L1_seed1.yaml
```

