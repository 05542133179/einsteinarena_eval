from itertools import combinations

MIN_SIZE = 4
MAX_SIZE = 18
MAX_ABS_VALUE = 1_000_000_000


def is_sidon(subset):
    sums = set()
    for i, left in enumerate(subset):
        for right in subset[i:]:
            value = left + right
            if value in sums:
                return False
            sums.add(value)
    return True


def evaluate(solution: dict) -> float:
    elements = solution["elements"]
    if not isinstance(elements, list) or not MIN_SIZE <= len(elements) <= MAX_SIZE:
        raise ValueError("Expected between 4 and 18 elements")
    if any(
        isinstance(x, bool)
        or not isinstance(x, int)
        or abs(x) > MAX_ABS_VALUE
        for x in elements
    ):
        raise ValueError("Elements must be integers in [-1e9, 1e9]")
    if len(set(elements)) != len(elements):
        raise ValueError("Elements must be distinct")

    ordered = sorted(elements)
    for four in combinations(ordered, 4):
        differences = {
            four[j] - four[i]
            for i in range(4)
            for j in range(i + 1, 4)
        }
        if len(differences) < 5:
            raise ValueError("The submitted set is not a (4,5)-set")

    for size in range(len(ordered), 0, -1):
        if any(is_sidon(subset) for subset in combinations(ordered, size)):
            return float(size / len(ordered))

    raise RuntimeError("No Sidon subset found")