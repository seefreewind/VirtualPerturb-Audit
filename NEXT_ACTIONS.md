# Next Actions

1. Acquire Norman manually or through an authenticated browser/session if Dataverse continues returning the AWS WAF challenge; target local path is `data/raw/norman/perturb_processed.h5ad`.
2. Verify `data/raw/norman/perturb_processed.h5ad` schema, checksum, and QC.
3. Install/reproduce GEARS in an isolated environment and record exact dependency versions.
4. Execute `python3 scripts/run_pilot.py` after data/model readiness.
5. Generate real pilot summary, uncertainty intervals, and GO/NO-GO decision.
