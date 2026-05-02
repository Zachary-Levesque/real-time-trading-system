from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.models.recommendation import RecommendationResult, RecommendationSignals
from app.models.signal import SignalData, SignalResult


@dataclass(frozen=True)
class ScoreBreakdown:
    final_score: int
    confidence: float
    risk: str
    recommendation: str
    reason: str


class RecommendationEngine:
    def generate(self, signal_result: SignalResult) -> RecommendationResult:
        signal_values = signal_result.data.values
        breakdown = self._score(signal_values)

        return RecommendationResult(
            ticker=signal_result.ticker,
            timestamp=datetime.now(UTC),
            recommendation=breakdown.recommendation,
            confidence=breakdown.confidence,
            risk=breakdown.risk,
            signals=RecommendationSignals.model_validate(signal_values.model_dump()),
            reason=breakdown.reason,
        )

    def _score(self, signals: SignalData) -> ScoreBreakdown:
        signal_score = (
            self._momentum_score(signals.momentum)
            + self._trend_score(signals.trend)
            + self._volume_score(signals.volume)
            - self._volatility_penalty(signals.volatility)
        )
        final_score = max(0, min(100, 50 + signal_score))

        if final_score >= 70:
            recommendation = "BUY"
        elif final_score >= 40:
            recommendation = "HOLD"
        else:
            recommendation = "SELL"

        confidence = self._confidence_label(final_score, recommendation, signals.volatility)
        risk = self._risk_label(signals.volatility, signals.trend)
        reason = self._reason_text(signals, recommendation)

        return ScoreBreakdown(
            final_score=final_score,
            confidence=confidence,
            risk=risk,
            recommendation=recommendation,
            reason=reason,
        )

    @staticmethod
    def _confidence_label(final_score: int, recommendation: str, volatility: str) -> float:
        if recommendation in {"BUY", "SELL"}:
            return round(abs(final_score - 50) / 50, 2)

        hold_distance = abs(final_score - 50)
        base_confidence = 0.3 + max(0, 20 - hold_distance) / 40
        volatility_adjustment = {
            "stable": 0.05,
            "low": 0.03,
            "medium": -0.05,
            "high": -0.1,
        }[volatility]
        hold_confidence = max(0.35, min(0.85, base_confidence + volatility_adjustment))
        return round(hold_confidence, 2)

    @staticmethod
    def _momentum_score(momentum: str) -> int:
        return {"positive": 15, "neutral": 0, "negative": -15}[momentum]

    @staticmethod
    def _trend_score(trend: str) -> int:
        return {"bullish": 15, "neutral": 0, "bearish": -15}[trend]

    @staticmethod
    def _volume_score(volume: str) -> int:
        return {"above_average": 8, "high": 4, "average": 0, "low": -6}[volume]

    @staticmethod
    def _volatility_penalty(volatility: str) -> int:
        return {"stable": 0, "low": 4, "medium": 8, "high": 14}[volatility]

    @staticmethod
    def _risk_label(volatility: str, trend: str) -> str:
        if volatility == "high":
            return "high"
        if volatility in {"medium", "low"} and trend == "neutral":
            return "medium"
        if volatility == "stable":
            return "low"
        return "medium"

    @staticmethod
    def _reason_text(signals: SignalData, recommendation: str) -> str:
        momentum_text = {
            "positive": "positive momentum",
            "neutral": "neutral momentum",
            "negative": "negative momentum",
        }[signals.momentum]
        trend_text = {
            "bullish": "a bullish trend",
            "neutral": "a neutral trend",
            "bearish": "a bearish trend",
        }[signals.trend]
        volatility_text = {
            "stable": "stable volatility",
            "low": "low volatility",
            "medium": "moderate volatility",
            "high": "high volatility",
        }[signals.volatility]
        volume_text = {
            "above_average": "above-average volume",
            "high": "high volume",
            "average": "average volume",
            "low": "low volume",
        }[signals.volume]

        if recommendation == "BUY":
            return f"{momentum_text.capitalize()} with {trend_text}, {volatility_text}, and {volume_text} supports a buy bias."
        if recommendation == "SELL":
            return f"{momentum_text.capitalize()} with {trend_text}, {volatility_text}, and {volume_text} supports a sell bias."
        return f"{momentum_text.capitalize()} with {trend_text}, {volatility_text}, and {volume_text} suggests waiting for clearer confirmation."
