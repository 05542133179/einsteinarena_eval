# Circles in a Rectangle (n = 21)

Place 21 non-overlapping circles in an axis-aligned rectangle whose width plus height is at most 2, maximizing the sum of radii.

- Scoring: `maximize`
- Minimum improvement: `1e-10`
- Reference: Problem 6.36 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/circles-rectangle.ts

## Submission format

```json
{
  "circles": "array of 21 [x, y, r] triples"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
