from __future__ import annotations

import time

from .config import SETTINGS
from .multicat_runner import run_multicat_once


def main() -> None:
    print("Starting multi-category Telegram alert loop...")
    print(f"Loop interval: {SETTINGS.loop_interval_seconds} seconds")
    while True:
        try:
            run_multicat_once(send_alerts=True)
        except KeyboardInterrupt:
            print("Stopped by user.")
            break
        except Exception as exc:
            print(f"Loop error: {exc}")
        time.sleep(SETTINGS.loop_interval_seconds)


if __name__ == "__main__":
    main()
