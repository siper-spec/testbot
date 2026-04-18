from __future__ import annotations

from .multicat_runner import run_multicat_once


def main() -> None:
    run_multicat_once(send_alerts=False)


if __name__ == "__main__":
    main()
