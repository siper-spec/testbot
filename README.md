# Polymarket Weather Bot (Paper Trading + Telegram Alerts)

This project scans active Polymarket markets, looks for simple weather markets, estimates a fair probability using Open-Meteo, compares that estimate to the Polymarket order book, and writes paper-trading signals to CSV.

It **does not place real trades**.

## What it does
- Fetches active events from Polymarket Gamma API
- Filters likely weather markets
- Parses simple temperature-threshold style questions
- Geocodes the city and requests forecast data from Open-Meteo
- Estimates a fair YES probability
- Pulls the Polymarket order book from the public CLOB read endpoint
- Writes signals to `data/signals.csv`
- Optionally sends only stronger paper signals to Telegram

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run one scan
```bash
python -m src.polymarket_weather_bot.main
```

## Turn on Telegram alerts
1. Create a Telegram bot using BotFather
2. Copy `.env.example` to `.env`
3. Add your bot token and chat ID
4. Start the alert loop:

```bash
cp .env.example .env
python -m src.polymarket_weather_bot.alert_bot
```

## Recommended first settings
- `MIN_REQUIRED_EDGE=0.05`
- `ALERT_MIN_EDGE=0.07`
- `LOOP_INTERVAL_SECONDS=900`

## Files
- `data/signals.csv` — all paper signals from the latest scan
- `data/alert_state.json` — tracks already-alerted markets so Telegram does not spam you

## Important limitations
- This parser only handles a simple subset of weather markets
- It does not fully parse every settlement rule or special resolution condition
- It does not trade real money
- It does not use WebSocket order book streaming yet

## Safer rollout
1. Run paper scans locally
2. Watch Telegram alerts for a few days
3. Review whether the strongest alerts would actually have been good trades
4. Only then consider adding live execution
