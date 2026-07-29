# Difference Bases

Construct a finite non-negative integer set B whose pairwise differences cover the longest possible initial interval while minimizing |B|^2/n.

- Scoring: `minimize`
- Minimum improvement: `1e-09`
- Reference: Problem 6.7 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/difference-bases.ts

## Submission format

```json
{
  "set": "list of non-negative integers (up to 2000 elements)"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
