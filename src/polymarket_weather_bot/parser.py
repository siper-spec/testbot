from __future__ import annotations

import re
from typing import Optional

from .models import MarketCandidate, ParsedWeatherRule


TEMPERATURE_PATTERNS = [
    re.compile(
        r"(?P<location>[A-Za-zÀ-ÿ' .-]+?)\s+(?:on|for)\s+(?P<date>[A-Za-z0-9 ,:-]+?)\s+(?:be|is)?\s*(?:above|over)\s*(?P<threshold>-?\d+(?:\.\d+)?)\s*°?C",
        re.IGNORECASE,
    ),
    re.compile(
        r"will\s+the\s+(?:high(?:est)?\s+)?temperature\s+in\s+(?P<location>[A-Za-zÀ-ÿ' .-]+?)\s+(?:on|for)\s+(?P<date>[A-Za-z0-9 ,:-]+?)\s+(?:be|is)?\s*(?:above|over)\s*(?P<threshold>-?\d+(?:\.\d+)?)\s*°?C",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:high(?:est)?\s+temperature\s+in\s+)?(?P<location>[A-Za-zÀ-ÿ' .-]+?)\s+(?:above|over)\s*(?P<threshold>-?\d+(?:\.\d+)?)\s*°?C",
        re.IGNORECASE,
    ),
]


WEATHER_KEYWORDS = (
    "temperature",
    "highest temperature",
    "weather",
    "rain",
    "snow",
    "hurricane",
    "storm",
    "wind",
    "climate",
)


def looks_like_weather_market(market: MarketCandidate) -> bool:
    haystack = f"{market.question} {market.description}".lower()
    return any(keyword in haystack for keyword in WEATHER_KEYWORDS)



def parse_temperature_threshold_market(market: MarketCandidate) -> Optional[ParsedWeatherRule]:
    text_candidates = [market.question or "", market.description or ""]
    for text in text_candidates:
        for pattern in TEMPERATURE_PATTERNS:
            match = pattern.search(text)
            if match:
                location = " ".join(match.group("location").split())
                threshold = float(match.group("threshold"))
                date_label = match.groupdict().get("date")
                return ParsedWeatherRule(
                    location_name=location.strip(" ?,."),
                    metric="daily_high_temperature",
                    comparator=">",
                    threshold_c=threshold,
                    date_label=date_label.strip() if date_label else None,
                )

    return None
