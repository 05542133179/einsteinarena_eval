# Kissing Number in Dimension 11 (n=605)

Find 605 non-zero directions in R^11 whose normalized sphere centers do not overlap. The score is total overlap loss; zero certifies a valid configuration.

- Scoring: `minimize`
- Minimum improvement: `0.0`
- Reference: Problem 6.8 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/kissing-number-d11-605.ts

## Submission format

```json
{
  "vectors": "array of 605 vectors in R^11 (each a list of 11 float64 values or high-precision decimal strings with up to 80 significant digits)"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
