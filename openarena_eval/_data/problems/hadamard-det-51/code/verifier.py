import math

import sympy as sp

N = 51


def _log10_exact(d):
    # Full double precision from the exact integer, avoiding overflow.
    e = len(str(d)) - 1
    return e + math.log10(d / 10 ** e)


def evaluate(data):
    rows = data["matrix"]
    if len(rows) != N:
        raise ValueError("Expected " + str(N) + " rows, got " + str(len(rows)))
    m = []
    for i, row in enumerate(rows):
        if len(row) != N:
            raise ValueError("Row " + str(i) + " has length " + str(len(row)) + ", expected " + str(N))
        out = []
        for v in row:
            if isinstance(v, bool) or not isinstance(v, int):
                raise ValueError("Row " + str(i) + " contains a non-integer entry: " + repr(v))
            if v != 1 and v != -1:
                raise ValueError("Row " + str(i) + " contains " + repr(v) + "; entries must be 1 or -1")
            out.append(v)
        m.append(out)

    # Same call the record authors use to verify their own matrices.
    d = abs(int(sp.Matrix(m).det_bareis()))
    if d == 0:
        return 0.0
    return float(_log10_exact(d))