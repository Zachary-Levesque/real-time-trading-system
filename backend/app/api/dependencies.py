from pathlib import Path

from app.core.config import get_settings
from app.processing.storage import LocalMarketDataReader
from app.recommendation.storage import LocalRecommendationReader, LocalSignalReader
from app.storage.local_queries import PriceSnapshotService


def get_price_snapshot_service() -> PriceSnapshotService:
    settings = get_settings()
    return PriceSnapshotService(
        market_data_reader=LocalMarketDataReader(Path(settings.market_data_dir)),
    )


def get_signal_reader() -> LocalSignalReader:
    return LocalSignalReader(Path("./data/signals"))


def get_recommendation_reader() -> LocalRecommendationReader:
    return LocalRecommendationReader(Path("./data/recommendations"))

