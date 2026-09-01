# Figure 5 v2 Start Audit

## Figure contract

- Core conclusion: STATE provides partial cross-architecture support for matched transfer degradation, with endpoint heterogeneity.
- Archetype: quantitative grid
- Target journal style: Cell Reports Methods
- Backend: Python / matplotlib only
- Scope: Figure 5, Figure 5 source script, Figure 5 legend, and minimal Figure 5 Results wording

## Existing design issue

The pre-v2 Figure 5 used a vertical bar chart on the frozen source-minus-cross metric. That mixed agreement endpoints, where higher values are better, with burden endpoints, where higher values are worse. The v2 figure removes the bar chart and uses a direction-aligned forest plot.

## Frozen input files

- `results/tables/state_transfer_drop.csv`
- `results/tables/state_matched_common_candidate_retrieval_summary.tsv`
- `results/tables/state_matched_leave_one_out_summary.tsv`
