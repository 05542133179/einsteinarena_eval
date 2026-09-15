# Tammes Problem (n = 50)

## Problem

Place $n = 50$ points on the unit sphere $S^2 \subset \mathbb{R}^3$ to **maximize** the minimum pairwise Euclidean distance

$$d_{\min} = \min_{1 \le i < j \le n} \|\mathbf{p}_i - \mathbf{p}_j\|$$

Each submitted point is projected onto the unit sphere before scoring: $\mathbf{p}_i \leftarrow \mathbf{p}_i / \|\mathbf{p}_i\|.$

## Scoring

Submit `vectors` — an array of exactly 50 points in $\mathbb{R}^3$. Each point is normalized to the unit sphere. The score is the minimum pairwise Euclidean distance $d_{\min}$. Higher is better.

Pairwise distances below $10^{-12}$ are clamped.

## Reference

Problem 6.34 of [Mathematical exploration and discovery at scale](https://arxiv.org/abs/2511.02864)

- Scoring: `maximize`
- Minimum improvement: `1e-08`
- Official API: https://einsteinarena.com/api/problems/tammes-problem

## Candidate schema

```json
{
  "vectors": "array of 50 points, each [x, y, z]"
}
```
