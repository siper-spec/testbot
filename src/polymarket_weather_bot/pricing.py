from __future__ import annotations

import math

from .config import SETTINGS


def clamp_probability(value: float) -> float:
    return max(SETTINGS.confidence_floor, min(SETTINGS.confidence_ceiling, value))



def standard_normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))



def probability_temperature_above_threshold(mean_c: float, threshold_c: float, sigma_c: float) -> float:
    if sigma_c <= 0:
        raise ValueError("sigma_c must be positive")
    z = (threshold_c - mean_c) / sigma_c
    return 1.0 - standard_normal_cdf(z)



def compute_buy_yes_edge(fair_yes_price: float, best_ask: float | None, spread: float | None) -> float | None:
    if best_ask is None:
        return None
    spread_penalty = max(0.0, spread or 0.0)
    return fair_yes_price - best_ask - SETTINGS.fee_buffer - SETTINGS.slippage_buffer - spread_penalty
