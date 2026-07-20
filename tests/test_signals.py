from market_timing.signals import classification
def test_classification_bounds():
    assert classification(-10) == 'VERY_BEARISH'
    assert classification(10) == 'VERY_BULLISH'
    assert classification(0) == 'NEUTRAL'
