# Circle Packing in a Square

Pack 26 non-overlapping circles inside the unit square to maximize the sum of their radii. Every circle must be contained in [0,1]^2.

- Scoring: `maximize`
- Minimum improvement: `1e-10`
- Reference: Problem 6.36 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/circle-packing.ts

## Submission format

```json
{
  "circles": "array of [x, y, r] triples"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
