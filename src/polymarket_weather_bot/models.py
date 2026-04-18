from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketCandidate:
    market_id: str
    question: str
    description: str
    slug: Optional[str]
    yes_token_id: Optional[str]
    no_token_id: Optional[str]
    active: bool
    closed: bool
    end_date_iso: Optional[str]


@dataclass
class ParsedWeatherRule:
    location_name: str
    metric: str
    comparator: str
    threshold_c: float
    date_label: Optional[str]
    unit: str = "C"


@dataclass
class LocationCoordinates:
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    admin1: Optional[str] = None


@dataclass
class ForecastEstimate:
    expected_max_c: float
    probability_yes: float
    sigma_c: float
    source: str


@dataclass
class OrderBookSnapshot:
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    last_trade_price: Optional[float]


@dataclass
class TradeSignal:
    market_id: str
    question: str
    location_name: str
    threshold_c: float
    expected_max_c: float
    probability_yes: float
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    fair_yes_price: float
    edge_buy_yes: Optional[float]
    action: str
    note: str
