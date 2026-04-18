from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import requests

from .config import SETTINGS
from .models import TradeSignal


class TelegramAlerter:
    def __init__(self) -> None:
        self.enabled = bool(SETTINGS.enable_telegram and SETTINGS.telegram_bot_token and SETTINGS.telegram_chat_id)
        self.state_path = Path(SETTINGS.dedupe_state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, float]:
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text())
        except Exception:
            return {}

    def _save_state(self) -> None:
        self.state_path.write_text(json.dumps(self.state, indent=2, sort_keys=True))

    def should_alert(self, signal: TradeSignal) -> bool:
        if signal.action != "BUY_YES_PAPER":
            return False
        if signal.edge_buy_yes is None or signal.edge_buy_yes < SETTINGS.alert_min_edge:
            return False
        previous_edge = self.state.get(signal.market_id)
        if previous_edge is None:
            return True
        return signal.edge_buy_yes >= previous_edge + 0.02

    def format_message(self, signal: TradeSignal) -> str:
        return (
            "📈 Polymarket paper signal\n"
            f"Market: {signal.question}\n"
            f"Location: {signal.location_name}\n"
            f"Expected max: {signal.expected_max_c:.1f}°C\n"
            f"Threshold: {signal.threshold_c:.1f}°C\n"
            f"Model YES: {signal.probability_yes:.3f}\n"
            f"Best ask: {signal.best_ask}\n"
            f"Spread: {signal.spread}\n"
            f"Edge: {signal.edge_buy_yes:.3f}\n"
            f"Action: {signal.action}\n"
            f"Note: {signal.note}"
        )

    def send(self, signal: TradeSignal) -> bool:
        if not self.enabled:
            return False
        url = f"https://api.telegram.org/bot{SETTINGS.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": SETTINGS.telegram_chat_id,
            "text": self.format_message(signal),
        }
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        self.state[signal.market_id] = signal.edge_buy_yes or 0.0
        self._save_state()
        return True
