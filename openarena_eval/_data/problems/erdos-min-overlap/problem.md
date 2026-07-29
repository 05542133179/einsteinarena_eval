# Erdős Minimum Overlap (Upper Bound)

Find a step function h:[0,2]→[0,1] with integral 1 that minimizes the maximum overlap integral with its shifted complement.

- Scoring: `minimize`
- Minimum improvement: `1e-07`
- Reference: Problem 6.5 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/erdos-min-overlap.ts

## Submission format

```json
{
  "values": "array of floats (the discretized function values)"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
