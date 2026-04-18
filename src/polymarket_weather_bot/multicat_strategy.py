from __future__ import annotations

from typing import Iterable, Optional

from .models import MarketCandidate, OrderBookSnapshot
from .multicat_models import GenericMarketSignal


CATEGORY_KEYWORDS = {
    "weather": ["weather", "temperature", "storm", "rain", "snow", "wind", "climate", "hurricane"],
    "crypto": ["bitcoin", "btc", "ethereum", "eth", "solana", "sol", "crypto", "token", "price"],
    "sports": ["nba", "nfl", "mlb", "soccer", "champions league", "ufc", "tennis", "match", "game"],
    "politics": ["election", "president", "senate", "prime minister", "vote", "poll", "government"],
    "business": ["fed", "inflation", "cpi", "gdp", "earnings", "tesla", "apple", "nvidia", "economy"],
    "pop": ["movie", "album", "oscar", "grammy", "celebrity", "tv show"],
}


def detect_category(question: str, description: str) -> str:
    haystack = f"{question} {description}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category
    return "other"


def _midpoint(best_bid: Optional[float], best_ask: Optional[float]) -> Optional[float]:
    if best_bid is None or best_ask is None:
        return None
    return (best_bid + best_ask) / 2.0


def _spread_penalty(spread: Optional[float]) -> float:
    if spread is None:
        return 0.15
    if spread <= 0.01:
        return 0.0
    if spread <= 0.03:
        return 0.05
    if spread <= 0.06:
        return 0.15
    return 0.35


def _liquidity_confidence(book: OrderBookSnapshot) -> float:
    if book.best_bid is None or book.best_ask is None:
        return 0.2
    if book.spread is None:
        return 0.3
    if book.spread <= 0.01:
        return 0.9
    if book.spread <= 0.03:
        return 0.75
    if book.spread <= 0.06:
        return 0.55
    return 0.3


def _clarity_confidence(market: MarketCandidate) -> float:
    q = market.question.lower()
    score = 0.5
    if "will" in q:
        score += 0.05
    if " by " in q or " before " in q or " on " in q:
        score += 0.1
    if "according to" in q:
        score += 0.1
    if len(q) < 140:
        score += 0.1
    if "or" in q and "win" not in q:
        score -= 0.1
    return max(0.2, min(0.95, score))


def build_generic_signal(market: MarketCandidate, book: OrderBookSnapshot) -> GenericMarketSignal:
    category = detect_category(market.question, market.description)
    midpoint = _midpoint(book.best_bid, book.best_ask)
    liquidity_conf = _liquidity_confidence(book)
    clarity_conf = _clarity_confidence(market)

    confidence = round((liquidity_conf * 0.55) + (clarity_conf * 0.45), 4)

    score = confidence
    score -= _spread_penalty(book.spread)
    if midpoint is None:
        score -= 0.2
    elif midpoint < 0.08 or midpoint > 0.92:
        score -= 0.12

    risk_flags = []
    if book.best_bid is None or book.best_ask is None:
        risk_flags.append("missing_book_side")
    if book.spread is not None and book.spread > 0.06:
        risk_flags.append("wide_spread")
    if midpoint is not None and (midpoint < 0.08 or midpoint > 0.92):
        risk_flags.append("extreme_price")
    if category == "other":
        risk_flags.append("unknown_category")

    if confidence >= 0.72 and book.spread is not None and book.spread <= 0.03:
        action = "WATCH_PAPER"
        rationale = "High clarity and tighter spread"
    elif confidence >= 0.58:
        action = "MONITOR"
        rationale = "Reasonable setup but not clean enough"
    else:
        action = "SKIP"
        rationale = "Weak structure or liquidity"

    return GenericMarketSignal(
        market_id=market.market_id,
        question=market.question,
        category=category,
        best_bid=book.best_bid,
        best_ask=book.best_ask,
        spread=book.spread,
        last_trade_price=book.last_trade_price,
        midpoint_price=midpoint,
        yes_price_reference=book.best_ask,
        no_price_reference=(1.0 - book.best_bid) if book.best_bid is not None else None,
        score=round(score, 4),
        confidence=confidence,
        action=action,
        rationale=rationale,
        risk_flags=",".join(risk_flags),
    )
