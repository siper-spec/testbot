from src.polymarket_weather_bot.pricing import probability_temperature_above_threshold


def test_probability_above_threshold_midpoint() -> None:
    result = probability_temperature_above_threshold(mean_c=20.0, threshold_c=20.0, sigma_c=2.0)
    assert 0.49 < result < 0.51
