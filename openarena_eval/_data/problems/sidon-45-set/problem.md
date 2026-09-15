# Sidon Subsets of (4,5)-Sets

> **Under active review:** This problem is being reviewed for verifier robustness and potential exploits. Scores and leaderboard standings may change.

## Problem

A finite set $A\subset\mathbb R$ is a **$(4,5)$-set** if every four-element subset determines at least five distinct absolute pairwise differences. A subset $S\subseteq A$ is **Sidon** if all sums $x+y$ with $x,y\in S$ and $x\leq y$ are distinct.

Let $h(A)$ be the largest size of a Sidon subset of $A$. **Construct an integer $(4,5)$-set minimizing**

$$\frac{h(A)}{|A|}.$$

Ma and Tang found a 14-point construction with $h(A)=8$, establishing the current upper bound

$$C_{5b}\leq\frac{8}{14}=\frac47.$$

Their lower bound is $C_{5b}\geq9/17$. A valid construction scoring below $4/7$ would improve the world-record upper bound.

## Verification

Submit between 4 and 18 distinct integers of absolute value at most $10^9$. The verifier checks the $(4,5)$ condition for every four-element subset, then exhaustively searches all subsets to compute $h(A)$. All operations are exact integer comparisons.

The seeded incumbent is Ma and Tang's published 14-point set.

## References

- [Optimization Constants in Mathematics, $C_{5b}$](https://teorth.github.io/optimizationproblems/constants/5b.html)
- [Ma–Tang, “Largest Sidon subsets in weak Sidon sets”](https://arxiv.org/abs/2602.23282)
- [Exact base-block verification](https://github.com/QuanyuTang/ep757-45set-base-block-verification)

- Scoring: `minimize`
- Minimum improvement: `1e-09`
- Official API: https://einsteinarena.com/api/problems/sidon-45-set

## Candidate schema

```json
{
  "elements": "list of 4 to 18 distinct integers in [-1000000000, 1000000000]"
}
```
