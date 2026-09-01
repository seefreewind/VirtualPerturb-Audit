# GitHub Upload Report

Date: 2026-09-01

Repository: https://github.com/seefreewind/VirtualPerturb-Audit

## Upload status

The public GitHub repository has been created and populated with the necessary project code, derived manuscript-facing data, figures, reports, tests, and manuscript materials for VirtualPerturb-Audit.

Remote default branch: `main`

Remote upload commit verified before this report: `a294217cf7ea417011c4075cebc2dee70edfc2b2`

Local source commit before this report: `b74a2cd` (`Add public repository URL to CRM materials`)

## Uploaded content

The upload includes:

- Project documentation: `README.md`, `REPRODUCIBILITY.md`, provenance files, plan/status files, license, and citation metadata.
- Source code and package files: `src/`, `scripts/`, `models/`, `configs/`, `examples/`, and `tests/`.
- Manuscript-facing outputs: `manuscript/`, including `CRM_MANUSCRIPT_v1.6_FULL.md` and `CRM_MANUSCRIPT_v1.6_FULL.docx`.
- Main figures: `figures/main/Figure1*` through `figures/main/Figure5*`, including PNG, SVG, and PDF exports.
- Derived tables used in manuscript interpretation and plotting: `results/tables/`.
- Audit and delivery reports: `reports/`.
- Submission support files: `submission/`.

## Intentionally excluded content

The following content was intentionally not uploaded because it is raw, large, runtime-specific, externally generated, or reproducible from the documented workflow:

- Raw downloaded datasets under `data/raw/`.
- Large processed data objects under `data/processed/`.
- Large GEARS and STATE run outputs under `results/replogle/gears/` and `results/state/`.
- External dependency checkouts under `external/`.
- Local runtime or environment folders under `environment/`.
- Operating-system sidecar files such as AppleDouble `._*` files and Word temporary lock files.

These exclusions are consistent with the repository's reproducibility policy: GitHub contains code, compact derived results, manuscript figures, and documentation, while large/raw artifacts require separate archival deposition when a DOI is prepared.

## Verification checks

Remote checks were performed using the GitHub CLI and GitHub API after the initial push.

Confirmed remote root contains project files directly, with no extra nested `VirtualPerturb-Audit/` wrapper.

Confirmed representative remote files:

- `scripts/build_figure5_v2.py`
- `results/tables/figure5_direction_aligned_effects.tsv`
- `results/tables/state_transfer_drop.csv`
- `figures/main/Figure1.png`
- `figures/main/Figure2_v2.png`
- `figures/main/Figure3_v2.png`
- `figures/main/Figure4_v2.png`
- `figures/main/Figure5_v2.png`
- `manuscript/CRM_MANUSCRIPT_v1.5.docx`
- `manuscript/CRM_MANUSCRIPT_v1.6_FULL.docx`
- `manuscript/CRM_MANUSCRIPT_v1.6_FULL.md`

Local test suite after repository URL updates:

```text
PYTHONPATH=. pytest -q tests
13 passed
```

## Remaining repository-related item

The public GitHub repository is available. The archival code/result DOI remains pending and should be completed before journal submission if required by the target journal or reviewer request.
