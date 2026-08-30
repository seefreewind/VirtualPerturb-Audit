# Cover Letter to Cell Reports Methods

Generated: 2026-08-30 07:13:25 UTC

Dear Editors,

We are pleased to submit the Article manuscript, "VirtualPerturb-Audit: a falsification framework for perturbation-response model evaluation," for consideration in Cell Reports Methods.

Perturbation-response models are often summarized by global transcriptional agreement, but this single view can miss failures in perturbation specificity and cross-context transfer. VirtualPerturb-Audit provides a reusable evaluation framework that separates global fit, perturbation retrieval, unsupported-effect behavior, sign-flip burden, leakage risk, and matched-target context transfer. The manuscript is framed as a methods paper: the contribution is the audit design and claim discipline, with GEARS and STATE used as worked examples rather than as a direct leaderboard.

The study reports frozen Norman and GEARS-compatible filtered Replogle analyses. Matched-target GEARS tests show strong cross-context degradation in both K562-to-RPE1 and RPE1-to-K562 directions. A full GPU STATE audit provides partial cross-architecture support: matched Replogle targets show a Pearson drop, while retrieval and unsupported-effect endpoints remain mixed in full-summary comparisons. We therefore present a bounded conclusion that the framework can reveal transfer-specific failure modes that aggregate metrics obscure.

All claims in the manuscript preserve the limitations of the current evidence. Replogle analyses use GEARS-compatible filtered essential-screen data rather than the complete Figshare+ processed objects; BNS is unverified; UER is sensitivity-only; and GEARS/STATE absolute values are not treated as a direct leaderboard where target universes and metric spaces differ.

This manuscript has not been submitted elsewhere. Author, conflict-of-interest, funding, and data/code availability details should be finalized by the submitting author before journal submission.

Sincerely,

[Corresponding author name]
