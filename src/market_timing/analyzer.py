from .indicators import add_emas, prior_high
from .ema_trend import trend_from_slope, turns
from .signals import trend_score, classification

def analyze(frame, instrument, cfg):
    close = frame['Close'].dropna().sort_index()
    x = add_emas(close, cfg['indicators']['ema_periods'], cfg['indicators']['ema_adjust'])
    x['Prior High'] = prior_high(close, cfg['drawdown_caution']['rolling_high_window'])
    x['Drawdown %'] = (x.Close / x['Prior High'] - 1) * 100
    x = x.dropna(subset=['EMA50'])
    tolerance = cfg['indicators']['equality_tolerance']
    slopes = {period: x[f'EMA{period}'].diff() for period in (10, 20, 30, 50)}
    trends = {period: slopes[period].map(lambda v: trend_from_slope(v, tolerance)) for period in (10, 20, 30, 50)}
    turn_list, events = turns(trends[30].tolist()), []
    for i in range(1, len(x)):
        prev, cur = x.iloc[i-1], x.iloc[i]
        sell_condition = all(trends[p].iloc[i] == 'FALLING' for p in (10, 20, 30))
        buy_condition = all(trends[p].iloc[i] == 'RISING' for p in (10, 20, 30))
        if sell_condition and turn_list[i] == 'TURN_DOWN':
            events.append({'date': x.index[i], 'event_type': 'SELL', 'signal': 'SELL', 'cross_basis': 'EMA10/EMA20/EMA30 slopes falling', 'close': cur.Close})
        if buy_condition and turn_list[i] == 'TURN_UP':
            events.append({'date': x.index[i], 'event_type': 'BUY', 'signal': 'BUY', 'cross_basis': 'EMA10/EMA20/EMA30 slopes rising', 'close': cur.Close})
        # EMA30/EMA50 trend crosses.
        if prev.EMA30 <= prev.EMA50 and cur.EMA30 > cur.EMA50:
            events.append({'date': x.index[i], 'event_type': 'GOLDEN_CROSS', 'signal': 'GOLDEN_CROSS', 'cross_basis': 'EMA30/EMA50', 'close': cur.Close})
        if prev.EMA30 >= prev.EMA50 and cur.EMA30 < cur.EMA50:
            events.append({'date': x.index[i], 'event_type': 'DEAD_CROSS', 'signal': 'DEAD_CROSS', 'cross_basis': 'EMA30/EMA50', 'close': cur.Close})
        if turn_list[i]: events.append({'date': x.index[i], 'event_type': 'EMA30_TURN', 'signal': turn_list[i], 'close': cur.Close})
        threshold = cfg['drawdown_caution']['threshold_percent']
        if cur['Drawdown %'] <= threshold < prev['Drawdown %']: events.append({'date': x.index[i], 'event_type': 'DRAWDOWN_CAUTION', 'signal': 'SELL_CAUTION', 'drawdown': cur['Drawdown %'], 'close': cur.Close})
    chart_frame = x.tail(cfg['data']['chart_trading_days'])
    chart_start = chart_frame.index.min()
    events = [event for event in events if event['date'] >= chart_start]
    row, score = x.iloc[-1], trend_score(x.iloc[-1], trends[50].iloc[-1], tolerance)
    return {'ticker': instrument.ticker, 'display_name': instrument.display_name, 'currency': instrument.currency, 'latest_date': x.index[-1], 'latest_price': float(row.Close), 'ema_values': {f'EMA{p}': float(row[f'EMA{p}']) for p in cfg['indicators']['ema_periods']}, 'ema50_trend': trends[50].iloc[-1], 'ema30_trend': trends[30].iloc[-1], 'ema50_slope': float(slopes[50].iloc[-1]), 'latest_ema30_turn': turn_list[-1], 'trend_score': score, 'classification': classification(score), 'rationale': f'EMA30 is {trends[30].iloc[-1].lower()} with score {score}.', 'primary_signal': events[-1]['signal'] if events else 'HOLD', 'active_conditions': ['DRAWDOWN_CAUTION'] if row['Drawdown %'] <= threshold else [], 'events': events, 'chart_frame': chart_frame}
