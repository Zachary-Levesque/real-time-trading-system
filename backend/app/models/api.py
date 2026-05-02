from datetime import datetime

from pydantic import BaseModel

from app.models.market_data import MarketDataPoint


class PriceSnapshotData(BaseModel):
    source: str
    currency: str | None = None
    interval: str
    current_price: float
    previous_close: float | None = None
    change: float | None = None
    change_percent: float | None = None
    points: list[MarketDataPoint]


class PriceSnapshotResponse(BaseModel):
    ticker: str
    timestamp: datetime
    data: PriceSnapshotData


class ErrorResponse(BaseModel):
    detail: str

