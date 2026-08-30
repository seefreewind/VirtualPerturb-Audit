# VirtualPerturb-Audit

VirtualPerturb-Audit is a falsification framework for perturbation-response model evaluation. It asks which model-performance claims survive when global transcriptomic similarity is separated from perturbation-specific retrieval, unsupported-effect behavior, sign-flip rate, leakage risk, and matched-target context transfer.

## What Problem Does It Solve?

Aggregate expression similarity can make a perturbation-response model look reliable even when target retrieval or cross-context transfer is weak. This repository turns those concerns into an auditable workflow with frozen splits, endpoint-specific tables, probe controls, and claim-evidence reports.

## Main Audit Dimensions

- Raw-space global transcriptomic similarity
- Control-subtracted audit-delta agreement
- Perturbation-specific retrieval
- Unsupported-effect rate, reported as sensitivity-only UER
- Sign-flip rate
- Matched-target context transfer
- Falsification probes and baseline controls

## Supported Example Datasets

- Norman perturbation data through a GEARS-compatible processed mirror
- GEARS-compatible filtered Replogle K562 and RPE1 essential-screen data

The current Replogle analyses do not use the complete Figshare+ processed objects.

## Quick Start

Inspect the frozen CRM package:

```bash
ls submission/cell_reports_methods/final
```

Regenerate the v1.1 submission-preparation package from frozen outputs:

```bash
environment/state-postprocess-venv/bin/python scripts/finalize_crm_submission_v11.py
```

Regenerate the earlier CRM v1.0 package:

```bash
environment/state-postprocess-venv/bin/python scripts/build_crm_submission_package.py
```

## Expected Outputs

- `manuscript/CRM_MANUSCRIPT_v1.1.md`
- `manuscript/CRM_MANUSCRIPT_v1.1.docx`
- `manuscript/CRM_SUPPLEMENT_v1.1.md`
- `figures/main/crm_figure4_matched_gears_transfer_v11.*`
- `figures/main/crm_figure5_state_partial_confirmation_v11.*`
- `reports/CRM_SUBMISSION_READINESS_FINAL.md`
- `submission/cell_reports_methods/final/`

## Reproduction Commands

The finalization script does not train models. It reads frozen tables under `results/tables/` and writes manuscript, figure, audit, and submission files. Earlier GEARS and STATE training commands are retained in phase-specific reports.

## Known Limitations

- Replogle scope is GEARS-compatible filtered essential-screen data.
- BNS remains unverified because validated biological replicate metadata were unavailable.
- UER is sensitivity-only because its null is not derived from validated biological replicate ground truth.
- GEARS R-L4 is a cross-context inference adapter.
- STATE support is partial and endpoint-heterogeneous.
- GEARS and STATE absolute metrics are not a direct universal model leaderboard.
