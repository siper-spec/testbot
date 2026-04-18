from __future__ import annotations

import pathlib
from dataclasses import asdict
from typing import List

import pandas as pd

from .config import SETTINGS
from .parser import looks_like_weather_market, parse_temperature_threshold_market
from .polymarket import PolymarketClient
from .strategy import build_signal
from .telegram import TelegramAlerter
from .weather import OpenMeteoClient
from .models import TradeSignal


def run_once(send_alerts: bool = False) -> List[TradeSignal]:
    polymarket = PolymarketClient()
    weather = OpenMeteoClient()
    alerter = TelegramAlerter()

    events = polymarket.fetch_active_events(limit=SETTINGS.active_events_limit)
    candidates = polymarket.extract_market_candidates(events)

    weather_candidates = [m for m in candidates if looks_like_weather_market(m)]
    weather_candidates = weather_candidates[: SETTINGS.max_markets_to_evaluate]

    signals: List[TradeSignal] = []
    for market in weather_candidates:
        if not market.yes_token_id:
            continue

        rule = parse_temperature_threshold_market(market)
        if not rule:
            continue

        location = weather.geocode(rule.location_name)
        if not location:
            continue

        try:
            forecast = weather.forecast_temperature_probability(location, rule)
            book = polymarket.get_order_book(market.yes_token_id)
        except Exception as exc:
            print(f"Skipping market {market.market_id}: {exc}")
            continue

        signal = build_signal(market, rule, forecast, book)
        signals.append(signal)
        print(
            f"{signal.action:>14} | edge={signal.edge_buy_yes!s:>8} | "
            f"p_yes={signal.probability_yes:.3f} | ask={signal.best_ask} | {signal.question}"
        )

        if send_alerts and alerter.should_alert(signal):
            try:
                alerter.send(signal)
                print(f"Telegram alert sent for market {signal.market_id}")
            except Exception as exc:
                print(f"Telegram alert failed for market {signal.market_id}: {exc}")

    output_path = pathlib.Path(SETTINGS.output_csv_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frame = pd.DataFrame(asdict(signal) for signal in signals)
    if not frame.empty:
        frame.sort_values(by=["action", "edge_buy_yes"], ascending=[True, False], inplace=True, na_position="last")
    frame.to_csv(output_path, index=False)
    print(f"\nSaved {len(frame)} signals to {output_path}")
    return signals
