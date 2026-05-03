from datetime import datetime

from pydantic import BaseModel

from app.models.market_data import MarketDataPoint
from app.models.recommendation import RecommendationLabel, RiskLabel
from app.models.recommendation import RecommendationResult
from app.models.signal import SignalResult


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


class RecommendationHistoryEntry(BaseModel):
    timestamp: datetime
    recommendation: RecommendationLabel
    confidence: float
    risk: RiskLabel
    reason: str


class RecommendationHistoryResponse(BaseModel):
    ticker: str
    timestamp: datetime
    data: list[RecommendationHistoryEntry]


class TickerCatalogData(BaseModel):
    configured_tickers: list[str]
    saved_market_tickers: list[str]
    saved_signal_tickers: list[str]
    saved_recommendation_tickers: list[str]
    available_tickers: list[str]


class TickerCatalogResponse(BaseModel):
    timestamp: datetime
    data: TickerCatalogData


class AnalysisRefreshData(BaseModel):
    price_snapshot: PriceSnapshotResponse
    signal: SignalResult
    recommendation: RecommendationResult
    storage_synced: bool
    persisted_market_data: bool | None = None
    persisted_signal: bool | None = None
    persisted_recommendation: bool | None = None


class AnalysisRefreshResponse(BaseModel):
    ticker: str
    timestamp: datetime
    data: AnalysisRefreshData


class ErrorResponse(BaseModel):
    detail: str
