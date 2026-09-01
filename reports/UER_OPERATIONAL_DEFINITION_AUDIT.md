# UER Operational Definition Audit v1.3

Status: COMPLETE.

UER is an internal sensitivity measure. It is not validated biological replicate ground truth and is not evidence of experimental hallucination by itself.

## Frozen Pseudocode

```text
input: pred_delta, true_delta, k, null_abs_threshold
order = argsort(descending abs(pred_delta))[0:k]
unsupported = abs(true_delta[order]) <= null_abs_threshold
UER@K = mean(unsupported)
```

In the GEARS and Replogle baseline scripts, `null_abs_threshold` is the 50th percentile of `abs(true_delta)` for the evaluated perturbation vector unless a frozen upstream table already supplies the value. In the STATE Phase 2C script, the same median absolute observed audit-delta rule is used and recorded as `median_abs_audit_delta` or `median_abs_raw_delta` depending on metric space. UER50 is emphasized in the manuscript. Secondary null/bound language is retained only in supplementary and reporting material because validated replicate metadata are unavailable.
