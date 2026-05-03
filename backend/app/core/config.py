import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.universe import SP500_TICKERS, SP500_TOP_100_TICKERS


class Settings(BaseSettings):
    ticker_universe: Literal["manual", "sp500_top100", "sp500_all"] = "sp500_all"
    featured_ticker_count: int = 12
    app_name: str = "Real-Time Trading System API"
    app_env: Literal["development", "test", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    market_data_dir: Path = Path("./data/market")
    signal_data_dir: Path = Path("./data/signals")
    recommendation_data_dir: Path = Path("./data/recommendations")
    default_market_period: str = "5d"
    default_market_interval: str = "1h"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/trading_system"
    redis_url: str = "redis://localhost:6379/0"
    storage_mode: Literal["file", "hybrid", "storage"] = "hybrid"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    enable_background_worker: bool = False
    background_worker_interval_seconds: int = 300
    background_worker_universe: Literal["manual", "sp500_top100", "sp500_all"] = "manual"
    background_worker_tickers: list[str] = ["AAPL", "MSFT", "NVDA", "SPY"]
    background_worker_run_immediately: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        enable_decoding=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                return [origin.strip() for origin in json.loads(value) if origin.strip()]
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("background_worker_tickers", mode="before")
    @classmethod
    def parse_background_worker_tickers(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                return [ticker.strip().upper() for ticker in json.loads(value) if ticker.strip()]
            return [ticker.strip().upper() for ticker in value.split(",") if ticker.strip()]
        return [ticker.upper() for ticker in value]

    @field_validator("background_worker_interval_seconds")
    @classmethod
    def validate_background_worker_interval_seconds(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("background_worker_interval_seconds must be greater than 0")
        return value

    @field_validator("featured_ticker_count")
    @classmethod
    def validate_featured_ticker_count(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("featured_ticker_count must be greater than 0")
        return value

    @property
    def searchable_ticker_universe(self) -> list[str]:
        if self.ticker_universe == "sp500_all":
            return SP500_TICKERS.copy()
        if self.ticker_universe == "sp500_top100":
            return SP500_TOP_100_TICKERS.copy()
        return self.background_worker_tickers.copy()

    @property
    def featured_tickers(self) -> list[str]:
        if self.ticker_universe == "sp500_all":
            return SP500_TOP_100_TICKERS[: self.featured_ticker_count]
        return self.searchable_ticker_universe[: self.featured_ticker_count]

    @property
    def resolved_background_worker_tickers(self) -> list[str]:
        if self.background_worker_universe == "sp500_all":
            return SP500_TICKERS.copy()
        if self.background_worker_universe == "sp500_top100":
            return SP500_TOP_100_TICKERS.copy()
        return self.background_worker_tickers.copy()


@lru_cache
def get_settings() -> Settings:
    return Settings()
