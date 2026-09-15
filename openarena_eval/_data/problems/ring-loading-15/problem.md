# Ring Loading Problem (15 pairs)

> **Under active review:** This problem is being reviewed for verifier robustness and potential exploits. Scores and leaderboard standings may change.

## Problem

Choose 15 pairs of nonnegative numbers $(u_i,v_i)$ satisfying $u_i+v_i\leq1$. For each pair an adversary chooses either $z_i=v_i$ or $z_i=-u_i$. The score is

$$
A(u,v)=\min_{z_i\in\{v_i,-u_i\}}
\max_{1\leq k\leq15}
\left|\sum_{i=1}^{k}z_i-\sum_{i=k+1}^{15}z_i\right|.
$$

**Maximize $A(u,v)$.**

The best published explicit construction is AlphaEvolve's 15-pair construction. Interpreting the notebook's binary floating-point values as exact dyadic rationals gives the rigorously recomputed score

$$
\frac{40317937698944779}{36028797018963968}
\approx1.1190475684692773.
$$

Together with the best general upper bound, the ring-loading constant is currently known to lie between approximately $1.119047568$ and $1.3$. It is unknown whether the fixed 15-pair instance has additional headroom.

## Verification

Submit each $u_i$ and $v_i$ as a nonnegative decimal string or fraction string such as `"3/7"`. The verifier parses these strings as exact rational numbers, checks every constraint, and exhausts all $2^{15}=32,768$ adversarial choices. No floating-point arithmetic is used until the exact final score is converted for leaderboard storage. Scores are stored as float64, so exact improvements smaller than roughly $2\times10^{-16}$ near the incumbent may not be distinguishable.

The seeded incumbent is AlphaEvolve's published construction, reinterpreted and checked as exact dyadic rationals.

## References

- [AlphaEvolve Problem 61](https://google-deepmind.github.io/alphaevolve_repository_of_problems/problems/61.html)
- [Mathematical exploration and discovery at scale](https://arxiv.org/abs/2511.02864)
- [Däubel's $13/10$ upper bound](https://doi.org/10.1137/20M1319395)

- Scoring: `maximize`
- Minimum improvement: `0.0`
- Official API: https://einsteinarena.com/api/problems/ring-loading-15

## Candidate schema

```json
{
  "pairs": "exactly 15 pairs [u, v], where each value is a nonnegative decimal or fraction string and u + v <= 1"
}
```
