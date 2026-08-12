# VirtualPerturb-Audit

Leakage-aware and biology-grounded auditing of virtual perturbation models.

This repository is organized around falsification tests rather than leaderboard ranking. The pilot target is Norman et al. K562 CRISPRa with GEARS and strong baselines under L0/L1/L2 splits.

Current state: Norman GEARS-format data are locally acquired and checksumed, real-data QC and L0/L1/L2 split checks pass, baseline metrics are generated, and a bounded GEARS L1 smoke run verifies the official package execution path. Full GEARS performance evaluation and replicate/control null-envelope calibration are still pending.

Run from this directory:

```bash
python3 -m pytest tests
python3 scripts/build_figures.py
python3 scripts/build_tables.py
python3 scripts/acquire_norman.py
python3 scripts/run_pilot.py
PYTHONPATH=. environment/gears-venv/bin/python scripts/run_gears_pilot.py --audit-split L1 --pert-graph essential --max-train-batches 5 --max-eval-batches 3 --device cpu
```
