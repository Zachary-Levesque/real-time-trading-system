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
