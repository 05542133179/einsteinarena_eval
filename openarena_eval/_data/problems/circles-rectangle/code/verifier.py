import numpy as np
import itertools
from fractions import Fraction

def evaluate(data):
    circles = np.array(data["circles"], dtype=np.float64)
    if circles.shape != (21, 3):
        return -float("inf")
    if not np.isfinite(circles).all():
        return -float("inf")
    radii = circles[:, 2]
    if not (radii > 0).all():
        return -float("inf")
    xs = [Fraction(float(v)) for v in circles[:, 0]]
    ys = [Fraction(float(v)) for v in circles[:, 1]]
    rs = [Fraction(float(v)) for v in radii]
    width = max(x + r for x, r in zip(xs, rs)) - min(x - r for x, r in zip(xs, rs))
    height = max(y + r for y, r in zip(ys, rs)) - min(y - r for y, r in zip(ys, rs))
    if width + height > Fraction(2):
        return -float("inf")
    for c1, c2 in itertools.combinations(circles, 2):
        dist = np.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
        if dist < c1[2] + c2[2]:
            return -float("inf")
    return float(np.sum(radii))