# Second Autocorrelation Inequality (Lower Bound)

Find a non-negative discretized function maximizing the L2-squared autoconvolution ratio divided by its L1 and L-infinity norms.

- Scoring: `maximize`
- Minimum improvement: `1e-05`
- Reference: Problem 6.3 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/second-autocorrelation-inequality.ts

## Submission format

```json
{
  "values": "array of non-negative floats (the discretized function values)"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
