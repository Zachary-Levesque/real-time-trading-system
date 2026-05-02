from __future__ import annotations

import json
from pathlib import Path

from app.ingestion.exceptions import MarketDataPersistenceError
from app.models.market_data import NormalizedMarketData


class LocalMarketDataStorage:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def write(self, market_data: NormalizedMarketData) -> Path:
        ticker_dir = self.base_dir / market_data.ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)

        output_path = ticker_dir / "latest.json"

        try:
            output_path.write_text(
                json.dumps(market_data.model_dump(mode="json"), indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            raise MarketDataPersistenceError(
                f"Failed to write normalized market data for ticker '{market_data.ticker}'."
            ) from exc

        return output_path
