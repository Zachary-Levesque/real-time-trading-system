from datetime import UTC, datetime
from pathlib import Path

from app.models.api import PriceSnapshotResponse
from app.models.market_data import MarketDataPayload, MarketDataPoint, NormalizedMarketData
from app.models.recommendation import RecommendationResult, RecommendationSignals
from app.models.signal import SignalData, SignalPayload, SignalResult
from app.runtime.worker import UpdatePipelineService


class StubIngestionService:
    def __init__(self) -> None:
        self.calls = []

    def ingest(self, ticker: str, period: str, interval: str) -> None:
        self.calls.append((ticker, period, interval))


class StubProcessingService:
    def __init__(self) -> None:
        self.calls = []

    def process(self, ticker: str) -> SignalResult:
        self.calls.append(ticker)
        return SignalResult(
            ticker=ticker,
            timestamp=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
            data=SignalPayload(
                source="signal_processor_v1",
                lookback_points=20,
                data_points_used=35,
                values=SignalData(
                    momentum="positive",
                    trend="bullish",
                    volatility="stable",
                    volume="average",
                ),
            ),
        )


class StubRecommendationService:
    def __init__(self) -> None:
        self.calls = []

    def generate(self, ticker: str) -> RecommendationResult:
        self.calls.append(ticker)
        return RecommendationResult(
            ticker=ticker,
            timestamp=datetime(2026, 5, 2, 12, 1, tzinfo=UTC),
            recommendation="BUY",
            confidence=0.6,
            risk="low",
            signals=RecommendationSignals(
                momentum="positive",
                trend="bullish",
                volatility="stable",
                volume="average",
            ),
            reason="Positive momentum with a bullish trend, stable volatility, and average volume supports a buy bias.",
        )


class StubStorageSyncService:
    def __init__(self) -> None:
        self.calls = []

    def sync_ticker(self, ticker: str):
        self.calls.append(ticker)
        return type(
            "StorageResult",
            (),
            {
                "ticker": ticker,
                "persisted_market_data": True,
                "persisted_signal": True,
                "persisted_recommendation": True,
            },
        )()


def test_update_pipeline_runs_full_sequence() -> None:
    ingestion = StubIngestionService()
    processing = StubProcessingService()
    recommendation = StubRecommendationService()
    sync = StubStorageSyncService()
    service = UpdatePipelineService(
        ingestion_service=ingestion,
        processing_service=processing,
        recommendation_service=recommendation,
        storage_sync_service=sync,
    )

    result = service.run_once_for_ticker("AAPL")

    assert ingestion.calls == [("AAPL", "5d", "1h")]
    assert processing.calls == ["AAPL"]
    assert recommendation.calls == ["AAPL"]
    assert sync.calls == ["AAPL"]
    assert result.storage_synced is True
