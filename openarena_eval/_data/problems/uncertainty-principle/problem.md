# Uncertainty Principle (Upper Bound)

Choose Laguerre double-root positions for an auxiliary-function linear program that minimizes an upper bound for the uncertainty principle constant.

- Scoring: `minimize`
- Minimum improvement: `1e-06`
- Reference: Problem 6.11 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/uncertainty-principle.ts

## Submission format

```json
{
  "laguerre_double_roots": "list of 1 to 25 positive reals (double root positions, each <= 300)"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
