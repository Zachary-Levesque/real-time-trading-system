from functools import lru_cache
from pathlib import Path

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
    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/trading_system"
    redis_url: str = "redis://redis:6379/0"
    storage_mode: str = "hybrid"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
