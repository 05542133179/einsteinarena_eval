import math

MAX_ORDER = 20


def evaluate(solution: dict) -> float:
    matrix = solution["matrix"]
    if not isinstance(matrix, list) or not 1 <= len(matrix) <= MAX_ORDER:
        raise ValueError("Matrix order must be between 1 and 20")

    n = len(matrix)
    row_masks = []
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("Matrix must be square")
        mask = 0
        for j, value in enumerate(row):
            if isinstance(value, bool) or not isinstance(value, int) or value not in (-1, 1):
                raise ValueError("Matrix entries must be exactly -1 or 1")
            if value == -1:
                mask |= 1 << j
        row_masks.append(mask)

    discrepancy = n
    for signs in range(1 << n):
        worst = max(abs(n - 2 * (signs ^ row).bit_count()) for row in row_masks)
        if worst < discrepancy:
            discrepancy = worst

    return float(discrepancy / math.sqrt(n))