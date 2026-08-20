#!/usr/bin/env bash
set -euo pipefail

DEVICE="${DEVICE:-cuda}"
EPOCHS="${EPOCHS:-20}"
BATCH_SIZE="${BATCH_SIZE:-16}"
TEST_BATCH_SIZE="${TEST_BATCH_SIZE:-16}"
PYTHON_BIN="${PYTHON_BIN:-environment/gears-venv/bin/python}"

for split in L1 L2 L3; do
  PYTHONPATH=. "${PYTHON_BIN}" scripts/run_gears_pilot.py \
    --audit-split "${split}" \
    --epochs "${EPOCHS}" \
    --batch-size "${BATCH_SIZE}" \
    --test-batch-size "${TEST_BATCH_SIZE}" \
    --device "${DEVICE}"
done

PYTHONPATH=. python3 scripts/run_null_envelope_sensitivity.py
PYTHONPATH=. python3 scripts/build_gene_family_confusion.py
PYTHONPATH=. python3 scripts/build_figures.py
PYTHONPATH=. python3 scripts/build_tables.py
