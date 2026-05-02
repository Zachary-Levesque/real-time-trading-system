from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.core.config import get_settings
from app.processing.storage import LocalMarketDataReader
from app.recommendation.storage import LocalRecommendationReader, LocalSignalReader
from app.storage.cache import RedisCache
from app.storage.db import create_session_factory
from app.storage.repository import PostgresStorageRepository
from app.storage.sync import StorageSyncService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Persist the latest local market, signal, and recommendation data into PostgreSQL and Redis.",
    )
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to persist. Defaults to AAPL.")
    return parser


def main() -> int:
    settings = get_settings()
    args = build_parser().parse_args()

    repository = PostgresStorageRepository(create_session_factory(settings.database_url))
    cache = RedisCache(settings.redis_url)
    service = StorageSyncService(
        repository=repository,
        cache=cache,
        market_data_reader=LocalMarketDataReader(Path(settings.market_data_dir)),
        signal_reader=LocalSignalReader(Path(settings.signal_data_dir)),
        recommendation_reader=LocalRecommendationReader(Path(settings.recommendation_data_dir)),
    )

    try:
        result = service.sync_ticker(args.ticker)
    except Exception as exc:
        print(f"[storage-sync-error] {exc}", file=sys.stderr)
        print(
            (
                "Storage sync requires reachable PostgreSQL and Redis services. "
                "For local terminal runs, use localhost-based values such as "
                "'postgresql+psycopg://postgres:postgres@localhost:5432/trading_system' "
                f"and '{settings.redis_url}'."
            ),
            file=sys.stderr,
        )
        print(
            "If you want to use Docker networking instead, install/start Docker and run 'docker compose up --build' first.",
            file=sys.stderr,
        )
        return 1

    print(json.dumps(result.__dict__, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
