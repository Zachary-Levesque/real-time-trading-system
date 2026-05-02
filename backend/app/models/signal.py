from datetime import datetime
from typing import Literal

from pydantic import BaseModel

MomentumSignal = Literal["positive", "neutral", "negative"]
TrendSignal = Literal["bullish", "bearish", "neutral"]
VolatilitySignal = Literal["low", "medium", "high", "stable"]
VolumeSignal = Literal["low", "average", "high", "above_average"]


class SignalData(BaseModel):
    momentum: MomentumSignal
    trend: TrendSignal
    volatility: VolatilitySignal
    volume: VolumeSignal


class SignalPayload(BaseModel):
    source: str
    lookback_points: int
    data_points_used: int
    values: SignalData


class SignalResult(BaseModel):
    ticker: str
    timestamp: datetime
    data: SignalPayload

