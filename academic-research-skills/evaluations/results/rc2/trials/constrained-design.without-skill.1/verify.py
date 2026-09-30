"""Synthetic model self-check. Run with Python 3; no external dependencies."""
from fractions import Fraction as Q
from itertools import product
from math import isqrt
import json


WEIGHTS = (Q(2, 5), Q(3, 5))
AGREEMENTS = (Q(3, 4), Q(3, 5))


def law(q, theta, replica=None):
    out = {}
    for t, e, d in product((0, 1), repeat=3):
        p = Q(1, 2) * (q if e else 1-q) * (1-theta if d else theta)
        copies = ((e, Q(1)),) if replica == "identical" else (
            ((0, 1-q), (1, q)) if replica == "independent" else ((None, Q(1)),)
        )
        for ep, pp in copies:
            key = (t ^ e, t ^ d) if ep is None else (t ^ e, t ^ d, t ^ ep)
            out[key] = out.get(key, Q(0)) + p * pp
    assert sum(out.values()) == 1
    return out


def parameters(x):
    qs = (x, Q(1, 6)-Q(2, 3)*x)
    thetas = tuple((a-q)/(1-2*q) for a, q in zip(AGREEMENTS, qs))
    return qs, thetas


def target(thetas):
    return sum(w*t for w, t in zip(WEIGHTS, thetas))


expected = tuple({(0, 0): a/2, (1, 1): a/2,
                  (0, 1): (1-a)/2, (1, 0): (1-a)/2}
                 for a in AGREEMENTS)
witnesses = []
for x, bound in ((Q(0), Q(69, 100)), (Q(1, 5), Q(307, 420))):
    qs, thetas = parameters(x)
    assert sum(w*q for w, q in zip(WEIGHTS, qs)) == Q(1, 10)
    assert target(thetas) == bound
    cloned = []
    for q, theta, observed in zip(qs, thetas, expected):
        assert Q(0) <= q <= Q(1, 5) and Q(1, 2) <= theta <= 1
        assert law(q, theta) == observed
        clone = law(q, theta, "identical")
        assert clone == {(x, y, x): p for (x, y), p in observed.items()}
        cloned.append(clone)
        independent = law(q, theta, "independent")
        b = sum(p for (x, y, xp), p in independent.items() if x == xp)
        square = 2*b-1
        root = Q(isqrt(square.numerator), isqrt(square.denominator))
        assert root*root == square and (1-root)/2 == q
    witnesses.append((bound, cloned))
assert witnesses[0][1] == witnesses[1][1]
assert witnesses[0][0] != witnesses[1][0]

# This finite grid checks arithmetic; the continuous proof is in answer.md.
previous = None
for i in range(201):
    x = Q(i, 1000)
    qs, thetas = parameters(x)
    value = target(thetas)
    r1, r2 = 1-2*x, Q(2, 3)+Q(4, 3)*x
    derivative = Q(1, 5)/r1**2-Q(2, 25)/r2**2
    assert r2 >= Q(2, 3)*r1 > 0 and derivative >= Q(1, 50)/r1**2
    assert Q(69, 100) <= value <= Q(307, 420)
    assert previous is None or previous < value
    assert all(law(q, t) == p for q, t, p in zip(qs, thetas, expected))
    previous = value

qs, thetas = parameters(Q(1, 10))
assert qs == (Q(1, 10), Q(1, 10))
assert thetas == (Q(13, 16), Q(5, 8)) and target(thetas) == Q(7, 10)
print(json.dumps({"status": "passed", "synthetic_only": True,
                  "A_bounds": ["69/100", "307/420"], "B_target": "7/10",
                  "same_full_observable_law": True,
                  "identical_replica_not_identifying": True,
                  "independent_equal_error_replica_formula": True,
                  "arithmetic_grid_points": 201}, ensure_ascii=False, indent=2))
