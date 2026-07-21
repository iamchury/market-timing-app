def _cmp(a, b, tolerance=1e-8): return 0 if abs(a-b) <= tolerance else (1 if a > b else -1)

EMA_ALIGNMENT_PERIODS = (5, 10, 20, 30, 50)

def ema_alignment(row):
    periods = EMA_ALIGNMENT_PERIODS
    inversions = sum(row[f'EMA{left}'] <= row[f'EMA{right}'] for i, left in enumerate(periods) for right in periods[i + 1:])
    order = ' > '.join(f'EMA{p}' for p in sorted(periods, key=lambda p: row[f'EMA{p}'], reverse=True))
    return {'inversion_count': int(inversions), 'alignment_score': 10 - 2 * inversions, 'ema_order': order}
def trend_score(row, trends=None, tolerance=1e-8):
    periods = (5, 10, 15, 20, 30, 50)
    rising = trends and all(trends.get(period) == 'RISING' for period in periods)
    falling = trends and all(trends.get(period) == 'FALLING' for period in periods)
    bullish_order = all(row[f'EMA{a}'] > row[f'EMA{b}'] for a, b in zip(periods, periods[1:]))
    bearish_order = all(row[f'EMA{a}'] < row[f'EMA{b}'] for a, b in zip(periods, periods[1:]))
    if bullish_order and rising: return 10
    if bearish_order and falling: return -10
    if bearish_order: return -7
    if row.EMA5 > row.EMA10 > row.EMA20: return 7
    if row.EMA5 > row.EMA10: return 4
    if row.EMA5 < row.EMA10 and trends and trends.get(5) == 'FALLING': return -4
    return 0
def classification(score):
    if score == 10: return 'VERY_BULLISH'
    if score >= 8: return 'STRONG_BULLISH'
    if score >= 5: return 'BULLISH'
    if score >= 2: return 'MILD_BULLISH'
    if score >= -1: return 'NEUTRAL'
    if score >= -4: return 'MILD_BEARISH'
    if score >= -7: return 'BEARISH'
    if score >= -9: return 'STRONG_BEARISH'
    return 'VERY_BEARISH'
