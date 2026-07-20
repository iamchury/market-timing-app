import pandas as pd

def add_emas(close, periods=(5, 10, 15, 20, 50), adjust=False):
    out = pd.DataFrame({'Close': close.copy()})
    for p in periods: out[f'EMA{p}'] = close.ewm(span=p, adjust=adjust, min_periods=p).mean()
    return out

def prior_high(close, window=252): return close.shift(1).rolling(window, min_periods=1).max()
