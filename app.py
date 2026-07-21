import sys
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
    rows.append({'Instrument': r['display_name'], 'Ticker': ticker, 'Latest Date': r.get('latest_date','Unavailable'), 'Latest Price': format_price(r['latest_price'],r['currency']) if 'latest_price' in r else 'Unavailable', 'EMA Trend Score': r.get('trend_score','—'), 'Classification': r.get('classification','Unavailable'), 'EMA50 Trend': r.get('ema50_trend','—'), 'Primary Signal': r.get('primary_signal','—'), 'Active Condition': ', '.join(r.get('active_conditions',[]))})
st.dataframe(rows, use_container_width=True, hide_index=True)
for ticker in cfg['detail_order']:
    r = results[ticker]; st.divider(); st.header(f"{r['display_name']} Market Timing")
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
    fig.update_layout(height=420, hovermode='x unified', margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displaylogo': False})
    st.dataframe(r['events'], use_container_width=True, hide_index=True)
