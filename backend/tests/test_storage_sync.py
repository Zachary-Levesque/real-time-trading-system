from datetime import UTC, datetime

from app.models.market_data import MarketDataPayload, MarketDataPoint, NormalizedMarketData
from app.models.recommendation import RecommendationResult, RecommendationSignals
from app.models.signal import SignalData, SignalPayload, SignalResult
from app.storage.sync import StorageSyncService


class FakeRepository:
    def __init__(self, latest_history: RecommendationResult | None = None) -> None:
        self.latest_history = latest_history
        self.append_calls = 0

    def create_schema(self) -> None:
        return None

    def upsert_market_data(self, market_data: NormalizedMarketData) -> None:
        return None

    def upsert_signal(self, signal_result: SignalResult) -> None:
        return None

    def upsert_recommendation(self, recommendation: RecommendationResult) -> None:
        return None

    def append_recommendation_history(self, recommendation: RecommendationResult) -> None:
        self.append_calls += 1

    def get_latest_recommendation_history(self, ticker: str) -> RecommendationResult | None:
        return self.latest_history


class StubMarketDataReader:
    def read(self, ticker: str) -> NormalizedMarketData:
        return NormalizedMarketData(
            ticker=ticker,
            timestamp=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
            data=MarketDataPayload(
                source="test",
                currency="USD",
                exchange_timezone="America/New_York",
                period="5d",
                interval="1h",
                points=[
                    MarketDataPoint(
                        timestamp=datetime(2026, 5, 2, 11, 0, tzinfo=UTC),
                        open=100.0,
                        high=101.0,
                        low=99.0,
                        close=100.0,
                        volume=1000,
                    )
                ],
            ),
        )


class StubSignalReader:
    def read(self, ticker: str) -> SignalResult:
        return SignalResult(
            ticker=ticker,
            timestamp=datetime(2026, 5, 2, 12, 5, tzinfo=UTC),
            data=SignalPayload(
                source="signal_processor_v1",
                lookback_points=20,
                data_points_used=35,
                values=SignalData(
                    momentum="neutral",
                    trend="neutral",
                    volatility="stable",
                    volume="average",
                ),
            ),
        )


class StubRecommendationReader:
    def __init__(self, recommendation: RecommendationResult) -> None:
        self.recommendation = recommendation

    def read(self, ticker: str) -> RecommendationResult:
        return self.recommendation


def build_recommendation() -> RecommendationResult:
    return RecommendationResult(
        ticker="AAPL",
        timestamp=datetime(2026, 5, 2, 12, 10, tzinfo=UTC),
        recommendation="HOLD",
        confidence=0.85,
        risk="low",
        signals=RecommendationSignals(
            momentum="neutral",
            trend="neutral",
            volatility="stable",
            volume="average",
        ),
        reason="Neutral momentum with a neutral trend, stable volatility, and average volume suggests waiting for clearer confirmation.",
    )


def test_storage_sync_skips_duplicate_history_entries() -> None:
    recommendation = build_recommendation()
    repository = FakeRepository(latest_history=recommendation)
    service = StorageSyncService(
        repository=repository,
        cache=None,
        market_data_reader=StubMarketDataReader(),
        signal_reader=StubSignalReader(),
        recommendation_reader=StubRecommendationReader(recommendation),
    )

    service.sync_ticker("AAPL")

    assert repository.append_calls == 0


def test_storage_sync_appends_new_history_entries() -> None:
    recommendation = build_recommendation()
    repository = FakeRepository(latest_history=None)
    service = StorageSyncService(
        repository=repository,
        cache=None,
        market_data_reader=StubMarketDataReader(),
        signal_reader=StubSignalReader(),
        recommendation_reader=StubRecommendationReader(recommendation),
    )

    service.sync_ticker("AAPL")

    assert repository.append_calls == 1
