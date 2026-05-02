from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

from app.ingestion.exceptions import MarketDataNotFoundError
from app.ingestion.providers import ProviderResult, YFinanceMarketDataProvider
from app.ingestion.service import MarketDataIngestionService
from app.ingestion.storage import LocalMarketDataStorage


class StubProvider:
    def __init__(self, result: ProviderResult) -> None:
        self.result = result

    def fetch(self, ticker: str, period: str, interval: str) -> ProviderResult:
        return self.result

    def normalize(self, result: ProviderResult):
        return YFinanceMarketDataProvider().normalize(result)


def make_history_frame() -> pd.DataFrame:
    index = pd.to_datetime(
        [
            "2026-05-01T14:30:00Z",
            "2026-05-01T15:30:00Z",
        ],
        utc=True,
    )

    return pd.DataFrame(
        {
            "Open": [210.25, 211.10],
            "High": [212.00, 212.45],
            "Low": [209.75, 210.80],
            "Close": [211.55, 212.12],
            "Volume": [3200100, 2875400],
        },
        index=index,
    )


def test_yfinance_provider_normalizes_history() -> None:
    provider = YFinanceMarketDataProvider()
    result = ProviderResult(
        ticker="AAPL",
        fetched_at=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
        currency="USD",
        exchange_timezone="America/New_York",
        period="5d",
        interval="1h",
        history=make_history_frame(),
    )

    normalized = provider.normalize(result)

    assert normalized.ticker == "AAPL"
    assert normalized.data.source == "yfinance"
    assert normalized.data.currency == "USD"
    assert normalized.data.period == "5d"
    assert len(normalized.data.points) == 2
    assert normalized.data.points[0].timestamp == datetime(2026, 5, 1, 14, 30, tzinfo=UTC)
    assert normalized.data.points[1].close == 212.12


def test_ingestion_service_writes_normalized_json(tmp_path: Path) -> None:
    result = ProviderResult(
        ticker="AAPL",
        fetched_at=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
        currency="USD",
        exchange_timezone="America/New_York",
        period="5d",
        interval="1h",
        history=make_history_frame(),
    )
    service = MarketDataIngestionService(
        provider=StubProvider(result),
        storage=LocalMarketDataStorage(tmp_path),
    )

    run = service.ingest(ticker="AAPL", period="5d", interval="1h")

    assert run.output_path == tmp_path / "AAPL" / "latest.json"
    assert run.output_path.exists()

    persisted = run.output_path.read_text(encoding="utf-8")
    assert '"ticker": "AAPL"' in persisted
    assert '"source": "yfinance"' in persisted


def test_yfinance_provider_raises_for_empty_history() -> None:
    provider = YFinanceMarketDataProvider()
    result = ProviderResult(
        ticker="AAPL",
        fetched_at=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
        currency="USD",
        exchange_timezone="America/New_York",
        period="5d",
        interval="1h",
        history=pd.DataFrame(),
    )

    with pytest.raises(MarketDataNotFoundError):
        provider.normalize(result)
