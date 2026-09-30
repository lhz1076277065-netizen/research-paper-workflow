"""Self-contained checks for the supplied synthetic model; no real data."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import product
from math import comb


W = (F(2, 5), F(3, 5))
P = (F(3, 4), F(3, 5))


def theta(p, q):
    return (p - q) / (1 - 2 * q)


def target(x):
    qs = (x, F(1, 6) - F(2, 3) * x)
    return sum(w * theta(p, q) for w, p, q in zip(W, P, qs))


def joint(q, accuracy, copy=False):
    out = defaultdict(F)
    for t, e, d in product((0, 1), repeat=3):
        prob = F(1, 2) * (q if e else 1 - q)
        prob *= (1 - accuracy if d else accuracy)
        x, y = t ^ e, t ^ d
        # The permitted perfectly correlated copy has E' = E.
        out[(x, x, y) if copy else (x, y)] += prob
    return dict(out)


def check_world(qs):
    assert sum(w * q for w, q in zip(W, qs)) == F(1, 10)
    result = []
    for p, q in zip(P, qs):
        accuracy = theta(p, q)
        assert 0 <= q <= F(1, 5) and F(1, 2) <= accuracy <= 1
        expected = {(0, 0): p / 2, (1, 1): p / 2,
                    (0, 1): (1 - p) / 2, (1, 0): (1 - p) / 2}
        assert joint(q, accuracy) == expected
        result.append(accuracy)
    return tuple(result)


def main():
    low_q, high_q = (F(0), F(1, 6)), (F(1, 5), F(1, 30))
    low_t, high_t = check_world(low_q), check_world(high_q)
    assert low_t == (F(3, 4), F(13, 20))
    assert high_t == (F(11, 12), F(17, 28))
    assert target(F(0)) == F(69, 100)
    assert target(F(1, 5)) == F(307, 420)
    assert target(F(1, 5)) - target(F(0)) == F(43, 1050)
    for i in range(201):
        x = F(i, 1000)
        check_world((x, F(1, 6) - F(2, 3) * x))
        derivative = F(1, 5) / (1 - 2 * x) ** 2
        derivative -= F(9, 50) / (1 + 2 * x) ** 2
        assert derivative > 0
        assert target(x) == F(1, 2) + F(1, 10) / (1 - 2 * x) + F(9, 100) / (1 + 2 * x)
    b_t = check_world((F(1, 10), F(1, 10)))
    assert b_t == (F(13, 16), F(5, 8)) and target(F(1, 10)) == F(7, 10)
    for g in (0, 1):
        assert joint(low_q[g], low_t[g], True) == joint(high_q[g], high_t[g], True)
    n, q0 = 24, F(1, 10)
    tail = lambda k: sum(F(comb(n, j)) * q0 ** j * (1 - q0) ** (n - j) for j in range(k, n + 1))
    assert tail(6) < F(1, 20) < tail(5)
    assert (1 - q0) ** n > F(1, 20)
    upper_q_zero = 1 - 0.05 ** (1 / n)
    upper_target_zero = 0.5 + 0.1 / (1 - 2 * upper_q_zero) + 0.09 / (1 + 2 * upper_q_zero)
    print("PASS: exact joint distributions, all constraints, sharp endpoints, B and correlated-copy counterexample")
    print(f"A target: [{F(69, 100)}, {F(307, 420)}] = [{0.69:.9f}, {307 / 420:.9f}]")
    print(f"24 group-1 truths: P_q=.1(K>=6)={float(tail(6)):.9f}; P(K>=5)={float(tail(5)):.9f}")
    print(f"P_q=.1(K=0)={float((1-q0)**n):.9f}; P_q=.2(K=0)={0.8**n:.9f}")
    print(f"K=0 one-sided 95% upper q={upper_q_zero:.9f}, upper target={upper_target_zero:.9f}")


if __name__ == "__main__":
    main()
