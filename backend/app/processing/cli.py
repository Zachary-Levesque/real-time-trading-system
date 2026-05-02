from __future__ import annotations

import argparse
import json
import sys

from app.processing.exceptions import SignalProcessingError
from app.processing.service import SignalProcessingService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate deterministic trading signals from normalized market data.",
    )
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to process. Defaults to AAPL.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    service = SignalProcessingService()

    try:
        result = service.process(args.ticker)
    except SignalProcessingError as exc:
        print(f"[processing-error] {exc}", file=sys.stderr)
        return 1

    summary = {
        "ticker": result.signal_result.ticker,
        "timestamp": result.signal_result.timestamp.isoformat(),
        "signals": result.signal_result.data.values.model_dump(),
        "output_path": str(result.output_path),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
