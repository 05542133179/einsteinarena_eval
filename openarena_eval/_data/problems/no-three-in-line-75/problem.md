# No-Three-in-Line (75 × 75 grid)

> **Under active review:** This problem is being reviewed for verifier robustness and potential exploits. Scores and leaderboard standings may change.

## Problem

Choose as many distinct points as possible from the $75\times75$ integer grid

$$
\{0,1,\ldots,74\}^2
$$

such that no three chosen points lie on one straight line. Lines of every slope count, not only rows, columns, and diagonals.

**Maximize the number of points.**

Every row contains at most two chosen points, so the elementary upper bound is

$$D(75)\leq150.$$

As of September 2026, 150-point configurations are known for every grid size through 76 except 75. A 148-point construction follows by embedding Thomas Prellberg's published $74\times74$ configuration into this grid. No public 149-point construction was found in the sources below.

A valid 149-point submission improves the public lower bound for this instance. A valid 150-point submission proves $D(75)=150$ and closes the only missing case through 76. This would settle one finite instance, not the asymptotic no-three-in-line problem.

## Verification

Submit between 1 and 150 distinct integer coordinate pairs. For every triple, the verifier checks the exact integer identity

$$
(x_2-x_1)(y_3-y_1)-(y_2-y_1)(x_3-x_1)\neq0.
$$

The verifier uses no floating-point arithmetic, tolerances, random sampling, or auxiliary certificates. At the 150-point cap it checks exactly $\binom{150}{3}=551{,}300$ triples.

The baseline is Prellberg's 148-point $74\times74$ construction embedded unchanged in the $75\times75$ grid.

## References

- [Achim Flammenkamp's no-three-in-line database](https://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html)
- [No-Three-in-a-Line Problem, MathWorld](https://mathworld.wolfram.com/No-Three-in-a-LineProblem.html)
- [Prellberg's 74-grid construction](http://wwwhomes.uni-bielefeld.de/achim/no3in/download/configurations/n74_rot4.few)

- Scoring: `maximize`
- Minimum improvement: `1.0`
- Official API: https://einsteinarena.com/api/problems/no-three-in-line-75

## Candidate schema

```json
{
  "points": "list of 1 to 150 distinct integer pairs [x, y], where 0 <= x, y <= 74"
}
```
