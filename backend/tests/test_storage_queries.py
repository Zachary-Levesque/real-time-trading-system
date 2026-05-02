from datetime import UTC, datetime

import pytest

from app.models.market_data import MarketDataPayload, NormalizedMarketData
from app.processing.exceptions import MarketDataReadError
from app.storage.local_queries import PriceSnapshotService


class EmptyMarketDataReader:
    def read(self, ticker: str) -> NormalizedMarketData:
        return NormalizedMarketData(
            ticker=ticker.upper(),
            timestamp=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
            data=MarketDataPayload(
                source="test",
                currency="USD",
                exchange_timezone="America/New_York",
                period="5d",
                interval="1h",
                points=[],
            ),
        )


def test_price_snapshot_service_rejects_empty_points() -> None:
    service = PriceSnapshotService(market_data_reader=EmptyMarketDataReader())

    with pytest.raises(MarketDataReadError):
        service.get_snapshot("AAPL")
