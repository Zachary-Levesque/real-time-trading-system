from __future__ import annotations

from app.models.api import PriceSnapshotData, PriceSnapshotResponse
from app.processing.exceptions import MarketDataReadError
from app.processing.storage import LocalMarketDataReader


class PriceSnapshotService:
    def __init__(self, market_data_reader: LocalMarketDataReader) -> None:
        self.market_data_reader = market_data_reader

    def get_snapshot(self, ticker: str) -> PriceSnapshotResponse:
        market_data = self.market_data_reader.read(ticker)
        points = market_data.data.points

        if not points:
            raise MarketDataReadError(
                f"Normalized market data for ticker '{ticker.upper()}' does not contain any price points."
            )

        latest_point = points[-1]
        previous_point = points[-2] if len(points) > 1 else None

        change = None
        change_percent = None

        if previous_point is not None:
            change = round(latest_point.close - previous_point.close, 4)
            if previous_point.close != 0:
                change_percent = round((change / previous_point.close) * 100, 4)

        return PriceSnapshotResponse(
            ticker=market_data.ticker,
            timestamp=market_data.timestamp,
            data=PriceSnapshotData(
                source=market_data.data.source,
                currency=market_data.data.currency,
                interval=market_data.data.interval,
                current_price=latest_point.close,
                previous_close=previous_point.close if previous_point else None,
                change=change,
                change_percent=change_percent,
                points=points,
            ),
        )
