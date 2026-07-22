import sys
import html
from pathlib import Path

# Streamlit Community Cloud runs app.py from the repository root and does not
# automatically add a src-layout package to sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st
import plotly.graph_objects as go
from market_timing.config import load_config
from market_timing.data_provider import load_history
from market_timing.analyzer import analyze
from market_timing.formatting import format_price

st.set_page_config(page_title='Market Timing', page_icon='📈', layout='wide')
st.markdown("""
<style>
/* Keep the wide desktop layout, but use the full viewport on phones. */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.6rem 2rem;
    }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.15rem !important; }
    [data-testid="stDataFrame"] {
        overflow-x: auto;
    }
    [data-testid="stPlotlyChart"] {
        width: 100% !important;
    }
}
.summary-table-wrap {
    width: 100%;
    overflow-x: auto;
}
.summary-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.875rem;
    white-space: nowrap;
}
.summary-table th, .summary-table td {
    padding: 0.5rem 0.55rem;
    border-right: 1px solid #30333d;
    border-bottom: 1px solid #30333d;
    text-align: left;
}
.summary-table th {
    background: #1b1e26;
    color: #aeb4c0;
    font-weight: 500;
}
.summary-table td:first-child, .summary-table th:first-child {
    border-left: 1px solid #30333d;
}
.summary-table thead th:first-child { border-top-left-radius: 0.45rem; }
.summary-table thead th:last-child { border-top-right-radius: 0.45rem; }
.summary-table tbody tr:last-child td:first-child { border-bottom-left-radius: 0.45rem; }
.summary-table tbody tr:last-child td:last-child { border-bottom-right-radius: 0.45rem; }
.summary-table a { color: #d8e7ff; text-decoration: none; font-weight: 600; }
.summary-table a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)
cfg = load_config()
st.title('Market Timing')
results = {}
for ticker in cfg['summary_order']:
    inst = cfg['instrument_map'][ticker]
    try: results[ticker] = analyze(load_history(ticker, cfg['data']['history_period'], cfg['data']['auto_adjust']), inst, cfg)
    except Exception as exc: results[ticker] = {'error': str(exc), 'display_name': inst.display_name, 'ticker': ticker, 'currency': inst.currency}
st.subheader('Market Timing Summary')
rows = []
for ticker in cfg['summary_order']:
    r = results[ticker]
    rows.append({'Instrument': r['display_name'], 'Primary Signal': r.get('primary_signal','—'), 'Latest Date': r.get('latest_date','Unavailable'), 'Latest Price': format_price(r['latest_price'],r['currency']) if 'latest_price' in r else 'Unavailable', 'EMA Trend Score': r.get('trend_score','—'), 'EMA Alignment Score': r.get('alignment_score','—'), 'EMA Order': r.get('ema_order','—'), 'Classification': r.get('classification','Unavailable'), 'EMA50 Trend': r.get('ema50_trend','—'), 'Active Condition': ', '.join(r.get('active_conditions',[]))})
summary_columns = list(rows[0].keys()) if rows else []
summary_html = ['<div class="summary-table-wrap"><table class="summary-table"><thead><tr>']
summary_html.append(''.join(f'<th>{html.escape(str(column))}</th>' for column in summary_columns))
summary_html.append('</tr></thead><tbody>')
signal_colors = {
    'TURN_UP': '#2eaf67',
    'TURN_DOWN': '#e05252',
    'SELL_CAUTION': '#f28ab2',
    'DEAD_CROSS': '#aeb4c0',
    'GOLDEN_CROSS': '#e5b94c',
}
for ticker, row in zip(cfg['summary_order'], rows):
    anchor = f'{ticker.lower().replace(".", "-")}-market-timing'
    summary_html.append('<tr>')
    for column in summary_columns:
        value = html.escape(str(row[column]))
        if column == 'Instrument':
            value = f'<a href="#{anchor}">{value}</a>'
        elif column == 'Primary Signal':
            color = signal_colors.get(str(row[column]), '#d8dde7')
            value = f'<span style="color:{color};font-weight:600">{value}</span>'
        summary_html.append(f'<td>{value}</td>')
    summary_html.append('</tr>')
summary_html.append('</tbody></table></div>')
st.markdown(''.join(summary_html), unsafe_allow_html=True)
for ticker in cfg['detail_order']:
    r = results[ticker]; st.divider(); st.header(f"{r['display_name']} Market Timing", anchor=f'{ticker.lower().replace(".", "-")}-market-timing')
    if 'error' in r: st.warning(f"{ticker} unavailable: {r['error']}"); continue
    st.metric('Overall', r['classification'], r['primary_signal']); st.metric('EMA Trend Score', r['trend_score'])
    st.write(r['rationale'])
    f = r['chart_frame']; fig = go.Figure()
    line_widths = {'EMA5': 3, 'EMA10': 3, 'EMA20': 3}
    for col in ['Close','EMA5','EMA10','EMA20','EMA30','EMA50','Prior High']:
        if col in f:
            fig.add_trace(go.Scatter(x=f.index, y=f[col], name=col, mode='lines', line={'width': line_widths.get(col, 1.5)}))
    event_colors = {
        'BUY': '#2e7d32', 'SELL': '#d32f2f',
        'GOLDEN_CROSS': '#00a86b', 'DEAD_CROSS': '#e53935',
        'STRONG_SELL': '#b71c1c', 'VERY_STRONG_SELL': '#7f0000',
        'SELL_CAUTION': '#f57c00', 'TURN_UP': '#1565c0',
        'TURN_DOWN': '#6a1b9a',
    }
    chart_start = f.index.min()
    chart_end = f.index.max()
    for event in r['events']:
        event_date = event['date']
        if chart_start <= event_date <= chart_end:
            signal = event['signal']
            fig.add_vline(
                x=event_date,
                line_color=event_colors.get(signal, '#757575'),
                line_width=4 if signal in {'BUY', 'SELL'} else 1,
                line_dash='solid' if signal in {'BUY', 'SELL'} else 'dash',
                annotation_text=signal,
                annotation_position='top right',
                opacity=0.75,
            )
    # Always mark the most recent trading day, even when no trade event was
    # generated for it. Use the requested trade-event styling for this marker.
    latest_events = [event for event in r['events']
                     if event['date'].date() == chart_end.date()]
    latest_signal = next(
        (event['signal'] for event in latest_events
         if event['signal'] in {'BUY', 'SELL', 'SELL_CAUTION'}),
        None,
    )
    latest_color = {
        'BUY': '#2e7d32',
        'SELL': '#d32f2f',
        'SELL_CAUTION': '#d32f2f',
    }.get(latest_signal, '#9e9e9e')
    fig.add_vline(
        x=chart_end,
        line_color=latest_color,
        line_width=3 if latest_signal in {'BUY', 'SELL'} else 2,
        line_dash='dot' if latest_signal in {None, 'SELL_CAUTION'} else 'solid',
        annotation_text=latest_signal or 'Latest day',
        annotation_position='top right',
        opacity=0.85,
    )
    fig.update_layout(height=420, hovermode='x unified', margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displaylogo': False})
    st.dataframe(r['events'], use_container_width=True, hide_index=True)
