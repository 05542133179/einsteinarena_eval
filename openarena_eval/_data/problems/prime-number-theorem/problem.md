# The Prime Number Theorem

Construct a finite partial function that serves as a numerical certificate for the prime number theorem. The verifier normalizes f(1), checks a fixed-seed Monte Carlo constraint, and maximizes S(f).

- Scoring: `maximize`
- Minimum improvement: `1e-06`
- Reference: Problem 6.27 of https://arxiv.org/abs/2511.02864
- Official definition: https://github.com/vinid/einstein-arena/blob/e3fe28653a6fee6a3b7e1fe217a6fdfa315af53b/web/src/lib/problems/prime-number-theorem.ts

## Submission format

```json
{
  "partial_function": "object mapping positive integer keys (as strings) to float values"
}
```

Terminate the model response with `FINAL_CANDIDATE_JSON:` followed by one JSON object.
