"""Causal first-alarm detectors. Calibration and clipping are known robust tools."""
import math
import statistics
from collections import deque


def _calibrate(x):
    if len(x) < 64:
        return None
    prefix = [v for v in x[:64] if v is not None]
    if not prefix:
        return None
    mu = statistics.median(prefix)
    scale = max(.25, 1.4826 * statistics.median(abs(v - mu) for v in prefix))
    return mu, scale


def detect_initial(x, params):
    """CUSUM proposal followed by a fresh observed-sample confirmation batch."""
    calibration = _calibrate(x)
    if calibration is None:
        return -1
    mu, scale = calibration
    plus = minus = 0.
    direction = 0
    age = count = 0
    evidence = 0.
    for t, v in enumerate(x[64:], 64):
        if direction:
            age += 1
        z = None if v is None else max(-params['clip'], min(params['clip'], (v - mu) / scale))
        if direction:
            if z is not None:
                count += 1
                evidence += direction * z
            if count >= params['confirm']:
                if evidence / count >= params['mean']:
                    return t
                direction = 0
                plus = minus = 0.
            elif age >= params['timeout']:
                direction = 0
                plus = minus = 0.
        elif z is not None:
            plus = max(0., plus + z - params['k'])
            minus = max(0., minus - z - params['k'])
            if max(plus, minus) > params['h']:
                direction = 1 if plus >= minus else -1
                age = count = 0
                evidence = 0.
    return -1


def detect_refined(x, params):
    """Require signed evidence after worst contiguous burst excision.

    Missing values advance the wall-clock window but contribute neither evidence
    nor observations. An alarm needs enough retained observations for *every*
    possible excised interval. This is a robust finite-window test, not a CUSUM.
    """
    calibration = _calibrate(x)
    if calibration is None:
        return -1
    mu, scale = calibration
    width = params['window']
    burst = params['burst']
    if not (isinstance(width, int) and isinstance(burst, int) and 0 <= burst < width):
        raise ValueError('require integer 0 <= burst < window')
    window = deque(maxlen=width)
    for t, v in enumerate(x[64:], 64):
        z = None if v is None else max(-params['clip'], min(params['clip'], (v - mu) / scale))
        window.append(z)
        if z is None or len(window) < width:
            continue
        sums = [0.]
        counts = [0]
        for value in window:
            sums.append(sums[-1] + (0. if value is None else value))
            counts.append(counts[-1] + (value is not None))
        n = counts[-1]
        if n < math.ceil(params['coverage'] * width):
            continue
        # ponytail: O(window) per time step; incremental interval extrema if long windows matter.
        for direction in (1, -1):
            worst = math.inf
            for start in range(width - burst + 1):
                removed_n = counts[start + burst] - counts[start]
                retained_n = n - removed_n
                if retained_n < math.ceil(params['coverage'] * (width - burst)):
                    worst = -math.inf
                    break
                removed_sum = sums[start + burst] - sums[start]
                statistic = direction * (sums[-1] - removed_sum) / math.sqrt(retained_n)
                worst = min(worst, statistic)
            if worst > params['threshold']:
                return t
    return -1
