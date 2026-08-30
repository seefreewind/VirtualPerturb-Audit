# CRM Code Release Audit

Decision: `NEEDS_CLEANUP_BEFORE_PUBLIC_RELEASE`.

## Present Assets

- Frozen reports and tables for Phase 1, Phase 2A, Phase 2B, and Phase 2C.
- Scripts for acquisition, GEARS audit runs, STATE post-processing, supplementary package generation, and CRM package generation.
- Figure exports in PDF/SVG/PNG.
- Raw Phase 2C h5ad outputs retained locally and intentionally not copied into the submission package.

## Blocking Release Items

- No top-level LICENSE file was found.
- No top-level `requirements.txt`, `environment.yml`, or `pyproject.toml` was found during audit.
- README is older than the final Phase 2A/2B/2C state and should be updated before repository release.
- Data availability language must state the filtered Replogle scope and identify external datasets precisely.
- Large local raw outputs should remain excluded or moved to a formal data repository if required.

## Safe Next Cleanup

Add a license selected by the user, export a minimal reproducible environment, update README with frozen run commands and limitations, and prepare a release manifest listing exactly which files are included.
