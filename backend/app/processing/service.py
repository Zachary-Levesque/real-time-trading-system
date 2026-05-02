from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.models.signal import SignalPayload, SignalResult
from app.processing.calculations import SignalCalculator
from app.processing.storage import LocalMarketDataReader, LocalSignalStorage


@dataclass
class SignalRunResult:
    signal_result: SignalResult
    output_path: Path


class SignalProcessingService:
    def __init__(
        self,
        *,
        market_data_reader: LocalMarketDataReader | None = None,
        signal_storage: LocalSignalStorage | None = None,
        signal_calculator: SignalCalculator | None = None,
    ) -> None:
        self.market_data_reader = market_data_reader or LocalMarketDataReader(Path("./data/market"))
        self.signal_storage = signal_storage or LocalSignalStorage(Path("./data/signals"))
        self.signal_calculator = signal_calculator or SignalCalculator()

    def process(self, ticker: str) -> SignalRunResult:
        market_data = self.market_data_reader.read(ticker)
        signals = self.signal_calculator.calculate(market_data)

        signal_result = SignalResult(
            ticker=market_data.ticker,
            timestamp=datetime.now(UTC),
            data=SignalPayload(
                source="signal_processor_v1",
                lookback_points=self.signal_calculator.lookback_points,
                data_points_used=len(market_data.data.points),
                values=signals,
            ),
        )
        output_path = self.signal_storage.write(signal_result)

        return SignalRunResult(signal_result=signal_result, output_path=output_path)

