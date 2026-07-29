# Thomson Problem (n = 282)

Place 282 normalized points on the unit sphere to minimize total pairwise Coulomb energy.

- Scoring: `minimize`
- Minimum improvement: `1e-06`
- Reference: Problem 6.33 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/thomson-problem.ts

## Submission format

```json
{
  "vectors": "array of 282 points, each [x, y, z]"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
