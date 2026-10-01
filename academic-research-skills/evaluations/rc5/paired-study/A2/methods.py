"""Two causal burst-rejection extensions of the supplied clipped CUSUM.

Initial: minimum observed age of the positive CUSUM excursion.
Refined: quarantine a trigger; require fresh evidence in two disjoint blocks.
Neither clipping, CUSUM, nor two-stage confirmation is claimed as new science.
"""
import math
import statistics


def _calibrate(x):
    if len(x) < 64:
        return None
    values = [v for v in x[:64] if v is not None]
    if not values:
        return None
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError('observed samples must be finite numbers or None')
    mu = statistics.median(values)
    scale = max(.25, 1.4826 * statistics.median(abs(v - mu) for v in values))
    return mu, scale


def _observations(x, mu, scale, clip):
    for t, value in enumerate(x[64:], 64):
        if value is None:
            yield t, None
        else:
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError('observed samples must be finite numbers or None')
            yield t, max(-clip, min(clip, (value - mu) / scale))


def detect_initial(x, params):
    """Alarm after threshold and min_age observed points in one excursion."""
    calibration = _calibrate(x)
    if calibration is None:
        return -1
    plus = minus = 0.
    age_plus = age_minus = 0
    for t, z in _observations(x, *calibration, params['clip']):
        if z is None:
            continue
        plus = max(0., plus + z - params['k'])
        minus = max(0., minus - z - params['k'])
        age_plus = age_plus + 1 if plus > 0 else 0
        age_minus = age_minus + 1 if minus > 0 else 0
        if ((plus > params['h'] and age_plus >= params['min_age']) or
                (minus > params['h'] and age_minus >= params['min_age'])):
            return t
    return -1


def _refined(x, params, trace=None):
    calibration = _calibrate(x)
    if calibration is None:
        return -1
    plus = minus = 0.
    direction = 0
    evidence = []
    missing_run = 0
    for t, z in _observations(x, *calibration, params['clip']):
        if z is None:
            missing_run += 1
            # A gap cannot supply persistence evidence or indefinitely bridge it.
            if missing_run > params['max_gap']:
                if trace is not None and direction:
                    trace.append({'time': t, 'event': 'gap_reset', 'direction': direction})
                plus = minus = 0.
                direction = 0
                evidence = []
            continue
        missing_run = 0
        if direction:
            evidence.append(direction * z)
            if len(evidence) == 2 * params['block']:
                left = statistics.mean(evidence[:params['block']])
                right = statistics.mean(evidence[params['block']:])
                accepted = (min(left, right) >= params['confirm_mean']
                            if params.get('two_blocks', True)
                            else statistics.mean(evidence) >= params['confirm_mean'])
                if trace is not None:
                    trace.append({'time': t, 'event': 'confirm' if accepted else 'reject',
                                  'direction': direction, 'left_mean': left, 'right_mean': right})
                if accepted:
                    return t
                # Rejecting a candidate discards its trigger energy: it cannot
                # be recycled into a new alarm after the nuisance has ended.
                plus = minus = 0.
                direction = 0
                evidence = []
            continue
        plus = max(0., plus + z - params['k'])
        minus = max(0., minus - z - params['k'])
        if max(plus, minus) > params['h']:
            direction = 1 if plus >= minus else -1
            evidence = []
            if trace is not None:
                trace.append({'time': t, 'event': 'candidate', 'direction': direction,
                              'trigger_energy': max(plus, minus)})
    return -1


def detect_refined(x, params):
    """Confirm a CUSUM trigger using only subsequent observed samples."""
    return _refined(x, params)


def trace_refined(x, params):
    events = []
    alarm = _refined(x, params, events)
    return alarm, events
