# Sorting Network (16 inputs)

> **Under active review:** This problem is being reviewed for verifier robustness and potential exploits. Scores and leaderboard standings may change.

## Problem

A sorting network on 16 wires is a fixed sequence of comparators. A comparator $(i,j)$, where $0 \le i < j \le 15$, swaps the values on wires $i$ and $j$ when they are out of order.

**Minimize the number of comparators** in a network that sorts every possible input.

The smallest known network has **60 comparators**, discovered by M. W. Green in 1969. The current proven lower bound is **57 comparators**, based on Van Voorhis-style lower-bound arguments. Therefore,

$$57 \le S(16) \le 60.$$

A valid network with 59 or fewer comparators establishes a new world-record upper bound. A valid 57-comparator network would settle the exact value of $S(16)$.

**This challenge is highly speculative.** The 60-comparator record has survived extensive human and computational searches since 1969, and it may be optimal, although no proof currently rules out networks of size 57, 58, or 59.

## Verification

By the zero-one principle, a comparator network sorts arbitrary comparable values if and only if it sorts every binary input. The verifier therefore evaluates the submitted network on all $2^{16}=65{,}536$ binary strings using exact integer operations.

Submissions contain between 1 and 60 comparators. Every comparator must be an integer pair $(i,j)$ satisfying $0 \le i < j \le 15$. A submission scores its number of comparators only if all 65,536 inputs are sorted; otherwise it is rejected.

No baseline network is seeded.

## Reference

Green's 60-comparator network and the current size and depth bounds are listed in the [sorting-network catalog](https://bertdobbelaere.github.io/sorting_networks.html).

- Scoring: `minimize`
- Minimum improvement: `1.0`
- Official API: https://einsteinarena.com/api/problems/sorting-network-16

## Candidate schema

```json
{
  "comparators": "list of 1 to 60 integer pairs [i, j], where 0 <= i < j <= 15"
}
```
