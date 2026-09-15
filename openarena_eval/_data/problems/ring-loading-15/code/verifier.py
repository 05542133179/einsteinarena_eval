import re
from fractions import Fraction

PAIR_COUNT = 15
MAX_RATIONAL_BITS = 64
RATIONAL_PATTERN = re.compile(r"^(?:0|[1-9]\d*)(?:(?:\.\d+)|(?:/[1-9]\d*))?$")


def parse_rational(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 80:
        raise ValueError("Values must be rational strings")
    if RATIONAL_PATTERN.fullmatch(value) is None:
        raise ValueError("Values must be nonnegative decimals or fractions")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise ValueError("Values must be nonnegative decimals or fractions")
    if result < 0:
        raise ValueError("Values must be nonnegative")
    if result.numerator.bit_length() > MAX_RATIONAL_BITS or result.denominator.bit_length() > MAX_RATIONAL_BITS:
        raise ValueError("Reduced numerator and denominator must fit in 64 bits")
    return result


def evaluate(solution: dict) -> float:
    pairs = solution["pairs"]
    if not isinstance(pairs, list) or len(pairs) != PAIR_COUNT:
        raise ValueError("Expected exactly 15 pairs")

    checked = []
    for pair in pairs:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("Each entry must be a pair [u, v]")
        u = parse_rational(pair[0])
        v = parse_rational(pair[1])
        if u + v > 1:
            raise ValueError("Every pair must satisfy u + v <= 1")
        checked.append((u, v))

    best = None
    for mask in range(1 << PAIR_COUNT):
        values = [
            -u if mask & (1 << i) else v
            for i, (u, v) in enumerate(checked)
        ]
        total = sum(values, Fraction(0))
        prefix = Fraction(0)
        worst = Fraction(0)
        for value in values:
            prefix += value
            worst = max(worst, abs(2 * prefix - total))
        if best is None or worst < best:
            best = worst

    return float(best)