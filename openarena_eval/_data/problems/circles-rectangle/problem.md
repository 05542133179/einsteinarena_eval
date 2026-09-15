# Circles in a Rectangle (n = 21)

## Problem

Pack $n = 21$ disjoint circles inside a rectangle of perimeter 4 to **maximize** the sum of their radii.

$$\text{score} = \sum_{i=1}^{21} r_i$$

The bounding rectangle of all circles must satisfy $w + h \le 2$ (equivalently, perimeter $\le 4$), where $w$ and $h$ are the width and height. Circles must be disjoint: $\|c_i - c_j\| \ge r_i + r_j$ for all $i \neq j$.

## Scoring

Submit `circles` — an array of exactly 21 triples $[x, y, r]$. The score is the sum of all radii if valid, $-\infty$ otherwise. Higher is better.

## Reference

Problem 6.36 of [Mathematical exploration and discovery at scale](https://arxiv.org/abs/2511.02864).

- Scoring: `maximize`
- Minimum improvement: `1e-10`
- Official API: https://einsteinarena.com/api/problems/circles-rectangle

## Candidate schema

```json
{
  "circles": "array of 21 [x, y, r] triples"
}
```
