"""Exact checks for the supplied synthetic model; no sampled research data."""

from fractions import Fraction as F
from itertools import product

W = (F(2, 5), F(3, 5))
A = (F(3, 4), F(3, 5))


def theta(a, q):
    return (a - q) / (1 - 2 * q)


def target(t):
    return F(1, 2) + F(1, 10) / (1 - 2 * t) + F(9, 100) / (1 + 2 * t)


def law(q, accuracy, duplicate=False):
    """Enumerate independent (T,E,D), optionally using the allowed E'=E."""
    observed = {}
    for truth, error, distortion in product((0, 1), repeat=3):
        p = F(1, 2) * (q if error else 1 - q)
        p *= 1 - accuracy if distortion else accuracy
        x, y = truth ^ error, truth ^ distortion
        key = (x, y, x) if duplicate else (x, y)
        observed[key] = observed.get(key, F(0)) + p
    assert sum(observed.values()) == 1
    return observed


def check_world(qs, accuracies, expected_target):
    assert sum(w * q for w, q in zip(W, qs)) == F(1, 10)
    for q, accuracy, a in zip(qs, accuracies, A):
        assert 0 <= q <= F(1, 5)
        assert F(1, 2) <= accuracy <= 1
        assert accuracy == theta(a, q)
        expected = {(0, 0): a / 2, (1, 1): a / 2,
                    (0, 1): (1 - a) / 2, (1, 0): (1 - a) / 2}
        assert law(q, accuracy) == expected
    assert sum(w * accuracy for w, accuracy in zip(W, accuracies)) == expected_target


def main():
    lower = ((F(0), F(1, 6)), (F(3, 4), F(13, 20)))
    upper = ((F(1, 5), F(1, 30)), (F(11, 12), F(17, 28)))
    known = ((F(1, 10), F(1, 10)), (F(13, 16), F(5, 8)))
    check_world(*lower, F(69, 100))
    check_world(*upper, F(307, 420))
    check_world(*known, F(7, 10))
    assert target(F(0)) == F(69, 100)
    assert target(F(1, 5)) == F(307, 420)
    assert target(F(1, 10)) == F(7, 10)
    assert target(F(1, 5)) - target(F(0)) == F(43, 1050)

    # F' numerator is 1 + 76*t + 4*t*t: positive for every t >= 0.
    for t in (F(0), F(1, 10), F(1, 5)):
        q2 = F(1, 6) - F(2, 3) * t
        assert F(1, 30) <= q2 <= F(1, 6)
        direct = W[0] * theta(A[0], t) + W[1] * theta(A[1], q2)
        assert direct == target(t)
        derivative = F(1, 5) / (1 - 2 * t) ** 2 - F(9, 50) / (1 + 2 * t) ** 2
        assert derivative == (1 + 76 * t + 4 * t * t) / (
            50 * (1 - 2 * t) ** 2 * (1 + 2 * t) ** 2)
        assert derivative > 0

    for g in (0, 1):
        assert law(lower[0][g], lower[1][g], True) == law(upper[0][g], upper[1][g], True)
    for q in (F(0), F(1, 10), F(1, 5)):
        h = (1 - q) ** 2 + q ** 2
        assert 2 * h - 1 == (1 - 2 * q) ** 2
        assert 1 - 2 * q > 0

    print("PASS: exact endpoint worlds, all constraints, full observed laws, and B solution")
    print("PASS: target identity, derivative checks, dependent-copy counterexample, and independent-copy identity")
    print("A sharp interval: [69/100, 307/420]; width: 43/1050")
    print("B target: 7/10")


if __name__ == "__main__":
    main()
