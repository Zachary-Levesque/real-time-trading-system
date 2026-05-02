from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Real-Time Trading System API"
    app_env: str = "development"
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
    storage_mode: str = "hybrid"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    enable_background_worker: bool = False
    background_worker_interval_seconds: int = 300
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
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("background_worker_tickers", mode="before")
    @classmethod
    def parse_background_worker_tickers(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [ticker.strip().upper() for ticker in value.split(",") if ticker.strip()]
        return [ticker.upper() for ticker in value]


@lru_cache
def get_settings() -> Settings:
    return Settings()
