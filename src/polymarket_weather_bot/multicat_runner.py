from __future__ import annotations

import pathlib
from dataclasses import asdict
from typing import List

import pandas as pd

from .config import SETTINGS
from .multicat_models import GenericMarketSignal
from .multicat_strategy import build_generic_signal
from .polymarket import PolymarketClient
from .telegram import TelegramAlerter


def run_multicat_once(send_alerts: bool = False) -> List[GenericMarketSignal]:
    polymarket = PolymarketClient()
    alerter = TelegramAlerter()

    events = polymarket.fetch_active_events(limit=SETTINGS.active_events_limit)
    candidates = polymarket.extract_market_candidates(events)
    candidates = candidates[: SETTINGS.max_markets_to_evaluate]

    signals: List[GenericMarketSignal] = []
    for market in candidates:
        if not market.yes_token_id:
            continue

        try:
            book = polymarket.get_order_book(market.yes_token_id)
        except Exception as exc:
            print(f"Skipping market {market.market_id}: {exc}")
            continue

        signal = build_generic_signal(market, book)
        signals.append(signal)
        print(
            f"{signal.action:>10} | score={signal.score:.3f} | "
            f"conf={signal.confidence:.3f} | spread={signal.spread} | {signal.question}"
        )

        if send_alerts and signal.action == "WATCH_PAPER" and signal.score >= 0.65:
            try:
                alerter.send_generic(signal)
                print(f"Telegram alert sent for market {signal.market_id}")
            except Exception as exc:
                print(f"Telegram alert failed for market {signal.market_id}: {exc}")

    output_path = pathlib.Path("data/multicat_signals.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frame = pd.DataFrame(asdict(signal) for signal in signals)
    if not frame.empty:
        frame.sort_values(by=["action", "score"], ascending=[True, False], inplace=True, na_position="last")
    frame.to_csv(output_path, index=False)
    print(f"\nSaved {len(frame)} multi-category signals to {output_path}")
    return signals
