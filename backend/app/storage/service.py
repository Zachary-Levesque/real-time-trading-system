from __future__ import annotations

from app.models.api import RecommendationHistoryEntry, RecommendationHistoryResponse, PriceSnapshotResponse
from app.models.recommendation import RecommendationResult
from app.models.signal import SignalResult
from app.processing.exceptions import MarketDataReadError
from app.processing.storage import LocalMarketDataReader
from app.recommendation.exceptions import SignalReadError
from app.recommendation.storage import LocalRecommendationReader, LocalSignalReader
from app.storage.cache import RedisCache
from app.storage.local_queries import PriceSnapshotService
from app.storage.repository import PostgresStorageRepository


class StorageBackedReadService:
    def __init__(
        self,
        *,
        repository: PostgresStorageRepository,
        cache: RedisCache | None,
        file_price_service: PriceSnapshotService,
        file_signal_reader: LocalSignalReader,
        file_recommendation_reader: LocalRecommendationReader,
        storage_mode: str,
    ) -> None:
        self.repository = repository
        self.cache = cache
        self.file_price_service = file_price_service
        self.file_signal_reader = file_signal_reader
        self.file_recommendation_reader = file_recommendation_reader
        self.storage_mode = storage_mode

    def get_price_snapshot(self, ticker: str) -> PriceSnapshotResponse:
        if self.storage_mode != "file":
            try:
                if self.cache is not None:
                    cached = self.cache.get_price_snapshot(ticker)
                    if cached is not None:
                        return cached

                market_data = self.repository.get_market_data(ticker)
                if market_data is not None:
                    snapshot = PriceSnapshotService.build_snapshot(market_data)
                    if self.cache is not None:
                        self.cache.set_price_snapshot(snapshot)
                    return snapshot
            except Exception:
                if self.storage_mode != "hybrid":
                    raise

        if self.storage_mode in {"file", "hybrid"}:
            return self.file_price_service.get_snapshot(ticker)

        raise MarketDataReadError(f"No stored market data available for ticker '{ticker.upper()}'.")

    def get_signal(self, ticker: str) -> SignalResult:
        if self.storage_mode != "file":
            try:
                signal_result = self.repository.get_signal(ticker)
                if signal_result is not None:
                    return signal_result
            except Exception:
                if self.storage_mode != "hybrid":
                    raise

        if self.storage_mode in {"file", "hybrid"}:
            return self.file_signal_reader.read(ticker)

        raise SignalReadError(f"No stored signals available for ticker '{ticker.upper()}'.")

    def get_recommendation(self, ticker: str) -> RecommendationResult:
        if self.storage_mode != "file":
            try:
                if self.cache is not None:
                    cached = self.cache.get_recommendation(ticker)
                    if cached is not None:
                        return cached

                recommendation = self.repository.get_recommendation(ticker)
                if recommendation is not None:
                    if self.cache is not None:
                        self.cache.set_recommendation(recommendation)
                    return recommendation
            except Exception:
                if self.storage_mode != "hybrid":
                    raise

        if self.storage_mode in {"file", "hybrid"}:
            return self.file_recommendation_reader.read(ticker)

        raise SignalReadError(f"No stored recommendation available for ticker '{ticker.upper()}'.")

    def get_recommendation_history(self, ticker: str, limit: int = 10) -> RecommendationHistoryResponse:
        if self.storage_mode != "file":
            try:
                history = self.repository.list_recommendation_history(ticker, limit)
                if history:
                    return RecommendationHistoryResponse(
                        ticker=ticker.upper(),
                        timestamp=history[0].timestamp,
                        data=history,
                    )
            except Exception:
                if self.storage_mode != "hybrid":
                    raise

        if self.storage_mode in {"file", "hybrid"}:
            history_results = self.file_recommendation_reader.list_history(ticker, limit)
            history = [
                RecommendationHistoryEntry(
                    timestamp=result.timestamp,
                    recommendation=result.recommendation,
                    confidence=result.confidence,
                    risk=result.risk,
                    reason=result.reason,
                )
                for result in history_results
            ]
            return RecommendationHistoryResponse(
                ticker=ticker.upper(),
                timestamp=history[0].timestamp,
                data=history,
            )

        raise SignalReadError(f"No stored recommendation history available for ticker '{ticker.upper()}'.")
