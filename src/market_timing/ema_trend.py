def trend_from_slope(slope, tolerance=1e-8):
    if slope > tolerance: return 'RISING'
    if slope < -tolerance: return 'FALLING'
    return 'FLAT'

def turns(trends):
    last, result = None, []
    for trend in trends:
        if trend in ('RISING', 'FALLING'):
            result.append(None if last is None or trend == last else ('TURN_UP' if trend == 'RISING' else 'TURN_DOWN'))
            last = trend
        else: result.append(None)
    return result
