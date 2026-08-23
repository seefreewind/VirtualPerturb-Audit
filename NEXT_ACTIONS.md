# Next Actions

1. Optionally run a bounded GEARS Replogle RPE1 smoke test to mirror the completed K562 R-L1 smoke. Keep the gate label `CONDITIONAL_GO_GEARS_FILTERED`.
2. If smoke coverage is sufficient, launch full filtered-data GEARS evaluations for R-L1-K562, R-L1-RPE1, R-L4-K2R, and R-L4-R2K, preferably on GPU or as resumable CPU jobs.
3. Rebuild downstream tables/figures with Replogle rows explicitly labeled `Replogle_GEARS_filtered` and `BNS_STATUS = UNVERIFIED`.
4. If complete Figshare+ processed h5ad/manifest access becomes available, repeat source/QC/split/baseline/gate on the complete objects before making complete-data claims.
5. Keep searching only paper-linked/official routes for complete Replogle data; do not use untrusted mirrors.
