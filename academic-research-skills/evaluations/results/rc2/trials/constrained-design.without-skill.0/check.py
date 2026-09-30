"""Exact fixture checks and the proposed 24-label confidence procedure.

The count examples are hypothetical inputs, not collected observations.
Run with the common Python runtime; only the standard library is used.
"""
from fractions import Fraction as F
from math import comb, sqrt


def theta(s, q):
    return (s - q) / (1 - 2 * q)


def target(t):
    return F(1, 2) + F(1, 10) / (1 - 2 * t) + F(9, 100) / (1 + 2 * t)


def observed_joint(q, h):
    # Explicit independent T, E, D construction, then marginalize T.
    p = {(x, y): F(0) for x in (0, 1) for y in (0, 1)}
    for t in (0, 1):
        for e in (0, 1):
            for d in (0, 1):
                p[t ^ e, t ^ d] += F(1, 2) * (q if e else 1 - q) * (1 - h if d else h)
    return p


def cp(k, n, coverage=0.975):
    """Equal-tailed Clopper-Pearson interval by binomial-tail inversion."""
    assert isinstance(k, int) and isinstance(n, int) and 0 <= k <= n and n > 0
    assert 0 < coverage < 1
    tail = (1 - coverage) / 2
    ends = []
    for lower in (True, False):
        if lower and k == 0:
            ends.append(0.0)
            continue
        if not lower and k == n:
            ends.append(1.0)
            continue
        lo, hi = 0.0, 1.0
        for _ in range(60):
            p = (lo + hi) / 2
            indices = range(k, n + 1) if lower else range(k + 1)
            prob = sum(comb(n, j) * p**j * (1 - p)**(n - j) for j in indices)
            if (prob < tail) if lower else (prob > tail):
                lo = p
            else:
                hi = p
        ends.append((lo + hi) / 2)
    return tuple(ends)


def truth_confidence_set(u, v, n=24):
    """At least 95% coverage by intersecting two 97.5% marginal intervals."""
    qlo, qhi = cp(u, n)
    hlo, hhi = cp(v, n)
    hlo, hhi = max(hlo, 0.75), min(hhi, 11 / 12)
    if hlo > hhi:
        return None
    inverse = lambda h: (h - 0.75) / (2 * h - 1)
    lo, hi = max(0.0, qlo, inverse(hlo)), min(0.2, qhi, inverse(hhi))
    return None if lo > hi else (lo, hi)


def check():
    expected = [
        {(0, 0): F(3, 8), (1, 1): F(3, 8), (0, 1): F(1, 8), (1, 0): F(1, 8)},
        {(0, 0): F(3, 10), (1, 1): F(3, 10), (0, 1): F(1, 5), (1, 0): F(1, 5)},
    ]
    for i in range(101):
        t = F(i, 500)
        q = (t, F(1, 6) - F(2, 3) * t)
        h = (theta(F(3, 4), q[0]), theta(F(3, 5), q[1]))
        assert all(0 <= x <= F(1, 5) for x in q)
        assert all(F(1, 2) <= x <= 1 for x in h)
        assert F(2, 5) * q[0] + F(3, 5) * q[1] == F(1, 10)
        assert F(2, 5) * h[0] + F(3, 5) * h[1] == target(t)
        for j in (0, 1):
            assert observed_joint(q[j], h[j]) == expected[j]
        derivative = F(1, 5) / (1 - 2 * t)**2 - F(9, 50) / (1 + 2 * t)**2
        assert derivative == (1 + 76 * t + 4 * t**2) / (50 * (1 - 2 * t)**2 * (1 + 2 * t)**2)
        assert derivative > 0
        # A same-rate, independent copy would identify q from its agreement.
        for rate in q:
            agreement = (1 - rate)**2 + rate**2
            assert abs((1 - sqrt(float(2 * agreement - 1))) / 2 - float(rate)) < 1e-12
    assert target(F(0)) == F(69, 100)
    assert target(F(1, 5)) == F(307, 420)
    assert theta(F(3, 4), F(1, 10)) == F(13, 16)
    assert theta(F(3, 5), F(1, 10)) == F(5, 8)
    assert target(F(1, 10)) == F(7, 10)
    assert abs(cp(0, 24)[1] - (1 - 0.0125**(1 / 24))) < 1e-12
    assert abs(cp(24, 24)[0] - 0.0125**(1 / 24)) < 1e-12
    cases = [(0, 20), (7, 20), (13, 20)]
    c0, c7, c13 = [truth_confidence_set(u, v) for u, v in cases]
    assert c0 is not None and c0[0] == 0 and 0.1 < c0[1] < 0.2
    assert c7 is not None and c7[0] > 0.1
    assert c13 is None
    print('PASS: exact constructions, complete observed distributions, bounds, B identification, copy inversion, confidence procedure.')
    print('A target bounds:', F(69, 100), F(307, 420), float(F(307, 420)))
    print('Hypothetical counts only; no truth observations were collected:')
    for u, v in cases:
        c = truth_confidence_set(u, v)
        print(f'U={u}, V={v}: q1 confidence set={c}; target interval={None if c is None else tuple(float(target(x)) for x in c)}')


if __name__ == '__main__':
    check()
