"""Causal sustained-shift detectors; calibration is the supplied 64-step prefix."""
import math
import statistics


def _calibrate(x):
    if len(x) < 64:
        return None
    vals = [v for v in x[:64] if v is not None]
    if not vals:
        return None
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in vals):
        raise ValueError('calibration observations must be finite numbers or None')
    center = statistics.median(vals)
    scale = max(.25, 1.4826 * statistics.median(abs(v - center) for v in vals))
    return center, scale


def _z(v, center, scale, clip):
    if not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError('observations must be finite numbers or None')
    return max(-clip, min(clip, (v - center) / scale))


def detect_initial(x, params):
    """CUSUM candidate followed by independent future evidence after a guard interval.

    Pending directions have a fixed wall-clock confirmation horizon. A failed
    confirmation resets that direction. Missing observations never supply evidence.
    """
    calibrated = _calibrate(x)
    if calibrated is None:
        return -1
    center, scale = calibrated
    scores = [0., 0.]
    pending = [None, None]
    for t, v in enumerate(x[64:], 64):
        z = None if v is None else _z(v, center, scale, params['clip'])
        for j, direction in enumerate((1, -1)):
            if pending[j] is None:
                if z is not None:
                    scores[j] = max(0., scores[j] + direction * z - params['k'])
                    if scores[j] > params['h']:
                        pending[j] = [t, 0., 0]
            else:
                elapsed = t - pending[j][0]
                if elapsed > params['guard'] and z is not None:
                    pending[j][1] += direction * z
                    pending[j][2] += 1
                if elapsed >= params['guard'] + params['confirm']:
                    _, total, n = pending[j]
                    if n >= params['min_count'] and total / n > params['mean']:
                        return t
                    pending[j] = None
                    scores[j] = 0.
    return -1


def detect_refined(x, params):
    """Trailing evidence after erasing its strongest contiguous nuisance block.

    Every wall-clock window must retain enough observed samples after erasure.
    erase=0 is the matched finite-moving-sum ablation. The erasure is exact for
    the specified block class, but does not protect against multiple bursts.
    """
    calibrated = _calibrate(x)
    if calibrated is None:
        return -1
    center, scale = calibrated
    # ponytail: O(window) work per step; maintain rolling sums if long windows matter.
    history = []
    for t, v in enumerate(x[64:], 64):
        z = None if v is None else _z(v, center, scale, params['clip'])
        history.append(z)
        if len(history) > params['window']:
            history.pop(0)
        if z is None:
            continue
        n = sum(v is not None for v in history)
        for direction in (1, -1):
            evidence = [0. if v is None else direction*v - params['k'] for v in history]
            width = min(params['erase'], len(evidence))
            removed, removed_count = 0., 0
            if width:
                block = sum(evidence[:width])
                count = sum(v is not None for v in history[:width])
                if block > removed:
                    removed, removed_count = block, count
                for j in range(width, len(evidence)):
                    block += evidence[j] - evidence[j-width]
                    count += int(history[j] is not None) - int(history[j-width] is not None)
                    if block > removed:
                        removed, removed_count = block, count
            if n - removed_count >= params['min_count'] and sum(evidence) - removed > params['h']:
                return t
    return -1
