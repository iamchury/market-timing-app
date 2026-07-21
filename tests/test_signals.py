from market_timing.signals import classification, ema_alignment


def ema_row(values):
    return {f'EMA{period}': value for period, value in zip((5, 10, 20, 30, 50), values)}
def test_classification_bounds():
    assert classification(-10) == 'VERY_BEARISH'
    assert classification(10) == 'VERY_BULLISH'
    assert classification(0) == 'NEUTRAL'


def test_alignment_perfect_bullish():
    result = ema_alignment(ema_row([5, 4, 3, 2, 1]))
    assert result['inversion_count'] == 0
    assert result['alignment_score'] == 10


def test_alignment_perfect_bearish():
    result = ema_alignment(ema_row([1, 2, 3, 4, 5]))
    assert result['inversion_count'] == 10
    assert result['alignment_score'] == -10


def test_alignment_neutral():
    result = ema_alignment(ema_row([4, 1, 3, 5, 2]))
    assert result['alignment_score'] == 0


def test_alignment_mixed():
    result = ema_alignment(ema_row([5, 2, 4, 1, 3]))
    assert result['inversion_count'] == 3
    assert result['alignment_score'] == 4
