# Market Timing

EMA-based market timing dashboard for QQQ, SOXX, Micron, Samsung Electronics, and SK hynix. This is informational software, not investment advice.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Run tests with `pytest -q`. EMA values use the full downloaded history and display the latest 100 trading days. Signals are based on EMA5 crossovers, EMA50 trend, and a configurable 252-day drawdown caution.
