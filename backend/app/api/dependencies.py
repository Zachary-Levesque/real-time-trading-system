from pathlib import Path

from app.core.config import get_settings
from app.processing.storage import LocalMarketDataReader
from app.recommendation.storage import LocalRecommendationReader, LocalSignalReader
from app.storage.cache import RedisCache
from app.storage.db import create_session_factory
from app.storage.local_queries import PriceSnapshotService
from app.storage.repository import PostgresStorageRepository
from app.storage.service import StorageBackedReadService


def get_price_snapshot_service() -> PriceSnapshotService:
    settings = get_settings()
    return PriceSnapshotService(
        market_data_reader=LocalMarketDataReader(Path(settings.market_data_dir)),
    )


def get_storage_read_service() -> StorageBackedReadService:
    settings = get_settings()
    cache = None if settings.storage_mode == "file" else RedisCache(settings.redis_url)

    return StorageBackedReadService(
        repository=PostgresStorageRepository(create_session_factory(settings.database_url)),
        cache=cache,
        file_price_service=PriceSnapshotService(
            market_data_reader=LocalMarketDataReader(Path(settings.market_data_dir)),
        ),
        file_signal_reader=LocalSignalReader(Path(settings.signal_data_dir)),
        file_recommendation_reader=LocalRecommendationReader(Path(settings.recommendation_data_dir)),
        storage_mode=settings.storage_mode,
    )
