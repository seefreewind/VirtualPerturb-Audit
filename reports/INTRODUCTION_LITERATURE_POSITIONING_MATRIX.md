# Introduction Literature Positioning Matrix v1.4

| Study | Year | Main evaluation problem addressed | Strong baselines | Systematic variation | Multiple metrics | Retrieval | OOD perturbation | Context transfer | Biological fidelity | Falsification probes | Matched-target transfer | Claim-boundary assignment | Reproducible framework | How VirtualPerturb-Audit differs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ahlmann-Eltze | 2025 | Strong baseline problem | Yes | No | Some | No | Some | No | Yes | No | No | No | Shows why target-blind/simple baselines must be explicit |
| Systema | 2025 | Systematic variation | Yes | Yes | Yes | No | Some | Some | Yes | No | No | Yes | VPA adds claim-boundary assignment and matched-target falsification |
| PerturBench | 2025 | Standardized benchmarking and metric complementarity | Yes | Some | Yes | Some | Yes | Some | Some | No | No | Yes | VPA shifts from comparison to claim falsification |
| scArchon | 2026 | Reproducible modular benchmark and biological response structure | Yes | Some | Yes | Some | Yes | Some | Yes | No | No | Yes | VPA adds information-removal probes and explicit claim boundaries |
| SBB | 2026 | Signal, bounds, and baselines | Yes | Some | Yes | No | Some | Some | Yes | No | No | Some | VPA operationalizes reviewer-facing audit outputs and matched-target transfer |
| In-the-wild virtual-cell benchmark | 2026 | Strict generalization and context transfer | Yes | Some | Yes | Some | Yes | Yes | Some | No | Some | Yes | VPA focuses on claim survival under stress tests |
| scPertEval | 2026 | Principled evaluation design | Yes | Some | Yes | Some | Some | Some | Some | Some | Some | Yes | VPA packages falsification probes, matched transfer, and claim boundaries as a protocol |
| VirtualPerturb-Audit | 2026 | Claim falsification and bounded interpretation | Yes | Reports caveat | Yes | Yes | Yes | Yes, matched | Endpoint-specific | Yes | Yes | Yes | Worked examples use GEARS and STATE outputs, not a universal leaderboard |
