MAX_POINTS = 150
GRID_MAX = 74


def evaluate(solution: dict) -> float:
    points = solution["points"]
    if not isinstance(points, list) or not 1 <= len(points) <= MAX_POINTS:
        raise ValueError("Expected between 1 and 150 points")

    checked = []
    for point in points:
        if not isinstance(point, list) or len(point) != 2:
            raise ValueError("Every point must be an [x, y] pair")
        x, y = point
        if (
            isinstance(x, bool)
            or isinstance(y, bool)
            or not isinstance(x, int)
            or not isinstance(y, int)
        ):
            raise ValueError("Coordinates must be integers")
        if not 0 <= x <= GRID_MAX or not 0 <= y <= GRID_MAX:
            raise ValueError("Coordinates must lie in [0, 74]")
        checked.append((x, y))

    if len(set(checked)) != len(checked):
        raise ValueError("Points must be distinct")

    for i in range(len(checked) - 2):
        x1, y1 = checked[i]
        for j in range(i + 1, len(checked) - 1):
            x2, y2 = checked[j]
            dx = x2 - x1
            dy = y2 - y1
            for k in range(j + 1, len(checked)):
                x3, y3 = checked[k]
                if dx * (y3 - y1) - dy * (x3 - x1) == 0:
                    raise ValueError("Three points are collinear")

    return float(len(checked))