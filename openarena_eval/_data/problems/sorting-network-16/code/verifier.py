import numpy as np

N = 16
MAX_COMPARATORS = 60


def evaluate(data):
    comparators = data["comparators"]
    if not isinstance(comparators, list) or not 1 <= len(comparators) <= MAX_COMPARATORS:
        raise ValueError("Expected between 1 and 60 comparators")

    checked = []
    for comparator in comparators:
        if not isinstance(comparator, list) or len(comparator) != 2:
            raise ValueError("Each comparator must be a pair [i, j]")
        i, j = comparator
        if isinstance(i, bool) or isinstance(j, bool) or not isinstance(i, int) or not isinstance(j, int):
            raise ValueError("Comparator indices must be integers")
        if not 0 <= i < j < N:
            raise ValueError("Each comparator must satisfy 0 <= i < j <= 15")
        checked.append((i, j))

    values = (
        (
            np.arange(1 << N, dtype=np.uint32)[:, None]
            >> np.arange(N, dtype=np.uint32)
        )
        & 1
    ).astype(np.uint8)

    for i, j in checked:
        left = values[:, i].copy()
        right = values[:, j].copy()
        values[:, i] = np.minimum(left, right)
        values[:, j] = np.maximum(left, right)

    if np.any(values[:, :-1] > values[:, 1:]):
        return float("inf")

    return float(len(checked))