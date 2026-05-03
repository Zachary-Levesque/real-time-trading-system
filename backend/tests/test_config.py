import os

import pytest

from app.core.config import Settings


def test_settings_parse_json_list_env_values(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:5173","http://127.0.0.1:5173"]')
    monkeypatch.setenv("BACKGROUND_WORKER_TICKERS", '["aapl","msft"]')

    settings = Settings(_env_file=None)

    assert settings.cors_origins == ["http://localhost:5173", "http://127.0.0.1:5173"]
    assert settings.background_worker_tickers == ["AAPL", "MSFT"]


def test_settings_parse_comma_separated_env_values(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    monkeypatch.setenv("BACKGROUND_WORKER_TICKERS", "aapl,msft")

    settings = Settings(_env_file=None)

    assert settings.cors_origins == ["http://localhost:5173", "http://127.0.0.1:5173"]
    assert settings.background_worker_tickers == ["AAPL", "MSFT"]


def test_settings_reject_non_positive_background_worker_interval(monkeypatch) -> None:
    monkeypatch.setenv("BACKGROUND_WORKER_INTERVAL_SECONDS", "0")

    with pytest.raises(ValueError):
        Settings(_env_file=None)


def test_settings_resolve_top100_universes(monkeypatch) -> None:
    monkeypatch.setenv("TICKER_UNIVERSE", "sp500_top100")
    monkeypatch.setenv("BACKGROUND_WORKER_UNIVERSE", "sp500_top100")
    monkeypatch.setenv("FEATURED_TICKER_COUNT", "5")

    settings = Settings(_env_file=None)

    assert settings.searchable_ticker_universe[:5] == ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL"]
    assert settings.featured_tickers == ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL"]
    assert settings.resolved_background_worker_tickers[:5] == ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL"]
