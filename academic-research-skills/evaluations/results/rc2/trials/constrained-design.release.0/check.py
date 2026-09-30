"""Exact checks for the synthetic fixture; no research data or sampled truths."""
from fractions import Fraction as F
from itertools import product
from math import comb, sqrt
import json

W = (F(2, 5), F(3, 5))
A = (F(3, 4), F(3, 5))


def theta(a, q):
    return (a - q) / (1 - 2 * q)


def world(q1):
    qs = (q1, F(1, 6) - F(2, 3) * q1)
    ts = tuple(theta(a, q) for a, q in zip(A, qs))
    return qs, ts, sum(w * t for w, t in zip(W, ts))


def observed(q, t, duplicate=False):
    out = {}
    for truth, e, d in product((0, 1), repeat=3):
        p = F(1, 2) * (q if e else 1 - q) * (1 - t if d else t)
        x, y = truth ^ e, truth ^ d
        key = (x, y, x) if duplicate else (x, y)
        out[key] = out.get(key, F(0)) + p
    return out


def target(q1):
    return F(1, 2) + F(1, 10) / (1 - 2 * q1) + F(9, 100) / (1 + 2 * q1)


def cp_interval(k, n, alpha=0.025):
    """Two-sided exact binomial interval, 1-alpha coverage."""
    if not 0 <= k <= n or n <= 0 or not 0 < alpha < 1:
        raise ValueError("Invalid binomial count or confidence level")

    def mass(p, j):
        return comb(n, j) * p ** j * (1 - p) ** (n - j)

    lower, upper = 0.0, 1.0
    if k:
        lo, hi = 0.0, 1.0
        for _ in range(80):
            p = (lo + hi) / 2
            if sum(mass(p, j) for j in range(k, n + 1)) < alpha / 2:
                lo = p
            else:
                hi = p
        lower = (lo + hi) / 2
    if k < n:
        lo, hi = 0.0, 1.0
        for _ in range(80):
            p = (lo + hi) / 2
            if sum(mass(p, j) for j in range(k + 1)) > alpha / 2:
                lo = p
            else:
                hi = p
        upper = (lo + hi) / 2
    return lower, upper


def validation_interval(e1, e2, n1=10, n2=14):
    """Bonferroni 95% set using purchased truths' X errors and known constraints."""
    l1, u1 = cp_interval(e1, n1)
    l2, u2 = cp_interval(e2, n2)
    lo = max(0.0, l1, 0.25 - 1.5 * u2)
    hi = min(0.2, u1, 0.25 - 1.5 * l2)
    if lo > hi:
        return None
    f = lambda x: 0.5 + 0.1 / (1 - 2 * x) + 0.09 / (1 + 2 * x)
    return (lo, hi), (f(lo), f(hi))


def main():
    lower, upper = world(F(0)), world(F(1, 5))
    assert lower[1] == (F(3, 4), F(13, 20))
    assert upper[1] == (F(11, 12), F(17, 28))
    assert lower[2] == F(69, 100) and upper[2] == F(307, 420)
    assert upper[2] - lower[2] == F(43, 1050)
    for i in range(101):
        x = F(i, 500)
        qs, ts, total = world(x)
        assert sum(w * q for w, q in zip(W, qs)) == F(1, 10)
        assert total == target(x)
        assert all(0 <= q <= F(1, 5) for q in qs)
        assert all(F(1, 2) <= t <= 1 for t in ts)
        for a, q, t in zip(A, qs, ts):
            expected = {(0, 0): a / 2, (1, 1): a / 2,
                        (0, 1): (1 - a) / 2, (1, 0): (1 - a) / 2}
            assert observed(q, t) == expected
            expected_copy = {(x, y, x): p for (x, y), p in expected.items()}
            assert observed(q, t, duplicate=True) == expected_copy
            c_copy = (1 - 2 * q) ** 2
            recovered_q = (1 - sqrt(float(c_copy))) / 2
            assert abs(recovered_q - float(q)) < 1e-12
    b = world(F(1, 10))
    assert b[0] == (F(1, 10), F(1, 10))
    assert b[1] == (F(13, 16), F(5, 8)) and b[2] == F(7, 10)
    for n in (10, 14):
        assert abs(cp_interval(0, n)[1] - (1 - 0.0125 ** (1 / n))) < 1e-12
        assert abs(cp_interval(n, n)[0] - 0.0125 ** (1 / n)) < 1e-12
    hypothetical_zero_errors = validation_interval(0, 0)
    assert hypothetical_zero_errors[0] == (0.0, 0.2)
    assert abs(hypothetical_zero_errors[1][0] - float(lower[2])) < 1e-12
    assert abs(hypothetical_zero_errors[1][1] - float(upper[2])) < 1e-12
    report = {
        "status": "PASS",
        "scope": "Synthetic exact-distribution checks, not acquired data",
        "A_lower": {"q": list(map(str, lower[0])), "theta": list(map(str, lower[1])), "target": str(lower[2])},
        "A_upper": {"q": list(map(str, upper[0])), "theta": list(map(str, upper[1])), "target": str(upper[2])},
        "A_width": str(upper[2] - lower[2]),
        "B_target": str(b[2]),
        "direct_24_stratified_SE_conservative_ceiling": sqrt(0.4 ** 2 / (4 * 10) + 0.6 ** 2 / (4 * 14)),
        "hypothetical_zero_X_errors_not_observed": hypothetical_zero_errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
