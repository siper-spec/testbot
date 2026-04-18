from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return float(value)


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    gamma_base_url: str = os.getenv("GAMMA_BASE_URL", "https://gamma-api.polymarket.com")
    clob_base_url: str = os.getenv("CLOB_BASE_URL", "https://clob.polymarket.com")
    openmeteo_forecast_url: str = os.getenv("OPENMETEO_FORECAST_URL", "https://api.open-meteo.com/v1/forecast")
    openmeteo_geocode_url: str = os.getenv("OPENMETEO_GEOCODE_URL", "https://geocoding-api.open-meteo.com/v1/search")

    request_timeout_seconds: int = _get_int("REQUEST_TIMEOUT_SECONDS", 20)
    active_events_limit: int = _get_int("ACTIVE_EVENTS_LIMIT", 150)
    max_markets_to_evaluate: int = _get_int("MAX_MARKETS_TO_EVALUATE", 75)

    min_required_edge: float = _get_float("MIN_REQUIRED_EDGE", 0.05)
    fee_buffer: float = _get_float("FEE_BUFFER", 0.018)
    slippage_buffer: float = _get_float("SLIPPAGE_BUFFER", 0.01)
    max_allowed_spread: float = _get_float("MAX_ALLOWED_SPREAD", 0.05)

    temperature_sigma_c: float = _get_float("TEMPERATURE_SIGMA_C", 1.8)
    confidence_floor: float = _get_float("CONFIDENCE_FLOOR", 0.02)
    confidence_ceiling: float = _get_float("CONFIDENCE_CEILING", 0.98)

    output_csv_path: str = os.getenv("OUTPUT_CSV_PATH", "data/signals.csv")

    enable_telegram: bool = _get_bool("ENABLE_TELEGRAM", False)
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    alert_min_edge: float = _get_float("ALERT_MIN_EDGE", 0.07)
    loop_interval_seconds: int = _get_int("LOOP_INTERVAL_SECONDS", 900)
    dedupe_state_path: str = os.getenv("DEDUPE_STATE_PATH", "data/alert_state.json")


SETTINGS = Settings()
