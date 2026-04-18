from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class GenericMarketSignal:
    market_id: str
    question: str
    category: str
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    last_trade_price: Optional[float]
    midpoint_price: Optional[float]
    yes_price_reference: Optional[float]
    no_price_reference: Optional[float]
    score: float
    confidence: float
    action: str
    rationale: str
    risk_flags: str
