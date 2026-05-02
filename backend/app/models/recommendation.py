from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.signal import MomentumSignal, TrendSignal, VolatilitySignal, VolumeSignal

RecommendationLabel = Literal["BUY", "SELL", "HOLD"]
RiskLabel = Literal["low", "medium", "high"]


class RecommendationSignals(BaseModel):
    momentum: MomentumSignal
    trend: TrendSignal
    volatility: VolatilitySignal
    volume: VolumeSignal


class RecommendationResult(BaseModel):
    ticker: str
    timestamp: datetime
    recommendation: RecommendationLabel
    confidence: float = Field(ge=0, le=1)
    risk: RiskLabel
    signals: RecommendationSignals
    reason: str

