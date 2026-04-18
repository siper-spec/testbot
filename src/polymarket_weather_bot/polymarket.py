from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from .config import SETTINGS
from .models import MarketCandidate, OrderBookSnapshot


class PolymarketClient:
    def __init__(self) -> None:
        self.session = requests.Session()

    def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        response = self.session.get(url, params=params, timeout=SETTINGS.request_timeout_seconds)
        response.raise_for_status()
        return response.json()

    def fetch_active_events(self, limit: int | None = None) -> List[Dict[str, Any]]:
        params = {
            "active": "true",
            "closed": "false",
            "limit": limit or SETTINGS.active_events_limit,
        }
        return self._get(f"{SETTINGS.gamma_base_url}/events", params=params)

    def extract_market_candidates(self, events: List[Dict[str, Any]]) -> List[MarketCandidate]:
        markets: List[MarketCandidate] = []
        for event in events:
            for market in event.get("markets", []):
                outcomes = market.get("outcomes")
                clob_token_ids = market.get("clobTokenIds")
                yes_token_id: Optional[str] = None
                no_token_id: Optional[str] = None

                if isinstance(outcomes, str) and isinstance(clob_token_ids, str):
                    # The API often returns stringified arrays.
                    import json

                    try:
                        outcomes_list = json.loads(outcomes)
                        token_ids_list = json.loads(clob_token_ids)
                        mapping = dict(zip(outcomes_list, token_ids_list))
                        yes_token_id = mapping.get("Yes")
                        no_token_id = mapping.get("No")
                    except Exception:
                        pass
                elif isinstance(outcomes, list) and isinstance(clob_token_ids, list):
                    mapping = dict(zip(outcomes, clob_token_ids))
                    yes_token_id = mapping.get("Yes")
                    no_token_id = mapping.get("No")

                markets.append(
                    MarketCandidate(
                        market_id=str(market.get("id")),
                        question=market.get("question") or market.get("title") or "",
                        description=market.get("description") or "",
                        slug=market.get("slug"),
                        yes_token_id=yes_token_id,
                        no_token_id=no_token_id,
                        active=bool(market.get("active", False)),
                        closed=bool(market.get("closed", False)),
                        end_date_iso=market.get("endDate") or market.get("end_date_iso"),
                    )
                )
        return markets

    def get_order_book(self, token_id: str) -> OrderBookSnapshot:
        payload = self._get(f"{SETTINGS.clob_base_url}/book", params={"token_id": token_id})
        bids = payload.get("bids", []) or []
        asks = payload.get("asks", []) or []

        best_bid = float(bids[0]["price"]) if bids else None
        best_ask = float(asks[0]["price"]) if asks else None
        spread = None
        if best_bid is not None and best_ask is not None:
            spread = best_ask - best_bid

        last_trade_price = None
        if payload.get("last_trade_price") is not None:
            try:
                last_trade_price = float(payload["last_trade_price"])
            except Exception:
                last_trade_price = None

        return OrderBookSnapshot(
            best_bid=best_bid,
            best_ask=best_ask,
            spread=spread,
            last_trade_price=last_trade_price,
        )
