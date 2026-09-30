"""Independent stdlib checks; synthetic calculations, no empirical results."""
from fractions import Fraction as Q
from math import comb, isclose, sqrt
import json

P = (Q(3, 4), Q(3, 5))
W = (Q(2, 5), Q(3, 5))


def parameters(t):
    q = (t, Q(1, 6) - Q(2, 3) * t)
    theta = tuple((p - e) / (1 - 2 * e) for p, e in zip(P, q))
    return q, theta, sum(w * v for w, v in zip(W, theta))


def joint(q, theta):
    cells = {(x, y): Q(0) for x in (0, 1) for y in (0, 1)}
    for t in (0, 1):
        for e in (0, 1):
            for d in (0, 1):
                prob = Q(1, 2) * (q if e else 1 - q)
                prob *= (1 - theta) if d else theta
                cells[t ^ e, t ^ d] += prob
    return cells


def pmf(n, k, p):
    return comb(n, k) * p ** k * (1 - p) ** (n - k)


def upper_tail(n, k, p):
    return sum(pmf(n, j, p) for j in range(k, n + 1))


def cp(n, k, coverage):
    tail_alpha = (1 - coverage) / 2

    def solve(fn, increasing):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if (fn(mid) < tail_alpha) == increasing:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else solve(lambda p: upper_tail(n, k, p), True)
    upper = 1.0 if k == n else solve(lambda p: sum(pmf(n, j, p) for j in range(k + 1)), False)
    return lower, upper


def target(t):
    return .5 + .1 / (1 - 2 * t) + .09 / (1 + 2 * t)


def group1_interval(k, s):
    lo, hi = cp(24, k, .975)
    lo, hi = max(0.0, lo), min(.2, hi)
    a, b = cp(24, s, .975)
    a, b = max(.75, a), min(11 / 12, b)
    if a > b:
        return None
    inverse = lambda theta: (theta - .75) / (2 * theta - 1)
    lo, hi = max(lo, inverse(a)), min(hi, inverse(b))
    return None if lo > hi else [target(lo), target(hi)]


def main():
    targets = (Q(69, 100), Q(7, 10), Q(307, 420))
    for t, expected in zip((Q(0), Q(1, 10), Q(1, 5)), targets):
        q, theta, value = parameters(t)
        assert value == expected and sum(w * e for w, e in zip(W, q)) == Q(1, 10)
        for g in range(2):
            assert 0 <= q[g] <= Q(1, 5) and Q(1, 2) <= theta[g] <= 1
            assert joint(q[g], theta[g]) == {(0, 0): P[g] / 2, (0, 1): (1 - P[g]) / 2,
                                            (1, 0): (1 - P[g]) / 2, (1, 1): P[g] / 2}
            h = (1 - q[g]) ** 2 + q[g] ** 2
            assert isclose((1 - sqrt(float(2 * h - 1))) / 2, float(q[g]), abs_tol=1e-14)
            for r in (Q(3, 10), Q(7, 10)):
                a, b, c = 1 - 2 * q[g], 2 * theta[g] - 1, 1 - 2 * r
                assert (a * b) * (a * c) / (b * c) == a ** 2
    # Equality check only: positivity on the whole interval is proved analytically in review.md.
    for t in (Q(0), Q(1, 10), Q(1, 5)):
        derivative = Q(1, 5) / (1 - 2 * t) ** 2 - Q(9, 50) / (1 + 2 * t) ** 2
        polynomial = (1 + 76 * t + 4 * t ** 2) / (50 * (1 - 2 * t) ** 2 * (1 + 2 * t) ** 2)
        assert derivative == polynomial and derivative >= Q(1, 50)
    examples = {str((k, s)): group1_interval(k, s) for k, s in ((0, 20), (7, 20), (13, 20))}
    assert isclose(examples['(0, 20)'][1], .7175764633944636, abs_tol=1e-12)
    assert isclose(examples['(7, 20)'][0], .7020107576381838, abs_tol=1e-12)
    assert examples['(13, 20)'] is None
    for n in (10, 12, 14):
        assert cp(n, 0, .975)[1] > .2
    size = upper_tail(24, 6, .1)
    assert isclose(size, .027658284470698, abs_tol=1e-14)
    assert isclose(.8 ** 24, .004722366482870, abs_tol=1e-14)
    q_upper = 1 - .05 ** (1 / 24)
    print(json.dumps({'checked': 'full cells, sharp endpoints, B, derivative identity, replication inversions, CP examples',
                      'group1_CP_examples': examples, 'K_ge_6_size_at_q1_0_1': size,
                      'K_ge_6_power_at_q1_0_2': upper_tail(24, 6, .2),
                      'K0_one_sided_q_upper': q_upper, 'K0_target_upper': target(q_upper),
                      'endpoint_group1_error_detection': {str(n): 1 - .8 ** n for n in (24, 12, 10)},
                      'direct_SE_generic_upper_10_14': sqrt(.25 * (.16 / 10 + .36 / 14))},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
