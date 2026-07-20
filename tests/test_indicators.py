import pandas as pd
from market_timing.indicators import add_emas
def test_ema_matches_pandas_reference():
    s = pd.Series(range(1, 80), dtype=float)
    assert add_emas(s).EMA50.equals(s.ewm(span=50, adjust=False, min_periods=50).mean())
