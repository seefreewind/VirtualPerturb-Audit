# VirtualPerturb-Audit Reporting Checklist v1.2

| Item | Reporting element | Minimum information |
| --- | --- | --- |
| 1 | Dataset version | Accession/source, processed object identity, filtering scope |
| 2 | Context labels | Cell line/tissue/state labels and how they were normalized |
| 3 | Control definition | Control labels, control pooling, and basal expression source |
| 4 | Perturbation labels | Canonicalization, single/double handling, ctrl+X collapsing |
| 5 | Target universe | Perturbation targets eligible for each endpoint |
| 6 | Gene universe | Gene identifiers, duplicates, model vocabulary, intersection rules |
| 7 | Split construction | Train/test logic, context holdout, target holdout, split hash |
| 8 | Model freeze | Checkpoint, inference adapter, preprocessing, no test-label fitting |
| 9 | Endpoint definitions | Raw-space metrics, audit-delta metrics, retrieval, UER@K, sign flip |
| 10 | Claim boundary | Allowed claim, failure signal, limitations, deposition location |
