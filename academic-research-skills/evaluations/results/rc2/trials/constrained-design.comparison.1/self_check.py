"""Run with Python 3; checks synthetic identities, never collects data."""

from fractions import Fraction as Q
from itertools import product
from math import isclose, sqrt


def observed_joint(q, theta):
    out = dict.fromkeys(product((0, 1), repeat=2), Q(0))
    for t, e, d in product((0, 1), repeat=3):
        pe = q if e else 1 - q
        pd = 1 - theta if d else theta
        out[t ^ e, t ^ d] += Q(1, 2) * pe * pd
    return out


def parameters(t):
    q2 = Q(1, 6) - Q(2, 3) * t
    theta1 = (Q(3, 4) - t) / (1 - 2 * t)
    theta2 = (Q(3, 5) - q2) / (1 - 2 * q2)
    return t, q2, theta1, theta2


def target(theta1, theta2):
    return Q(2, 5) * theta1 + Q(3, 5) * theta2


def check():
    endpoints = (Q(0), Q(1, 5))
    expected_targets = (Q(69, 100), Q(307, 420))
    for t, expected in zip(endpoints, expected_targets):
        q1, q2, theta1, theta2 = parameters(t)
        assert target(theta1, theta2) == expected
        assert Q(2, 5) * q1 + Q(3, 5) * q2 == Q(1, 10)
        for q, theta, a in ((q1, theta1, Q(3, 4)), (q2, theta2, Q(3, 5))):
            assert 0 <= q <= Q(1, 5)
            assert Q(1, 2) <= theta <= 1
            table = observed_joint(q, theta)
            assert sum(table.values()) == 1
            assert table == {(0, 0): a / 2, (1, 1): a / 2,
                             (0, 1): (1 - a) / 2, (1, 0): (1 - a) / 2}

    # This grid checks arithmetic; the continuous bound is proved in answer.md.
    previous = None
    for i in range(101):
        q1, q2, theta1, theta2 = parameters(Q(i, 500))
        derivative = Q(1, 5) / (1 - 2 * q1) ** 2 - Q(2, 25) / (1 - 2 * q2) ** 2
        assert derivative >= Q(1, 50)
        value = target(theta1, theta2)
        assert previous is None or value > previous
        previous = value

    _, _, theta1, theta2 = parameters(Q(1, 10))
    assert (theta1, theta2, target(theta1, theta2)) == (Q(13, 16), Q(5, 8), Q(7, 10))
    assert (Q(33, 50) - Q(1, 10)) / Q(4, 5) == Q(7, 10)

    for q in (Q(0), Q(1, 10), Q(1, 5)):
        b = (1 - q) ** 2 + q ** 2
        assert Q(17, 25) <= b <= 1
        assert isclose((1 - sqrt(float(2 * b - 1))) / 2, float(q), abs_tol=1e-14)

    # Possible, unobserved gold-data outcome: no X errors in either group.
    for t in endpoints:
        q1, q2, _, _ = parameters(t)
        assert (1 - q1) ** 12 * (1 - q2) ** 12 > 0
    assert 1 - (1 / 80) ** (1 / 12) > 1 / 5
    print("PASS: exact observation tables, feasible endpoints, target bounds, B point value, and design identities")


if __name__ == "__main__":
    check()
