# VirtualPerturb-Audit Reporting Checklist v1.0

| item | required/recommended | reason | reported_in_current_study | location |
| --- | --- | --- | --- | --- |
| dataset version | required | Defines input state | yes | STAR Methods; Resource availability |
| context labels | required | Required for transfer claims | yes | STAR Methods; contracts |
| control definition | required | Defines delta response | yes | STAR Methods; contracts |
| perturbation-label normalization | required | Prevents target mismatch | yes | STAR Methods |
| gene universe | required | Defines vector space | yes | STAR Methods; input contract |
| target universe | required | Defines candidate and matched analyses | yes | STAR Methods; registries |
| split construction | required | Defines generalization claim | yes | SPLIT_DEFINITION_FINAL_AUDIT.md |
| model checkpoint | required | Reproducibility | yes | Resource availability |
| preprocessing freeze | required | Avoids leakage and drift | yes | STAR Methods |
| evaluation code version | required | Reproducibility | yes | source map |
| strong baseline | recommended | Separates model signal from simple structure | yes | baseline registry |
| raw-space metric | required | Global expression agreement | yes | Results |
| control-subtracted metric | required | Response agreement | yes | Results |
| retrieval candidate universe | required | Interprets Top1/Top5/MRR | yes | retrieval audit |
| falsification probe | recommended | Tests information removal | yes | probe registry |
| context-shift test where relevant | recommended | Transfer boundary | yes | Results |
| matched-target transfer where relevant | recommended | Controls target composition | yes | Results |
| null provenance for UER | required | Avoids hallucination overclaim | yes | UER audit |
| statistical unit | required | Prevents cell-level precision inflation | yes | Quantification |
| model/data overlap provenance | required | Guards leakage and pretraining overlap | partly | limitations; deposition plan |
