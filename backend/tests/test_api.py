from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import get_price_snapshot_service, get_recommendation_reader, get_signal_reader
from app.main import app
from app.models.market_data import MarketDataPayload, MarketDataPoint, NormalizedMarketData
from app.models.recommendation import RecommendationResult, RecommendationSignals
from app.models.signal import SignalData, SignalPayload, SignalResult
from app.processing.storage import LocalMarketDataReader
from app.recommendation.storage import LocalRecommendationReader, LocalSignalReader
from app.storage.local_queries import PriceSnapshotService


def build_market_data() -> NormalizedMarketData:
    return NormalizedMarketData(
        ticker="AAPL",
        timestamp=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
        data=MarketDataPayload(
            source="yfinance",
            currency="USD",
            exchange_timezone="America/New_York",
            period="5d",
            interval="1h",
            points=[
                MarketDataPoint(
                    timestamp=datetime(2026, 5, 1, 13, 30, tzinfo=UTC),
                    open=100.0,
                    high=101.0,
                    low=99.5,
                    close=100.5,
                    volume=1_000_000,
                ),
                MarketDataPoint(
                    timestamp=datetime(2026, 5, 1, 14, 30, tzinfo=UTC),
                    open=100.5,
                    high=102.0,
                    low=100.2,
                    close=101.7,
                    volume=1_250_000,
                ),
            ],
        ),
    )


def build_signal_result() -> SignalResult:
    return SignalResult(
        ticker="AAPL",
        timestamp=datetime(2026, 5, 2, 12, 30, tzinfo=UTC),
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


def build_recommendation_result() -> RecommendationResult:
    return RecommendationResult(
        ticker="AAPL",
        timestamp=datetime(2026, 5, 2, 13, 0, tzinfo=UTC),
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


def seed_local_data(tmp_path: Path) -> None:
    market_file = tmp_path / "market" / "AAPL" / "latest.json"
    signal_file = tmp_path / "signals" / "AAPL" / "latest.json"
    recommendation_file = tmp_path / "recommendations" / "AAPL" / "latest.json"

    market_file.parent.mkdir(parents=True, exist_ok=True)
    signal_file.parent.mkdir(parents=True, exist_ok=True)
    recommendation_file.parent.mkdir(parents=True, exist_ok=True)

    market_file.write_text(build_market_data().model_dump_json(indent=2), encoding="utf-8")
    signal_file.write_text(build_signal_result().model_dump_json(indent=2), encoding="utf-8")
    recommendation_file.write_text(build_recommendation_result().model_dump_json(indent=2), encoding="utf-8")


def test_api_price_signals_and_recommendation_endpoints(tmp_path: Path) -> None:
    seed_local_data(tmp_path)

    app.dependency_overrides[get_price_snapshot_service] = lambda: PriceSnapshotService(
        LocalMarketDataReader(tmp_path / "market")
    )
    app.dependency_overrides[get_signal_reader] = lambda: LocalSignalReader(tmp_path / "signals")
    app.dependency_overrides[get_recommendation_reader] = lambda: LocalRecommendationReader(
        tmp_path / "recommendations"
    )

    client = TestClient(app)

    price_response = client.get("/api/v1/price/AAPL")
    signal_response = client.get("/api/v1/signals/AAPL")
    recommendation_response = client.get("/api/v1/recommendation/AAPL")

    app.dependency_overrides.clear()

    assert price_response.status_code == 200
    assert signal_response.status_code == 200
    assert recommendation_response.status_code == 200

    price_payload = price_response.json()
    assert price_payload["ticker"] == "AAPL"
    assert price_payload["data"]["current_price"] == 101.7
    assert price_payload["data"]["change"] == 1.2

    signal_payload = signal_response.json()
    assert signal_payload["data"]["values"]["trend"] == "bullish"

    recommendation_payload = recommendation_response.json()
    assert recommendation_payload["recommendation"] == "BUY"
    assert recommendation_payload["risk"] == "low"


def test_api_returns_404_for_missing_ticker(tmp_path: Path) -> None:
    app.dependency_overrides[get_price_snapshot_service] = lambda: PriceSnapshotService(
        LocalMarketDataReader(tmp_path / "market")
    )
    app.dependency_overrides[get_signal_reader] = lambda: LocalSignalReader(tmp_path / "signals")
    app.dependency_overrides[get_recommendation_reader] = lambda: LocalRecommendationReader(
        tmp_path / "recommendations"
    )

    client = TestClient(app)

    responses = [
        client.get("/api/v1/price/MSFT"),
        client.get("/api/v1/signals/MSFT"),
        client.get("/api/v1/recommendation/MSFT"),
    ]

    app.dependency_overrides.clear()

    assert all(response.status_code == 404 for response in responses)
