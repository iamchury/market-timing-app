import yfinance as yf

def load_history(ticker, period='2y', auto_adjust=False):
    data = yf.download(ticker, period=period, auto_adjust=auto_adjust, progress=False)
    if data.empty: raise ValueError(f'No data available for {ticker}')
    if hasattr(data.columns, 'levels'): data.columns = data.columns.get_level_values(0)
    if 'Close' not in data: raise ValueError(f'Close data unavailable for {ticker}')
    return data[['Close']].dropna()
