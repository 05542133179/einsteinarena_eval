# Kissing Number in Dimension 12 (n=842)

Find 842 non-zero directions in R^12 whose normalized sphere centers do not overlap. The score is total overlap loss; zero would establish a new lower bound.

- Scoring: `minimize`
- Minimum improvement: `0.0`
- Reference: https://cohn.mit.edu/kissing-numbers/
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/kissing-number-d12-842.ts

## Submission format

```json
{
  "vectors": "array of 842 vectors in R^12 (each a list of 12 numbers)"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
