from __future__ import annotations

import argparse
import json

from app.core.config import get_settings
from app.ingestion.exceptions import IngestionError
from app.ingestion.service import MarketDataIngestionService
from app.ingestion.storage import LocalMarketDataStorage


def build_parser() -> argparse.ArgumentParser:
    settings = get_settings()

    parser = argparse.ArgumentParser(
        description="Fetch and normalize market data for a ticker using yfinance.",
    )
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to fetch. Defaults to AAPL.")
    parser.add_argument(
        "--period",
        default=settings.default_market_period,
        help=f"yfinance history period. Defaults to {settings.default_market_period}.",
    )
    parser.add_argument(
        "--interval",
        default=settings.default_market_interval,
        help=f"yfinance history interval. Defaults to {settings.default_market_interval}.",
    )

    return parser


def main() -> int:
    settings = get_settings()
    args = build_parser().parse_args()

    service = MarketDataIngestionService(
        storage=LocalMarketDataStorage(settings.market_data_dir),
    )

    try:
        result = service.ingest(
            ticker=args.ticker,
            period=args.period,
            interval=args.interval,
        )
    except IngestionError as exc:
        print(f"[ingestion-error] {exc}")
        return 1

    summary = {
        "ticker": result.market_data.ticker,
        "timestamp": result.market_data.timestamp.isoformat(),
        "points": len(result.market_data.data.points),
        "output_path": str(result.output_path),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
