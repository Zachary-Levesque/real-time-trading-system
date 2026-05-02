from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings
from app.ingestion.service import MarketDataIngestionService
from app.processing.service import SignalProcessingService
from app.processing.storage import LocalMarketDataReader, LocalSignalStorage
from app.recommendation.service import RecommendationService
from app.recommendation.storage import LocalRecommendationStorage, LocalSignalReader
from app.storage.cache import RedisCache
from app.storage.db import create_session_factory
from app.storage.repository import PostgresStorageRepository
from app.storage.sync import StorageSyncService, StorageSyncResult


logger = logging.getLogger(__name__)


@dataclass
class UpdatePipelineResult:
    ticker: str
    storage_synced: bool
    storage_result: StorageSyncResult | None = None


class UpdatePipelineService:
    def __init__(
        self,
        *,
        ingestion_service: MarketDataIngestionService | None = None,
        processing_service: SignalProcessingService | None = None,
        recommendation_service: RecommendationService | None = None,
        storage_sync_service: StorageSyncService | None = None,
    ) -> None:
        settings = get_settings()
        self.settings = settings
        self.ingestion_service = ingestion_service or MarketDataIngestionService()
        self.processing_service = processing_service or SignalProcessingService(
            market_data_reader=LocalMarketDataReader(Path(settings.market_data_dir)),
            signal_storage=LocalSignalStorage(Path(settings.signal_data_dir)),
        )
        self.recommendation_service = recommendation_service or RecommendationService(
            signal_reader=LocalSignalReader(Path(settings.signal_data_dir)),
            recommendation_storage=LocalRecommendationStorage(Path(settings.recommendation_data_dir)),
        )
        self.storage_sync_service = storage_sync_service or StorageSyncService(
            repository=PostgresStorageRepository(create_session_factory(settings.database_url)),
            cache=None if settings.storage_mode == "file" else RedisCache(settings.redis_url),
            market_data_reader=LocalMarketDataReader(Path(settings.market_data_dir)),
            signal_reader=LocalSignalReader(Path(settings.signal_data_dir)),
            recommendation_reader=LocalRecommendationReader(Path(settings.recommendation_data_dir)),
        )

    def run_once_for_ticker(self, ticker: str) -> UpdatePipelineResult:
        normalized_ticker = ticker.upper()

        self.ingestion_service.ingest(
            ticker=normalized_ticker,
            period=self.settings.default_market_period,
            interval=self.settings.default_market_interval,
        )
        self.processing_service.process(normalized_ticker)
        self.recommendation_service.generate(normalized_ticker)

        try:
            storage_result = self.storage_sync_service.sync_ticker(normalized_ticker)
            return UpdatePipelineResult(
                ticker=normalized_ticker,
                storage_synced=True,
                storage_result=storage_result,
            )
        except Exception as exc:  # pragma: no cover - external service availability
            logger.warning("Storage sync failed for %s: %s", normalized_ticker, exc)
            return UpdatePipelineResult(
                ticker=normalized_ticker,
                storage_synced=False,
            )

    def run_once(self, tickers: list[str]) -> list[UpdatePipelineResult]:
        return [self.run_once_for_ticker(ticker) for ticker in tickers]


class BackgroundUpdateWorker:
    def __init__(
        self,
        *,
        pipeline_service: UpdatePipelineService,
        tickers: list[str],
        interval_seconds: int,
        run_immediately: bool,
    ) -> None:
        self.pipeline_service = pipeline_service
        self.tickers = tickers
        self.interval_seconds = interval_seconds
        self.run_immediately = run_immediately
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is not None:
            await self._task
            self._task = None

    async def _run_loop(self) -> None:
        if self.run_immediately:
            await self._execute_cycle()

        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.interval_seconds)
            except asyncio.TimeoutError:
                await self._execute_cycle()

    async def _execute_cycle(self) -> None:
        logger.info("Background update cycle started for tickers: %s", ", ".join(self.tickers))
        try:
            results = await asyncio.to_thread(self.pipeline_service.run_once, self.tickers)
            synced = [result.ticker for result in results if result.storage_synced]
            unsynced = [result.ticker for result in results if not result.storage_synced]
            logger.info("Background update cycle completed. storage_synced=%s storage_unsynced=%s", synced, unsynced)
        except Exception as exc:  # pragma: no cover - defensive loop protection
            logger.exception("Background update cycle failed: %s", exc)
