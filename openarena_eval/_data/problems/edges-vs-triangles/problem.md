# Edges vs Triangles (Minimal Triangle Density)

Submit weighted graphon samples that trace the lower boundary of triangle density versus edge density. The verifier returns the negative area with a coverage-gap penalty; higher is better.

- Scoring: `maximize`
- Minimum improvement: `1e-06`
- Reference: Problem 6.46 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/edges-vs-triangles.ts

## Submission format

```json
{
  "weights": "2D array of shape (m, 20), each row non-negative"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
