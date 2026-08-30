# Minimal VirtualPerturb-Audit Example

This toy example demonstrates the mechanics of the audit workflow. It is not manuscript evidence.

Run:

```bash
python run_minimal_audit.py
```

Inputs: `toy_predictions.csv` with perturbation, gene, true delta, and predicted delta columns.

Outputs: `minimal_audit_table.csv` with audit-delta Pearson, retrieval rank, MRR contribution, UER@2, and sign-flip rate.
