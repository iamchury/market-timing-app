from .indicators import add_emas, prior_high
from .ema_trend import trend_from_slope, turns
from .signals import trend_score, classification

def analyze(frame, instrument, cfg):
    close = frame['Close'].dropna().sort_index()
    x = add_emas(close, cfg['indicators']['ema_periods'], cfg['indicators']['ema_adjust'])
    x['Prior High'] = prior_high(close, cfg['drawdown_caution']['rolling_high_window'])
    x['Drawdown %'] = (x.Close / x['Prior High'] - 1) * 100
    x = x.dropna(subset=['EMA50'])
    slopes, trends = x.EMA50.diff(), x.EMA50.diff().map(lambda v: trend_from_slope(v, cfg['indicators']['equality_tolerance']))
    turn_list, events = turns(trends.tolist()), []
    for i in range(1, len(x)):
        prev, cur = x.iloc[i-1], x.iloc[i]
        # SELL: EMA5 crosses below EMA10.
        if prev.EMA5 >= prev.EMA10 > cur.EMA5:
            events.append({'date': x.index[i], 'event_type': 'SELL', 'signal': 'SELL', 'cross_basis': 'EMA5/EMA10', 'close': cur.Close})
        # BUY: EMA10 crosses above EMA20. The previous EMA10 must be at or
        # below EMA20, while the current EMA10 must be strictly above it.
        if prev.EMA10 <= prev.EMA20 and cur.EMA10 > cur.EMA20:
            events.append({'date': x.index[i], 'event_type': 'BUY', 'signal': 'BUY', 'cross_basis': 'EMA10/EMA20', 'close': cur.Close})
        if turn_list[i]: events.append({'date': x.index[i], 'event_type': 'EMA50_TURN', 'signal': turn_list[i], 'close': cur.Close})
        threshold = cfg['drawdown_caution']['threshold_percent']
        if cur['Drawdown %'] <= threshold < prev['Drawdown %']: events.append({'date': x.index[i], 'event_type': 'DRAWDOWN_CAUTION', 'signal': 'SELL_CAUTION', 'drawdown': cur['Drawdown %'], 'close': cur.Close})
    chart_frame = x.tail(cfg['data']['chart_trading_days'])
    chart_start = chart_frame.index.min()
    events = [event for event in events if event['date'] >= chart_start]
    row, score = x.iloc[-1], trend_score(x.iloc[-1], trends.iloc[-1], cfg['indicators']['equality_tolerance'])
    return {'ticker': instrument.ticker, 'display_name': instrument.display_name, 'currency': instrument.currency, 'latest_date': x.index[-1], 'latest_price': float(row.Close), 'ema_values': {f'EMA{p}': float(row[f'EMA{p}']) for p in cfg['indicators']['ema_periods']}, 'ema50_trend': trends.iloc[-1], 'ema50_slope': float(slopes.iloc[-1]), 'latest_ema50_turn': turn_list[-1], 'trend_score': score, 'classification': classification(score), 'rationale': f'EMA50 is {trends.iloc[-1].lower()} with score {score}.', 'primary_signal': events[-1]['signal'] if events else 'HOLD', 'active_conditions': ['DRAWDOWN_CAUTION'] if row['Drawdown %'] <= threshold else [], 'events': events, 'chart_frame': chart_frame}
