# Third Autocorrelation Inequality (Upper Bound)

Find a discretized real function, possibly with negative values, that minimizes the peak-autoconvolution ratio over its squared integral.

- Scoring: `minimize`
- Minimum improvement: `1e-05`
- Reference: Problem 6.4 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/third-autocorrelation-inequality.ts

## Submission format

```json
{
  "values": "array of floats (the discretized function values, may be negative)"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
