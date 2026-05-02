from __future__ import annotations

from dataclasses import dataclass

from app.models.api import PriceSnapshotResponse
from app.models.market_data import NormalizedMarketData
from app.models.recommendation import RecommendationResult
from app.models.signal import SignalResult
from app.processing.storage import LocalMarketDataReader
from app.recommendation.storage import LocalRecommendationReader, LocalSignalReader
from app.storage.cache import RedisCache
from app.storage.local_queries import PriceSnapshotService
from app.storage.repository import PostgresStorageRepository


@dataclass
class StorageSyncResult:
    ticker: str
    persisted_market_data: bool
    persisted_signal: bool
    persisted_recommendation: bool


class StorageSyncService:
    def __init__(
        self,
        *,
        repository: PostgresStorageRepository,
        cache: RedisCache | None,
        market_data_reader: LocalMarketDataReader,
        signal_reader: LocalSignalReader,
        recommendation_reader: LocalRecommendationReader,
    ) -> None:
        self.repository = repository
        self.cache = cache
        self.market_data_reader = market_data_reader
        self.signal_reader = signal_reader
        self.recommendation_reader = recommendation_reader

    def sync_ticker(self, ticker: str) -> StorageSyncResult:
        self.repository.create_schema()

        market_data = self.market_data_reader.read(ticker)
        signal_result = self.signal_reader.read(ticker)
        recommendation = self.recommendation_reader.read(ticker)

        self.repository.upsert_market_data(market_data)
        self.repository.upsert_signal(signal_result)
        self.repository.upsert_recommendation(recommendation)
        latest_history = self.repository.get_latest_recommendation_history(ticker)
        if not self._matches_history_signature(latest_history, recommendation):
            self.repository.append_recommendation_history(recommendation)

        if self.cache is not None:
            self.cache.set_price_snapshot(PriceSnapshotService.build_snapshot(market_data))
            self.cache.set_recommendation(recommendation)

        return StorageSyncResult(
            ticker=ticker.upper(),
            persisted_market_data=True,
            persisted_signal=True,
            persisted_recommendation=True,
        )

    @staticmethod
    def _matches_history_signature(
        existing: RecommendationResult | None,
        recommendation: RecommendationResult,
    ) -> bool:
        if existing is None:
            return False

        return (
            existing.recommendation == recommendation.recommendation
            and existing.confidence == recommendation.confidence
            and existing.risk == recommendation.risk
            and existing.reason == recommendation.reason
            and existing.signals == recommendation.signals
        )
