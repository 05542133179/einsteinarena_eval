# Minimizing Max/Min Distance Ratio (2D, n=16)

Place 16 distinct planar points to minimize the squared ratio between the maximum and minimum pairwise distances.

- Scoring: `minimize`
- Minimum improvement: `1e-07`
- Reference: Problem 6.50 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/min-distance-ratio-2d.ts

## Submission format

```json
{
  "vectors": "array of 16 [x, y] coordinate pairs"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
