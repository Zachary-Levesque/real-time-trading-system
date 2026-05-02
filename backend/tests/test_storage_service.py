from datetime import UTC, datetime

from app.models.api import PriceSnapshotData, PriceSnapshotResponse
from app.models.market_data import MarketDataPayload, MarketDataPoint, NormalizedMarketData
from app.models.recommendation import RecommendationResult, RecommendationSignals
from app.models.signal import SignalData, SignalPayload, SignalResult
from app.storage.local_queries import PriceSnapshotService
from app.storage.service import StorageBackedReadService


class FakeRepository:
    def __init__(self, *, market_data=None, signal=None, recommendation=None, should_fail=False) -> None:
        self.market_data = market_data
        self.signal = signal
        self.recommendation = recommendation
        self.should_fail = should_fail

    def get_market_data(self, ticker: str):
        if self.should_fail:
            raise RuntimeError("db unavailable")
        return self.market_data

    def get_signal(self, ticker: str):
        if self.should_fail:
            raise RuntimeError("db unavailable")
        return self.signal

    def get_recommendation(self, ticker: str):
        if self.should_fail:
            raise RuntimeError("db unavailable")
        return self.recommendation

    def list_recommendation_history(self, ticker: str, limit: int = 10):
        if self.should_fail:
            raise RuntimeError("db unavailable")
        return []


class FakeCache:
    def __init__(self, *, price=None, recommendation=None) -> None:
        self.price = price
        self.recommendation = recommendation

    def get_price_snapshot(self, ticker: str):
        return self.price

    def set_price_snapshot(self, snapshot):
        self.price = snapshot

    def get_recommendation(self, ticker: str):
        return self.recommendation

    def set_recommendation(self, recommendation):
        self.recommendation = recommendation


class FakeFilePriceService:
    def __init__(self, snapshot: PriceSnapshotResponse) -> None:
        self.snapshot = snapshot

    def get_snapshot(self, ticker: str) -> PriceSnapshotResponse:
        return self.snapshot


class FakeFileSignalReader:
    def __init__(self, signal_result: SignalResult) -> None:
        self.signal_result = signal_result

    def read(self, ticker: str) -> SignalResult:
        return self.signal_result


class FakeFileRecommendationReader:
    def __init__(self, recommendation: RecommendationResult) -> None:
        self.recommendation = recommendation

    def read(self, ticker: str) -> RecommendationResult:
        return self.recommendation

    def list_history(self, ticker: str, limit: int = 10):
        return [self.recommendation]


def build_market_data() -> NormalizedMarketData:
    return NormalizedMarketData(
        ticker="AAPL",
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
                    volume=1_000_000,
                ),
                MarketDataPoint(
                    timestamp=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
                    open=100.0,
                    high=102.0,
                    low=99.8,
                    close=101.5,
                    volume=1_200_000,
                ),
            ],
        ),
    )


def build_signal_result() -> SignalResult:
    return SignalResult(
        ticker="AAPL",
        timestamp=datetime(2026, 5, 2, 12, 15, tzinfo=UTC),
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


def build_recommendation() -> RecommendationResult:
    return RecommendationResult(
        ticker="AAPL",
        timestamp=datetime(2026, 5, 2, 12, 30, tzinfo=UTC),
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


def test_storage_service_prefers_cache_for_price_snapshot() -> None:
    snapshot = PriceSnapshotService.build_snapshot(build_market_data())
    service = StorageBackedReadService(
        repository=FakeRepository(),
        cache=FakeCache(price=snapshot),
        file_price_service=FakeFilePriceService(snapshot),
        file_signal_reader=FakeFileSignalReader(build_signal_result()),
        file_recommendation_reader=FakeFileRecommendationReader(build_recommendation()),
        storage_mode="hybrid",
    )

    result = service.get_price_snapshot("AAPL")

    assert result.data.current_price == snapshot.data.current_price


def test_storage_service_falls_back_to_files_when_storage_fails() -> None:
    market_data = build_market_data()
    snapshot = PriceSnapshotService.build_snapshot(market_data)
    recommendation = build_recommendation()
    signal_result = build_signal_result()

    service = StorageBackedReadService(
        repository=FakeRepository(should_fail=True),
        cache=None,
        file_price_service=FakeFilePriceService(snapshot),
        file_signal_reader=FakeFileSignalReader(signal_result),
        file_recommendation_reader=FakeFileRecommendationReader(recommendation),
        storage_mode="hybrid",
    )

    assert service.get_price_snapshot("AAPL").ticker == "AAPL"
    assert service.get_signal("AAPL").data.values.trend == "bullish"
    assert service.get_recommendation("AAPL").recommendation == "BUY"
    assert service.get_recommendation_history("AAPL").data[0].recommendation == "BUY"
