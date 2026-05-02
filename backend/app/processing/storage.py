from __future__ import annotations

import json
from pathlib import Path

from app.models.market_data import NormalizedMarketData
from app.models.signal import SignalResult
from app.processing.exceptions import MarketDataReadError, SignalProcessingError


class LocalMarketDataReader:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def read(self, ticker: str) -> NormalizedMarketData:
        input_path = self.base_dir / ticker.upper() / "latest.json"

        try:
            payload = json.loads(input_path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise MarketDataReadError(
                f"Failed to read normalized market data for ticker '{ticker.upper()}'."
            ) from exc
        except json.JSONDecodeError as exc:
            raise MarketDataReadError(
                f"Normalized market data for ticker '{ticker.upper()}' is not valid JSON."
            ) from exc

        return NormalizedMarketData.model_validate(payload)


class LocalSignalStorage:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def write(self, signal_result: SignalResult) -> Path:
        ticker_dir = self.base_dir / signal_result.ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)

        output_path = ticker_dir / "latest.json"

        try:
            output_path.write_text(
                json.dumps(signal_result.model_dump(mode="json"), indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            raise SignalProcessingError(
                f"Failed to write processed signals for ticker '{signal_result.ticker}'."
            ) from exc

        return output_path

