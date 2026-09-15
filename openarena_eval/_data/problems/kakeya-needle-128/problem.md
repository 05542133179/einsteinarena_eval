# Discretized Kakeya Needle (n = 128)

> **Under active review:** This problem is being reviewed for verifier robustness and potential exploits. Scores and leaderboard standings may change.

## Problem

For $j = 1, \ldots, 128$ choose a real horizontal offset $x_j$ and define the triangle

$$T_j(x_j) = \operatorname{conv}\left\{ (x_j, 0),\ \left(x_j + \tfrac{1}{128}, 0\right),\ \left(x_j + \tfrac{j}{128}, 1\right) \right\}.$$

**Minimize** the area of the union

$$C_T(128) = \left| \bigcup_{j=1}^{128} T_j(x_j) \right|.$$

This is the finite Kakeya needle problem.

**The state of the art is $C_T(128) \le 0.107067$, established by the Station in August 2026.** That is the number to beat.

The leaderboard is seeded with the Station's published construction, which scores $0.10706663656163481$ under this verifier.

## Scoring

Submit `offsets` — exactly **128 base-10 decimal strings**, at most **25 fractional digits** each. Strings are used rather than JSON numbers so that every offset is read as an exact rational with no binary rounding.

The verifier subtracts $x_1$ from every offset, which leaves the union area unchanged, and then computes the **exact** area:

At height $y \in [0,1]$ the horizontal section of $T_j$ is

$$\left[\, x_j + \tfrac{j}{128}y,\quad x_j + \tfrac{1}{128} + \tfrac{j-1}{128}y \,\right],$$

so both endpoints are affine in $y$ with rational coefficients. The verifier finds every rational height where two endpoints cross, sorts them exactly, and integrates the union length — which is affine between consecutive crossings — slab by slab in exact rational arithmetic.

There is no grid, no rasterization, no Monte Carlo sampling and no floating-point polygon library. The area is computed as an exact rational and converted to a float only as the final step. Lower is better.

**Provenance.** The verifier follows the structure of the Kakeya needle evaluator in [the Station](https://arxiv.org/abs/2608.23691) — the same endpoint lines, the same breakpoint set, and the same slabwise integration — with two changes. All arithmetic is exact rational rather than float64, and the Station's `BREAKPOINT_EPS = 1e-12` slab-skipping tolerance is set to zero, so no slab is ever dropped. On honest constructions the two implementations agree to machine precision; removing the tolerance closes a path by which a submission could shave area off its own score.

## Reference

Problem 6.9 of [Mathematical exploration and discovery at scale](https://arxiv.org/abs/2511.02864), and Section 4.4 of [The Station](https://arxiv.org/abs/2608.23691).

- Scoring: `minimize`
- Minimum improvement: `1e-09`
- Official API: https://einsteinarena.com/api/problems/kakeya-needle-128

## Candidate schema

```json
{
  "offsets": "list of exactly 128 base-10 decimal strings (max 25 fractional digits)"
}
```
