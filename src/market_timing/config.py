from pathlib import Path
import yaml
from .models import InstrumentConfig

def load_config(path=None):
    with Path(path or 'config/market_timing.yaml').open(encoding='utf-8') as f: c = yaml.safe_load(f)
    instruments = [InstrumentConfig(**x) for x in c['instruments']]
    tickers = {x.ticker for x in instruments}
    if len(tickers) != len(instruments): raise ValueError('Duplicate ticker')
    if any(x.currency not in {'USD', 'KRW'} for x in instruments): raise ValueError('Unsupported currency')
    for key in ('summary_order', 'detail_order'):
        if any(x not in tickers for x in c[key]): raise ValueError(f'{key} contains unknown ticker')
    if 50 not in c['indicators']['ema_periods']: raise ValueError('EMA50 is required')
    if c['data']['chart_trading_days'] < 1: raise ValueError('chart_trading_days must be positive')
    c['instrument_map'] = {x.ticker: x for x in instruments}
    return c
