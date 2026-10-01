"""Runnable causal, burst-removal, and known-case checks; no validation scoring."""
import json
import random
import statistics
import sys
from pathlib import Path

from methods import detect_initial, detect_refined, _max_interval
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import harness


def main():
    frozen = json.loads((HERE / 'frozen.json').read_text())
    rng = random.Random(728)
    max_interval_checks = 0
    for n in range(1, 25):
        values = [rng.uniform(-3, 3) for _ in range(n)]
        for budget in range(n + 1):
            brute = max([0.] + [sum(values[a:b]) for a in range(n) for b in range(a + 1, min(n, a + budget) + 1)])
            assert abs(_max_interval(values, budget) - brute) < 1e-10
            max_interval_checks += 1
    prefix = [-1., 1.] * 32
    scale = 1.4826
    stable = prefix + [0.] * 240
    cases = {'stable': stable, 'burst_8': prefix + [0.] * 56 + [3. * scale] * 8 + [0.] * 176,
             'burst_16_limit': prefix + [0.] * 56 + [3. * scale] * 16 + [0.] * 168,
             'weak_sustained': prefix + [0.] * 56 + [.8 * scale] * 184,
             'positive_sustained': prefix + [0.] * 56 + [1.2 * scale] * 184,
             'negative_sustained': prefix + [0.] * 56 + [-1.2 * scale] * 184,
             'shift_with_gap': prefix + [0.] * 56 + [1.2 * scale] * 5 + [None] * 18 + [1.2 * scale] * 161,
             'short': prefix[:40], 'no_calibration': [None] * 304}
    known = {}
    for name, x in cases.items():
        known[name] = {m: fn(x, frozen[m]) for m, fn in [('initial', detect_initial), ('refined', detect_refined)]}
        if name not in ['short', 'no_calibration']:
            known[name]['baseline'] = harness.baseline(x, frozen['baseline'])
    assert known['stable']['initial'] == known['stable']['refined'] == -1
    assert known['burst_8']['refined'] == -1
    assert known['weak_sustained']['initial'] == -1
    assert 120 <= known['weak_sustained']['refined'] <= 180
    for name in ['positive_sustained', 'negative_sustained', 'shift_with_gap']:
        assert 120 <= known[name]['refined'] <= 180
    assert known['burst_16_limit']['refined'] >= 120
    assert known['short']['initial'] == known['short']['refined'] == -1
    assert known['no_calibration']['initial'] == known['no_calibration']['refined'] == -1
    causal_checks = 0
    # Exhaust every prefix of synthetic mechanisms, including no-alarm cases.
    for x in cases.values():
        for m, fn in [('initial', detect_initial), ('refined', detect_refined)]:
            alarm = fn(x, frozen[m])
            for cut in range(len(x) + 1):
                expected = alarm if 0 <= alarm < cut else -1
                assert fn(x[:cut], frozen[m]) == expected
                causal_checks += 1
    # All supplied training cases, especially alarm boundary; suffix perturbations.
    train = json.loads((HERE.parent / 'data/train.json').read_text())
    for case in train:
        x = case['x']
        for m, fn in [('initial', detect_initial), ('refined', detect_refined)]:
            alarm = fn(x, frozen[m])
            cuts = {0, 63, 64, 65, 100, 180, 270, len(x)}
            if alarm >= 0:
                cuts.update([alarm, alarm + 1])
            for cut in cuts:
                expected = alarm if 0 <= alarm < cut else -1
                assert fn(x[:cut], frozen[m]) == expected
                changed = x[:cut] + [rng.choice([None, -1e6, 1e6])] * (len(x) - cut)
                changed_alarm = fn(changed, frozen[m])
                assert (changed_alarm if 0 <= changed_alarm < cut else -1) == expected
                causal_checks += 2
    result = {'status': 'passed', 'bounded_interval_bruteforce_checks': max_interval_checks,
              'causal_prefix_and_suffix_checks': causal_checks, 'known_cases': known,
              'scope': 'Synthetic exhaustive prefixes and all 40 train cases at selected cuts; no holdout or dev scoring.'}
    (HERE / 'checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
