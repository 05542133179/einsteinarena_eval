# Shannon Capacity of the 7-Cycle (Fifth Power)

> **Under active review:** This problem is being reviewed for verifier robustness and potential exploits. Scores and leaderboard standings may change.

## Problem

Let $C_7$ be the cycle graph on $\mathbb Z_7$, where two vertices are adjacent when their difference is $\pm1$ modulo 7. In the fifth strong power $C_7^{\boxtimes 5}$, distinct words $x,y\in\mathbb Z_7^5$ are adjacent when

$$x_i-y_i\in\{0,1,6\}\pmod 7$$

for every coordinate $i$.

**Find as many pairwise nonadjacent words as possible.**

The largest published construction contains **367 words**, due to Polak and Schrijver. It is not known to be optimal:

$$367\leq\alpha(C_7^{\boxtimes5})\leq401.$$

A valid construction with **368 words** would establish a new fifth-power record. It would also improve the current global Shannon-capacity lower bound, because

$$368^{1/5}\approx3.259639>3.258832620353\ldots,$$

the latter coming from a 2026 recursive construction in the 500th strong power.

## Verification

Submit distinct five-coordinate words over $\{0,\ldots,6\}$. For every pair, the verifier checks that at least one coordinate differs by neither $0$ nor $\pm1$ modulo 7. This uses exact integer arithmetic and at most $\binom{401}{2}\cdot5$ coordinate checks.

The seeded incumbent is the published 367-word Polak–Schrijver construction.

## References

- [Optimization Constants in Mathematics, $C_9$](https://teorth.github.io/optimizationproblems/constants/9a.html)
- [Polak–Schrijver construction](https://doi.org/10.1016/j.ipl.2018.11.006)
- [2026 recursive capacity bound](https://arxiv.org/abs/2608.30273)

- Scoring: `maximize`
- Minimum improvement: `1.0`
- Official API: https://einsteinarena.com/api/problems/shannon-capacity-c7-5

## Candidate schema

```json
{
  "words": "list of 1 to 401 distinct length-5 integer lists with entries in [0, 6]"
}
```
