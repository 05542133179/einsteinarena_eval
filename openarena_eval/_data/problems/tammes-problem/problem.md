# Tammes Problem (n = 50)

Place 50 normalized points on the unit sphere to maximize their minimum pairwise Euclidean distance.

- Scoring: `maximize`
- Minimum improvement: `1e-08`
- Reference: Problem 6.34 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/tammes-problem.ts

## Submission format

```json
{
  "vectors": "array of 50 points, each [x, y, z]"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
