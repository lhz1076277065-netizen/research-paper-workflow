"""Causal first alarms: post-trigger confirmation and burst-deleted scan.

The 64-slot stable prefix and robust standardization are task-known machinery.
Neither this clipping nor CUSUM is claimed as a new method.
"""
import math
import statistics
from collections import deque


def _calibrate(x):
    if len(x) < 64:
        return None
    prefix = [float(v) for v in x[:64] if v is not None and math.isfinite(v)]
    if len(prefix) < 8:
        return None
    mu = statistics.median(prefix)
    scale = max(.25, 1.4826 * statistics.median(abs(v - mu) for v in prefix))
    return mu, scale


def detect_initial(x, params):
    """Known CUSUM candidate, followed by a disjoint fixed-size fresh block.

    Reject a candidate if fresh directional clipped mean does not exceed confirm.
    Missing samples do not count toward the block; candidates expire in wall time.
    """
    cal = _calibrate(x)
    if cal is None:
        return -1
    mu, scale = cal
    plus = minus = 0.
    direction = count = age = 0
    total = 0.
    for t in range(64, len(x)):
        v = x[t]
        if direction:
            age += 1
            if age > params['expiry']:
                direction = count = age = 0
                plus = minus = total = 0.
        if v is None or not math.isfinite(v):
            continue
        z = max(-params['clip'], min(params['clip'], (v - mu) / scale))
        if direction:
            total += direction * z
            count += 1
            if count == params['confirm_n']:
                if total / count > params['confirm']:
                    return t
                direction = count = age = 0
                plus = minus = total = 0.
        else:
            plus = max(0., plus + z - params['k'])
            minus = max(0., minus - z - params['k'])
            if max(plus, minus) > params['h']:
                direction = 1 if plus >= minus else -1
                count = age = 0
                total = 0.
    return -1


def _max_interval(values, budget):
    """Largest nonnegative evidence sum in one interval of at most budget slots."""
    if budget == 0:
        return 0.
    # ponytail: O(window) scan; rolling max queues if long windows matter.
    prefix = [0.]
    for v in values:
        prefix.append(prefix[-1] + v)
    minima = deque([0])
    best = 0.
    for j in range(1, len(prefix)):
        while minima and minima[0] < j - budget:
            minima.popleft()
        best = max(best, prefix[j] - prefix[minima[0]])
        while minima and prefix[minima[-1]] >= prefix[j]:
            minima.pop()
        minima.append(j)
    return best


def detect_refined(x, params):
    """Trailing directional evidence after deleting its strongest short interval.

    At each time t and direction s, form e_i=s*clip(z_i)-k (zero for missing).
    Score = sum(e_i) - max(0, sum(e_i) over any contiguous interval <= budget).
    Alarm if either score exceeds h with sufficient observed coverage.
    budget=0 is the matched moving-sum ablation.
    """
    cal = _calibrate(x)
    if cal is None:
        return -1
    mu, scale = cal
    window = deque(maxlen=params['window'])
    for t in range(64, len(x)):
        v = x[t]
        valid = v is not None and math.isfinite(v)
        z = max(-params['clip'], min(params['clip'], (v - mu) / scale)) if valid else None
        window.append(z)
        if not valid or len(window) < params['window']:
            continue
        if sum(v is not None for v in window) < math.ceil(params['coverage'] * params['window']):
            continue
        for direction in (1, -1):
            evidence = [direction * v - params['k'] if v is not None else 0. for v in window]
            score = sum(evidence) - _max_interval(evidence, params['budget'])
            if score > params['h']:
                return t
    return -1
