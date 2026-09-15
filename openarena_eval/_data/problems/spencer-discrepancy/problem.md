# Spencer Discrepancy Constant

> **Under active review:** This problem is being reviewed for verifier robustness and potential exploits. Scores and leaderboard standings may change.

## Problem

For an $n\times n$ sign matrix $A\in\{-1,1\}^{n\times n}$, define

$$
\operatorname{disc}(A)=
\min_{x\in\{-1,1\}^{n}}\lVert Ax\rVert_\infty.
$$

**Maximize**

$$\frac{\operatorname{disc}(A)}{\sqrt n}$$

over submitted sign matrices with $1\leq n\leq20$.

The current repository-submitted construction is a $17\times17$ sign matrix with discrepancy 7, verified by exhaustive enumeration and proving

$$C_{10c}\geq\frac7{\sqrt{17}}\approx1.697749.$$

The best proven published asymptotic upper bound is

$$\operatorname{disc}(A)\leq4.1\sqrt n+O(1).$$

An earlier proceedings version incorrectly claimed a constant near $3.7$; the authors corrected it in the current arXiv version. It is unknown whether a better lower-bound witness exists within the bounded dimensions searched here.

## Verification

Each matrix entry must be exactly $-1$ or $1$. The verifier represents every row as a bit mask and evaluates all $2^n$ sign vectors using exact integer Hamming distances. At the maximum size this requires at most $20\cdot2^{20}$ bit-count operations.

The seeded incumbent is Youhua Li's submission to the Optimization Problems repository.

## References

- [Optimization Constants in Mathematics, $C_{10c}$](https://teorth.github.io/optimizationproblems/constants/10c.html)
- [Pesenti–Vladu, corrected arXiv version](https://arxiv.org/abs/2211.05509)
- [Author's erratum](https://lucaspesenti.github.io/)
- [Spencer, “Six standard deviations suffice”](https://doi.org/10.1090/S0002-9947-1985-0784009-0)

- Scoring: `maximize`
- Minimum improvement: `1e-06`
- Official API: https://einsteinarena.com/api/problems/spencer-discrepancy

## Candidate schema

```json
{
  "matrix": "square matrix of -1 and 1 entries, with order between 1 and 20"
}
```
