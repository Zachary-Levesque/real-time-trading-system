from __future__ import annotations

from statistics import mean

from app.models.market_data import MarketDataPoint, NormalizedMarketData
from app.models.signal import SignalData
from app.processing.exceptions import InsufficientMarketDataError


class SignalCalculator:
    def __init__(
        self,
        *,
        lookback_points: int = 20,
        short_window: int = 5,
        long_window: int = 12,
    ) -> None:
        self.lookback_points = lookback_points
        self.short_window = short_window
        self.long_window = long_window

    def calculate(self, market_data: NormalizedMarketData) -> SignalData:
        points = market_data.data.points
        required_points = max(self.lookback_points, self.long_window + 1)

        if len(points) < required_points:
            raise InsufficientMarketDataError(
                f"Expected at least {required_points} market data points for signal calculation, received {len(points)}."
            )

        window = points[-self.lookback_points :]

        return SignalData(
            momentum=self._classify_momentum(window),
            trend=self._classify_trend(window),
            volatility=self._classify_volatility(window),
            volume=self._classify_volume(window),
        )

    @staticmethod
    def _classify_momentum(points: list[MarketDataPoint]) -> str:
        start_close = points[0].close
        end_close = points[-1].close
        change_ratio = (end_close - start_close) / start_close

        if change_ratio >= 0.02:
            return "positive"
        if change_ratio <= -0.02:
            return "negative"
        return "neutral"

    def _classify_trend(self, points: list[MarketDataPoint]) -> str:
        closes = [point.close for point in points]
        short_average = mean(closes[-self.short_window :])
        long_average = mean(closes[-self.long_window :])
        difference_ratio = (short_average - long_average) / long_average

        if difference_ratio >= 0.01:
            return "bullish"
        if difference_ratio <= -0.01:
            return "bearish"
        return "neutral"

    @staticmethod
    def _classify_volatility(points: list[MarketDataPoint]) -> str:
        ratios = [(point.high - point.low) / point.close for point in points if point.close > 0]
        average_ratio = mean(ratios)

        if average_ratio <= 0.01:
            return "stable"
        if average_ratio <= 0.02:
            return "low"
        if average_ratio <= 0.035:
            return "medium"
        return "high"

    @staticmethod
    def _classify_volume(points: list[MarketDataPoint]) -> str:
        historical_volumes = [point.volume for point in points[:-1]]
        latest_volume = points[-1].volume
        baseline = mean(historical_volumes)
        ratio = latest_volume / baseline

        if ratio >= 1.5:
            return "above_average"
        if ratio >= 1.15:
            return "high"
        if ratio <= 0.75:
            return "low"
        return "average"

