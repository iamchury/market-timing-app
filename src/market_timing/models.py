from dataclasses import dataclass, field
from typing import Any
import pandas as pd

@dataclass(frozen=True)
class InstrumentConfig:
    ticker: str
    display_name: str
    currency: str

@dataclass
class MarketTimingResult:
    ticker: str
    display_name: str
    currency: str
    latest_date: Any
    latest_price: float
    ema_values: dict
    ema50_trend: str
    ema50_slope: float
    latest_ema50_turn: str | None
    trend_score: int
    classification: str
    rationale: str
    primary_signal: str
    active_conditions: list[str] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)
    chart_frame: pd.DataFrame = field(default_factory=pd.DataFrame)
