# CRM v1.3 Reviewer Attack Audit

## Reviewer 1: Computational reproducibility

Major concern: Metric definitions, candidate universes, and split construction must be traceable to code.

Status: RESOLVED. v1.3 adds `V13_IMPLEMENTATION_SOURCE_MAP.md`, retrieval/UER/sign-flip audits, split audit, input/output contracts, registries, and minimal-example QC.

Minor concern: Public deposition must be completed before submission.

Status: MANUAL_METADATA. `FINAL_DEPOSITION_PLAN.md`, `CITATION.cff`, Zenodo metadata, and release notes are prepared, but repository/archive publication remains manual.

## Reviewer 2: Endpoint validity

Major concern: UER could be overinterpreted as biological hallucination.

Status: RESOLVED. v1.3 defines UER as an internal sensitivity endpoint and moves unsupported null-bound language out of the main claim set.

Major concern: Retrieval depends on candidate universe.

Status: RESOLVED. v1.3 defines native-candidate and common-candidate retrieval and adds STATE common-candidate sensitivity from frozen centroids.

## Reviewer 3: Generality and overclaiming

Major concern: STATE n=15 is too small to establish architecture-level generality.

Status: LIMITATION. The manuscript states partial cross-architecture support only, labels leave-one-target-out and common-candidate retrieval as exploratory, and avoids broad architecture-level generality language.

Major concern: The study might be read as a universal leaderboard.

Status: RESOLVED. v1.3 frames GEARS/STATE as worked examples and the contribution as an audit grammar.
