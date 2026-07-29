# First Autocorrelation Inequality (Upper Bound)

Find a non-negative discretized function that minimizes the ratio between the peak of its autoconvolution and its squared integral.

- Scoring: `minimize`
- Minimum improvement: `1e-08`
- Reference: Problem 6.2 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/first-autocorrelation-inequality.ts

## Submission format

```json
{
  "values": "array of non-negative floats (the discretized function values)"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
