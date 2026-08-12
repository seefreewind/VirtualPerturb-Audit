# Next Actions

1. Add GEARS prediction export and metric integration so GEARS rows can be appended to `results/pilot/pilot_summary.csv`.
2. Run GEARS L1/L2 with adequate compute; use `--max-train-batches` only for development smoke checks.
3. Verify whether any Norman metadata or alternate source file contains true replicate/batch labels.
4. Replace provisional UER/BNS thresholds with verified replicate/control null envelopes when possible.
5. Regenerate figures and GO/NO-GO decision after GEARS metrics are available.
