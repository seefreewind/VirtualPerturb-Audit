# Figure 1 Redesign Brief v1.2

## Goal

Redesign Figure 1 as the visual identity of VirtualPerturb-Audit, not as a result plot. The figure should let an editor understand the method in one scan.

## Recommended Layout

Use a left-to-right five-stage workflow:

1. Freeze inputs
2. Global-fit audit
3. Perturbation-specific audit
4. Falsification audit
5. Transfer and unsupported-effect audit

Below each stage, show one compact line for inputs, tests, failure signal, and allowed claim. Use color only to separate endpoint families: global agreement, perturbation identity, falsification, transfer, and unsupported-effect/sign-direction burden.

## Mandatory Labels

- Raw-space Pearson is not audit-delta Pearson.
- Retrieval requires a declared candidate universe.
- UER@K is an internal sensitivity measure.
- Matched-target transfer controls target composition but not every context confounder.
- Output is a bounded claim, not a single pass/fail verdict.

## Avoid

- Do not present GEARS or STATE as the framework itself.
- Do not use pipeline status labels or phase labels.
- Do not overfill the figure with numeric results.
