from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .config import SETTINGS
from .models import ForecastEstimate, LocationCoordinates, ParsedWeatherRule
from .pricing import probability_temperature_above_threshold, clamp_probability


class OpenMeteoClient:
    def __init__(self) -> None:
        self.session = requests.Session()

    def _get(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = self.session.get(url, params=params, timeout=SETTINGS.request_timeout_seconds)
        response.raise_for_status()
        return response.json()

    def geocode(self, location_name: str) -> Optional[LocationCoordinates]:
        payload = self._get(
            SETTINGS.openmeteo_geocode_url,
            {"name": location_name, "count": 1, "language": "en", "format": "json"},
        )
        results = payload.get("results") or []
        if not results:
            return None
        result = results[0]
        return LocationCoordinates(
            name=result.get("name", location_name),
            latitude=float(result["latitude"]),
            longitude=float(result["longitude"]),
            country=result.get("country"),
            admin1=result.get("admin1"),
        )

    def forecast_temperature_probability(
        self,
        location: LocationCoordinates,
        rule: ParsedWeatherRule,
    ) -> ForecastEstimate:
        payload = self._get(
            SETTINGS.openmeteo_forecast_url,
            {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "daily": "temperature_2m_max",
                "timezone": "auto",
                "forecast_days": 7,
            },
        )

        daily = payload.get("daily") or {}
        temps = daily.get("temperature_2m_max") or []
        dates = daily.get("time") or []
        if not temps:
            raise ValueError(f"No forecast temperatures returned for {location.name}")

        expected_max_c = float(temps[0])
        if rule.date_label:
            lowered = rule.date_label.lower()
            for idx, date_str in enumerate(dates):
                if lowered in str(date_str).lower():
                    expected_max_c = float(temps[idx])
                    break

        probability_yes = probability_temperature_above_threshold(
            mean_c=expected_max_c,
            threshold_c=rule.threshold_c,
            sigma_c=SETTINGS.temperature_sigma_c,
        )
        return ForecastEstimate(
            expected_max_c=expected_max_c,
            probability_yes=clamp_probability(probability_yes),
            sigma_c=SETTINGS.temperature_sigma_c,
            source="Open-Meteo forecast API",
        )
