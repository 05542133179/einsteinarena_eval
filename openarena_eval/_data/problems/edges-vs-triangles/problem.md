# Edges vs Triangles (Minimal Triangle Density)

## Problem

For $0 \le \rho \le 1$, let $C(\rho)$ denote the largest quantity such that any graph on $n$ vertices and $(\rho + o(1))\binom{n}{2}$ edges will have at least $(C(\rho) - o(1))\binom{n}{3}$ triangles. What is $C(\rho)$?

This is the Razborov flag-algebra problem on the minimum triangle density as a function of edge density. The goal is to construct a tight lower bound on $C(\rho)$ over the full range $\rho \in [0,1]$.

## Encoding

Each row of the solution is a probability distribution over 20 bins. The verifier computes edge density and triangle density per row using Newton's power-sum identities. Each point $(\rho_i, t_i)$ extends a horizontal line to the left and a line of slope 3 to the right. The area under the lower envelope of these lines is an upper bound on $\int_0^1 C(\rho)\,d\rho$.

## Scoring

Submit `weights` — a 2D array of shape $(m, 20)$ where $m \le 500$ and each row has non-negative entries (rows are normalized to sum to 1). The score is

$$\text{score} = -(\text{area} + 10 \cdot \text{max\_gap})$$

where $\text{max\_gap}$ is the largest gap between consecutive edge densities. Higher (less negative) is better. The gap penalty encourages dense coverage of the $\rho$ axis.

## Reference

Problem 6.46 of [Mathematical exploration and discovery at scale](https://arxiv.org/abs/2511.02864)

- Scoring: `maximize`
- Minimum improvement: `1e-06`
- Official API: https://einsteinarena.com/api/problems/edges-vs-triangles

## Candidate schema

```json
{
  "weights": "2D array of shape (m, 20), each row non-negative"
}
```
