import numpy as np
import itertools

def evaluate(data):
    circles = np.array(data["circles"], dtype=np.float64)
    if circles.shape != (21, 3):
        return -float("inf")
    if not np.isfinite(circles).all():
        return -float("inf")
    radii = circles[:, 2]
    if not (radii > 0).all():
        return -float("inf")
    min_x = np.min(circles[:, 0] - radii)
    max_x = np.max(circles[:, 0] + radii)
    min_y = np.min(circles[:, 1] - radii)
    max_y = np.max(circles[:, 1] + radii)
    width = max_x - min_x
    height = max_y - min_y
    if width + height > 2 + 1e-9:
        return -float("inf")
    for c1, c2 in itertools.combinations(circles, 2):
        dist = np.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
        if dist < c1[2] + c2[2] - 1e-9:
            return -float("inf")
    return float(np.sum(radii))