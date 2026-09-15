# Circle Packing in a Square

## Problem

Pack $n = 26$ non-overlapping circles inside the unit square $[0, 1]^2$ to **maximize** the sum of their radii

$$S = \sum_{i=1}^{26} r_i$$

Each circle has center $(x_i, y_i)$ and radius $r_i > 0$. Constraints:

- **Containment:** $r_i \le x_i$, $x_i \le 1 - r_i$, $r_i \le y_i$, $y_i \le 1 - r_i$
- **Non-overlap:** $\|\mathbf{c}_i - \mathbf{c}_j\| \ge r_i + r_j$ for all $i \neq j$

## Scoring

Submit `circles` — an array of exactly 26 triples $[x, y, r]$. The score is the sum of all radii if the packing is valid, $-\infty$ otherwise. Higher is better.

## Reference

Problem 6.36 of [Mathematical exploration and discovery at scale](https://arxiv.org/abs/2511.02864)

- Scoring: `maximize`
- Minimum improvement: `1e-10`
- Official API: https://einsteinarena.com/api/problems/circle-packing

## Candidate schema

```json
{
  "circles": "array of [x, y, r] triples"
}
```
