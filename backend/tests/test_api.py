from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import get_storage_read_service, get_update_pipeline_service
from app.core.config import get_settings
from app.ingestion.exceptions import MarketDataNotFoundError
from app.main import app
from app.models.market_data import MarketDataPayload, MarketDataPoint, NormalizedMarketData
from app.models.recommendation import RecommendationResult, RecommendationSignals
from app.models.signal import SignalData, SignalPayload, SignalResult
from app.runtime.worker import UpdatePipelineResult
from app.processing.storage import LocalMarketDataReader
from app.recommendation.storage import LocalRecommendationReader, LocalSignalReader
from app.storage.local_queries import PriceSnapshotService
from app.storage.repository import PostgresStorageRepository
from app.storage.service import StorageBackedReadService


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

    app.dependency_overrides[get_storage_read_service] = lambda: StorageBackedReadService(
        repository=PostgresStorageRepository.__new__(PostgresStorageRepository),
        cache=None,
        file_price_service=PriceSnapshotService(LocalMarketDataReader(tmp_path / "market")),
        file_signal_reader=LocalSignalReader(tmp_path / "signals"),
        file_recommendation_reader=LocalRecommendationReader(tmp_path / "recommendations"),
        storage_mode="file",
    )

    client = TestClient(app)

    price_response = client.get("/api/v1/price/AAPL")
    signal_response = client.get("/api/v1/signals/AAPL")
    recommendation_response = client.get("/api/v1/recommendation/AAPL")
    recommendation_history_response = client.get("/api/v1/recommendation/AAPL/history")

    app.dependency_overrides.clear()

    assert price_response.status_code == 200
    assert signal_response.status_code == 200
    assert recommendation_response.status_code == 200
    assert recommendation_history_response.status_code == 200

    price_payload = price_response.json()
    assert price_payload["ticker"] == "AAPL"
    assert price_payload["data"]["current_price"] == 101.7
    assert price_payload["data"]["change"] == 1.2

    signal_payload = signal_response.json()
    assert signal_payload["data"]["values"]["trend"] == "bullish"

    recommendation_payload = recommendation_response.json()
    assert recommendation_payload["recommendation"] == "BUY"
    assert recommendation_payload["risk"] == "low"

    recommendation_history_payload = recommendation_history_response.json()
    assert recommendation_history_payload["ticker"] == "AAPL"
    assert recommendation_history_payload["data"][0]["recommendation"] == "BUY"


def test_api_returns_404_for_missing_ticker(tmp_path: Path) -> None:
    app.dependency_overrides[get_storage_read_service] = lambda: StorageBackedReadService(
        repository=PostgresStorageRepository.__new__(PostgresStorageRepository),
        cache=None,
        file_price_service=PriceSnapshotService(LocalMarketDataReader(tmp_path / "market")),
        file_signal_reader=LocalSignalReader(tmp_path / "signals"),
        file_recommendation_reader=LocalRecommendationReader(tmp_path / "recommendations"),
        storage_mode="file",
    )

    client = TestClient(app)

    responses = [
        client.get("/api/v1/price/MSFT"),
        client.get("/api/v1/signals/MSFT"),
        client.get("/api/v1/recommendation/MSFT"),
        client.get("/api/v1/recommendation/MSFT/history"),
    ]

    app.dependency_overrides.clear()

    assert all(response.status_code == 404 for response in responses)


def test_ticker_catalog_endpoint_lists_saved_and_configured_tickers(tmp_path: Path) -> None:
    seed_local_data(tmp_path)
    settings = get_settings()
    original_market_dir = settings.market_data_dir
    original_signal_dir = settings.signal_data_dir
    original_recommendation_dir = settings.recommendation_data_dir
    original_background_worker_tickers = settings.background_worker_tickers

    settings.market_data_dir = tmp_path / "market"
    settings.signal_data_dir = tmp_path / "signals"
    settings.recommendation_data_dir = tmp_path / "recommendations"
    settings.background_worker_tickers = ["AAPL", "MSFT", "NVDA"]

    client = TestClient(app)
    response = client.get("/api/v1/tickers")

    settings.market_data_dir = original_market_dir
    settings.signal_data_dir = original_signal_dir
    settings.recommendation_data_dir = original_recommendation_dir
    settings.background_worker_tickers = original_background_worker_tickers

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["universe_name"] == "sp500_all"
    assert payload["data"]["featured_tickers"][:3] == ["NVDA", "AAPL", "MSFT"]
    assert payload["data"]["searchable_tickers"][:3] == ["MMM", "AOS", "ABT"]
    assert payload["data"]["companies"][0] == {"ticker": "MMM", "name": "3M"}
    assert payload["data"]["configured_tickers"] == ["AAPL", "MSFT", "NVDA"]
    assert payload["data"]["saved_market_tickers"] == ["AAPL"]
    assert payload["data"]["saved_signal_tickers"] == ["AAPL"]
    assert payload["data"]["saved_recommendation_tickers"] == ["AAPL"]
    assert "AMD" in payload["data"]["available_tickers"]
    assert "NVDA" in payload["data"]["available_tickers"]


def test_analysis_refresh_endpoint_returns_latest_objects(tmp_path: Path) -> None:
    class StubPipelineService:
        def __init__(self) -> None:
            self.calls = []

        def run_once_for_ticker(self, ticker: str) -> UpdatePipelineResult:
            self.calls.append(ticker)
            return UpdatePipelineResult(
                ticker=ticker,
                storage_synced=True,
                storage_result=type(
                    "StorageResult",
                    (),
                    {
                        "persisted_market_data": True,
                        "persisted_signal": True,
                        "persisted_recommendation": True,
                    },
                )(),
            )

    seed_local_data(tmp_path)
    pipeline_service = StubPipelineService()
    app.dependency_overrides[get_update_pipeline_service] = lambda: pipeline_service
    app.dependency_overrides[get_storage_read_service] = lambda: StorageBackedReadService(
        repository=PostgresStorageRepository.__new__(PostgresStorageRepository),
        cache=None,
        file_price_service=PriceSnapshotService(LocalMarketDataReader(tmp_path / "market")),
        file_signal_reader=LocalSignalReader(tmp_path / "signals"),
        file_recommendation_reader=LocalRecommendationReader(tmp_path / "recommendations"),
        storage_mode="file",
    )

    client = TestClient(app)
    response = client.post("/api/v1/analysis/aapl/refresh")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "AAPL"
    assert payload["data"]["price_snapshot"]["data"]["current_price"] == 101.7
    assert payload["data"]["signal"]["data"]["values"]["trend"] == "bullish"
    assert payload["data"]["recommendation"]["recommendation"] == "BUY"
    assert payload["data"]["storage_synced"] is True
    assert pipeline_service.calls == ["AAPL"]


def test_analysis_refresh_endpoint_rejects_invalid_ticker() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/analysis/INVALID_SYMBOL_TOO_LONG/refresh")

    assert response.status_code == 422


def test_analysis_refresh_endpoint_returns_404_when_market_data_is_missing() -> None:
    class MissingTickerPipelineService:
        def run_once_for_ticker(self, ticker: str) -> UpdatePipelineResult:
            raise MarketDataNotFoundError(f"No market data returned for ticker '{ticker}'.")

    app.dependency_overrides[get_update_pipeline_service] = lambda: MissingTickerPipelineService()
    client = TestClient(app)

    response = client.post("/api/v1/analysis/INVALID/refresh")

    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_api_allows_cors_preflight() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/v1/price/AAPL",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_api_echoes_request_id_header() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health", headers={"x-request-id": "req-123"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-123"
