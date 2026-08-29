# scGPT Feasibility Audit

更新时间：2026-08-29

## Verdict

```yaml
official_feasibility: FAIRLY_EVALUABLE_IN_PRINCIPLE
local_phase2b_verdict: NOT_FAIRLY_EVALUABLE
selected_as_second_model: false
primary_reason: local reproducible import/smoke environment could not be established without major environment replacement
phase2b_action: proceed_to_STATE_feasibility_audit
```

scGPT has enough official material to be considered a legitimate perturbation-prediction candidate in principle: public code, an official perturbation tutorial, PyPI releases, pretrained checkpoint links, and an MIT license. It was not selected for this Phase 2B local replication because the available Mac/external-drive environment could not produce a clean, reproducible scGPT import and smoke run without destabilizing the already frozen GEARS environment.

## Official Source Audit

```yaml
repository: https://github.com/bowang-lab/scGPT
repository_status: official codebase
commit_checked: cebd6fae655b9c585a4807daa3ac31bb764f06b4
latest_pypi_version_seen: 0.2.4
pyproject_version_on_main: 0.2.5
license: MIT
official_docs: https://scgpt.readthedocs.io/en/latest/
official_perturbation_tutorial: https://github.com/bowang-lab/scGPT/blob/main/tutorials/Tutorial_Perturbation.ipynb
checkpoint: scGPT whole-human recommended checkpoint
checkpoint_source: Google Drive model zoo link in official README
pretraining_data_claim: 33 million normal human cells for the whole-human checkpoint
perturbation_prediction_supported: true
genetic_perturbation_supported: true
custom_dataset_supported: true_via_GEARS_PertData_compatible_dataset_folder
cross_context_supported: adapter_required_not_native
```

## Evidence From Official Materials

- The official README identifies the repository as the scGPT codebase and lists installation through `pip install scgpt`.
- The official README lists pretrained model zoo checkpoints and states that each checkpoint folder includes a paired gene vocabulary.
- The official perturbation tutorial is explicitly organized around perturbation prediction and uses GEARS `PertData`, PyG data loaders, `TransformerGenerator`, perturbation flags, pretrained model loading, `vocab.json`, and perturbed-expression prediction from control inputs.
- The official documentation describes genetic perturbation prediction as a supported downstream task.

## Local Execution Audit

### Existing GEARS Environment

The existing GEARS environment was tested first because it already contains the audited GEARS datasets, split tooling, and working PyTorch stack.

```yaml
environment: environment/gears-venv
cell_gears_restored_version: 0.1.2
scgpt_attempted_version: 0.2.4
torch_version: 2.8.0
torchtext_version: 0.18.0
result: failed
```

Observed blockers:

- Installing `scgpt==0.2.4` downgraded `cell-gears` toward the old `cell-gears<0.0.3` dependency range, conflicting with the project GEARS installation. `cell-gears==0.1.2` was restored immediately to protect frozen GEARS reproducibility.
- `torchtext` could not import cleanly against the current PyTorch stack because `libtorchtext.so` raised an ABI symbol error.
- `scgpt` import also required additional interactive/notebook dependencies such as `IPython`.

This path was rejected because repairing it would require replacing the PyTorch/GEARS dependency stack used for the frozen benchmark.

### Isolated scGPT Environment

An isolated environment was then attempted to avoid contaminating GEARS.

```yaml
environment: environment/scgpt-venv
attempted_stack:
  - scgpt==0.2.4
  - torch==2.3.0
  - torchtext==0.18.0
  - torch-geometric==2.6.1
  - ipython
result: failed_incomplete_environment
```

Observed blockers:

- The external exFAT volume generated AppleDouble `._*` files inside the virtual environment, producing Python `.pth` Unicode decode failures during package operations.
- The long install did not leave a valid environment: `torch` failed to import because `libtorch_global_deps.dylib` was missing, and `scgpt`, `torchtext`, `torch_geometric`, and `IPython` were not importable.

This path was rejected because it did not reach a clean import smoke test.

## Fairness Decision

Calling a partially repaired, locally modified scGPT stack a confirmatory second model would weaken the audit. The project can truthfully state that scGPT was audited as an official candidate but was not fairly executable in this Phase 2B local environment.

```text
SCGPT_LOCAL_VERDICT = NOT_FAIRLY_EVALUABLE
SECOND_MODEL = NOT_SCGPT
NEXT_ACTION = AUDIT_STATE
```
