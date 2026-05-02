from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings
from app.ingestion.providers import MarketDataProvider, YFinanceMarketDataProvider
from app.ingestion.storage import LocalMarketDataStorage
from app.models.market_data import NormalizedMarketData


@dataclass
class IngestionRunResult:
    market_data: NormalizedMarketData
    output_path: Path


class MarketDataIngestionService:
    def __init__(
        self,
        provider: MarketDataProvider | None = None,
        storage: LocalMarketDataStorage | None = None,
    ) -> None:
        settings = get_settings()
        self.provider = provider or YFinanceMarketDataProvider()
        self.storage = storage or LocalMarketDataStorage(Path(settings.market_data_dir))

    def ingest(self, ticker: str, period: str, interval: str) -> IngestionRunResult:
        provider_result = self.provider.fetch(ticker=ticker, period=period, interval=interval)
        market_data = self.provider.normalize(provider_result)
        output_path = self.storage.write(market_data)

        return IngestionRunResult(
            market_data=market_data,
            output_path=output_path,
        )
