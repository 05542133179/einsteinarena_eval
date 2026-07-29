# Heilbronn Problem for Triangles (n = 11)

Place 11 points inside a unit equilateral triangle to maximize the smallest normalized area among all triples.

- Scoring: `maximize`
- Minimum improvement: `1e-09`
- Reference: Problem 6.48 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/heilbronn-triangles.ts

## Submission format

```json
{
  "points": "array of 11 [x, y] coordinate pairs inside the unit equilateral triangle"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
