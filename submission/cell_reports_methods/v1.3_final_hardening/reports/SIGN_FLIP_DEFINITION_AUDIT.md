# Sign-Flip Definition Audit v1.3

Status: COMPLETE.

The implemented sign-flip endpoint identifies supported genes using an observed-effect threshold, then compares predicted and observed directions.

## Frozen Pseudocode

```text
input: pred_delta, true_delta, support_threshold
supported = abs(true_delta) > support_threshold
flip = sign(pred_delta[supported]) != sign(true_delta[supported])
sign_flip_rate = mean(flip)
major_flip = flip and abs(pred_delta[supported]) > support_threshold
major_sign_flip_rate = mean(major_flip)
```

The frozen scripts set `support_threshold` to the 95th percentile of absolute observed delta within the evaluated perturbation/gene vector. The main manuscript reports sign-flip rate; major sign-flip remains an implementation output when available.
