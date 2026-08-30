# Article Type Audit

Decision: `ARTICLE_METHODS_FRAME_READY_WITH_MANUAL_FORMAT_CHECK`.

VirtualPerturb-Audit should be submitted as a methods Article. The core contribution is a reusable falsification and reporting framework for perturbation-response model evaluation, demonstrated on frozen GEARS and STATE worked examples. The manuscript should not be framed as a GEARS benchmark paper, STATE benchmark paper, or universal virtual-cell leaderboard.

## Fit Rationale

- The paper introduces a transferable evaluation workflow.
- The strongest novelty is endpoint separation and claim-evidence discipline.
- GEARS and STATE are examples used to demonstrate the workflow.
- The framework produces editor-facing audit artifacts: limitations, code-release gate, reviewer simulation, and claim-evidence matrix.

## Risks

- If framed as a benchmark, the incomplete Replogle data and mixed STATE endpoints become major weaknesses.
- If framed as a method audit, those same constraints become visible boundaries of the worked example.
