from __future__ import annotations

from .config import SETTINGS
from .models import ForecastEstimate, MarketCandidate, OrderBookSnapshot, ParsedWeatherRule, TradeSignal
from .pricing import compute_buy_yes_edge



def build_signal(
    market: MarketCandidate,
    rule: ParsedWeatherRule,
    forecast: ForecastEstimate,
    book: OrderBookSnapshot,
) -> TradeSignal:
    fair_yes_price = forecast.probability_yes
    edge_buy_yes = compute_buy_yes_edge(
        fair_yes_price=fair_yes_price,
        best_ask=book.best_ask,
        spread=book.spread,
    )

    action = "SKIP"
    note = "No edge"

    if book.best_ask is None:
        note = "No ask available"
    elif book.spread is not None and book.spread > SETTINGS.max_allowed_spread:
        note = f"Spread too wide ({book.spread:.4f})"
    elif edge_buy_yes is not None and edge_buy_yes >= SETTINGS.min_required_edge:
        action = "BUY_YES_PAPER"
        note = "Edge above threshold after buffers"

    return TradeSignal(
        market_id=market.market_id,
        question=market.question,
        location_name=rule.location_name,
        threshold_c=rule.threshold_c,
        expected_max_c=forecast.expected_max_c,
        probability_yes=forecast.probability_yes,
        best_bid=book.best_bid,
        best_ask=book.best_ask,
        spread=book.spread,
        fair_yes_price=fair_yes_price,
        edge_buy_yes=edge_buy_yes,
        action=action,
        note=note,
    )
