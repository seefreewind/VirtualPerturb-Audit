# Cover Letter to Cell Reports Methods

Generated: 2026-08-30 14:00:36 UTC

Dear Editors,

We are pleased to submit "VirtualPerturb-Audit: a falsification framework for perturbation-response model evaluation" as an Article for Cell Reports Methods.

The central contribution is not a new perturbation predictor, but a reusable framework for testing which aspects of apparent predictive performance survive perturbation-specific and context-shifted stress testing. The framework freezes analysis inputs, separates raw-space global similarity from control-subtracted audit-delta agreement, evaluates perturbation-specific retrieval and unsupported-effect behavior, and records which claims survive matched-target transfer analysis.

The worked example uses frozen GEARS and STATE analyses on Norman and GEARS-compatible filtered Replogle perturbation data. In matched GEARS K562-to-RPE1 transfer, audit-delta Pearson decreased from 0.2812 to -0.0070, a paired drop of 0.2883 with a 95% interval of [0.2559, 0.3206]. The reverse RPE1-to-K562 direction showed a paired drop of 0.5480. STATE provided partial cross-architecture support: across 15 matched Replogle targets, audit-delta Pearson decreased from 0.2955 to 0.1792, a drop of 0.1163 with a 95% interval of [0.0684, 0.1599].

We believe the manuscript fits Cell Reports Methods because it provides a reusable, reproducible evaluation workflow for an active area of computational biology. The manuscript emphasizes claim discipline and community utility rather than a direct model leaderboard. It also makes its boundaries explicit: Replogle analyses use GEARS-compatible filtered essential-screen data, validated biological replicate metadata were unavailable, UER is sensitivity-only, and STATE support is endpoint-heterogeneous.

The authors declare no competing interests. This work received no specific funding. Public code and data archive details are being finalized and are marked as TODO_DEPOSIT in the submission-preparation files.

Sincerely,

[Corresponding author name]
