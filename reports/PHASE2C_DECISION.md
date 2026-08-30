# Phase 2C Decision

Generated: 2026-08-30 00:24:12 UTC

Decision: `PARTIAL_ARCHITECTURE_SUPPORT_TARGET_MATCHED_ENDPOINT_MIXED`.

The full GPU STATE run completed for Norman L1, Norman L2, Replogle K562 R-L1, and Replogle K562-to-RPE1 R-L4. The Replogle full-summary comparison shows lower cross-context Pearson under an independent STATE architecture, while retrieval MRR and UER@50 are mixed because the R-L4 target set is smaller:

- STATE K562 R-L1 delta-Pearson: 0.2639
- STATE K562-to-RPE1 R-L4 delta-Pearson: 0.1874
- Pearson drop: 0.0765
- Retrieval MRR drop: -0.0405
- UER@50 increase: -0.0174

On matched Replogle targets, STATE shows a clearer context-transfer contrast:

- Matched Pearson drop: 0.1163
- Matched UER@50 source-minus-cross difference: -0.0280
- Matched sign-flip source-minus-cross difference: -0.0557

Interpretation: STATE partially reproduces the GEARS context-transfer failure phenotype on matched targets, supporting an architecture-independent signal for the core transfer drop. The endpoint-level picture is mixed in the full-summary table, so the decision is not a blanket confirmation. The conclusion remains bounded by the audit-delta null choice, unverified BNS, target-set differences, and the fact that Norman GEARS frozen rows are in raw GEARS space while STATE primary rows use audit-delta space.

Main deliverables:

- `results/tables/state_phase2c_primary_metrics.csv`
- `results/tables/state_transfer_drop.csv`
- `results/tables/gears_state_primary_comparison.csv`
- `reports/STATE_GEARS_METRIC_COMPATIBILITY.md`
- `reports/STATE_REPLOGLE_EARLY_GATE.md`
- `reports/STATE_RL4_ADAPTER_REPORT.md`
- `figures/main/gears_state_confirmatory_audit.pdf`
- `figures/main/gears_state_confirmatory_audit.svg`
- `figures/main/gears_state_confirmatory_audit.png`
- `figures/main/gears_state_context_transfer.pdf`
