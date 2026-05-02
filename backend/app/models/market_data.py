from datetime import datetime

from pydantic import BaseModel, Field


class MarketDataPoint(BaseModel):
    timestamp: datetime
    open: float = Field(ge=0)
    high: float = Field(ge=0)
    low: float = Field(ge=0)
    close: float = Field(ge=0)
    volume: int = Field(ge=0)


class MarketDataPayload(BaseModel):
    source: str
    currency: str | None = None
    exchange_timezone: str | None = None
    period: str
    interval: str
    points: list[MarketDataPoint]


class NormalizedMarketData(BaseModel):
    ticker: str
    timestamp: datetime
    data: MarketDataPayload

