"""Exact arithmetic for the judgement's invented two-world example, not a study."""
from fractions import Fraction


def check():
    for world, expected in (("A", (1, 0, 1)), ("B", (0, 1, -1))):
        baseline = corrected = identity = Fraction(0)
        for correction in (-1, 1):
            raw = correction
            target = 0 if world == "A" else correction
            baseline += Fraction((raw - target) ** 2, 2)
            corrected += Fraction((raw - correction - target) ** 2, 2)
            identity += Fraction(2 * correction * (raw - target) - correction ** 2, 2)
        assert (baseline, corrected, baseline - corrected) == expected
        assert identity == baseline - corrected
    print("PASS: exact two-world risks and gain decomposition")


if __name__ == "__main__":
    check()
