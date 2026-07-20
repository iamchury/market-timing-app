def _cmp(a, b, tolerance=1e-8): return 0 if abs(a-b) <= tolerance else (1 if a > b else -1)
def trend_score(row, trend, tolerance=1e-8):
    return max(-10, min(10, (5 if trend == 'RISING' else -5 if trend == 'FALLING' else 0) + 2*_cmp(row.EMA5,row.EMA50,tolerance) + _cmp(row.EMA5,row.EMA20,tolerance) + _cmp(row.EMA5,row.EMA15,tolerance) + _cmp(row.EMA5,row.EMA10,tolerance)))
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
