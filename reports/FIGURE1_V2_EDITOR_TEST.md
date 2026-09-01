# Figure 1 v2 Editor Test

Editor test: PASS

| question | answer |
| --- | --- |
| What is VirtualPerturb-Audit? | A model-agnostic protocol that audits perturbation-response predictions under frozen provenance. |
| What inputs does it require? | Observed responses, model predictions, controls, perturbation/context labels, and frozen splits/genes/targets/preprocessing/checkpoint/code. |
| What are its main audit modules? | Global-fit, perturbation-specific, falsification, and transfer/error-burden audits. |
| How is it different from a single-score benchmark? | It maps metrics through stress tests into endpoint-specific claim boundaries. |
| What is the final output? | An endpoint-specific claim profile. |
| Does it look model-agnostic? | Yes; no GEARS/STATE labels are used in the schematic body. |
| Can the workflow be understood in <30 seconds? | Yes; the panel hierarchy reads top to middle to bottom. |
