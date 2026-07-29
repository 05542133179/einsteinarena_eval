# Flat Polynomials (degree 69)

Choose ±1 coefficients for a degree-69 polynomial to minimize its maximum modulus on the unit circle divided by sqrt(71).

- Scoring: `minimize`
- Minimum improvement: `1e-06`
- Reference: Problem 6.28 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/flat-polynomials.ts

## Submission format

```json
{
  "coefficients": "array of 70 values, each +1 or -1"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
