from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

import pandas as pd
import yfinance as yf

from app.ingestion.exceptions import IngestionError, MarketDataNotFoundError
from app.models.market_data import MarketDataPayload, MarketDataPoint, NormalizedMarketData


@dataclass
class ProviderResult:
    ticker: str
    fetched_at: datetime
    currency: str | None
    exchange_timezone: str | None
    period: str
    interval: str
    history: pd.DataFrame


class MarketDataProvider(Protocol):
    def fetch(self, ticker: str, period: str, interval: str) -> ProviderResult: ...
    def normalize(self, result: ProviderResult) -> NormalizedMarketData: ...


class YFinanceMarketDataProvider:
    source_name = "yfinance"

    def fetch(self, ticker: str, period: str, interval: str) -> ProviderResult:
        normalized_ticker = ticker.strip().upper()

        try:
            ticker_client = yf.Ticker(normalized_ticker)
            history = ticker_client.history(period=period, interval=interval, auto_adjust=False)
            info = ticker_client.fast_info or {}
        except Exception as exc:  # pragma: no cover - upstream library behavior
            raise IngestionError(f"Failed to fetch market data for {normalized_ticker}.") from exc

        if history.empty:
            raise MarketDataNotFoundError(
                f"No market data returned for ticker '{normalized_ticker}' with period '{period}' and interval '{interval}'."
            )

        return ProviderResult(
            ticker=normalized_ticker,
            fetched_at=datetime.now(UTC),
            currency=info.get("currency"),
            exchange_timezone=info.get("timezone"),
            period=period,
            interval=interval,
            history=history,
        )

    def normalize(self, result: ProviderResult) -> NormalizedMarketData:
        if result.history.empty:
            raise MarketDataNotFoundError(
                f"No market data returned for ticker '{result.ticker}' with period '{result.period}' and interval '{result.interval}'."
            )

        records = self._normalize_history(result.history)

        return NormalizedMarketData(
            ticker=result.ticker,
            timestamp=result.fetched_at,
            data=MarketDataPayload(
                source=self.source_name,
                currency=result.currency,
                exchange_timezone=result.exchange_timezone,
                period=result.period,
                interval=result.interval,
                points=records,
            ),
        )

    @staticmethod
    def _normalize_history(history: pd.DataFrame) -> list[MarketDataPoint]:
        normalized_points: list[MarketDataPoint] = []

        prepared = history.reset_index()
        timestamp_column = prepared.columns[0]

        for _, row in prepared.iterrows():
            timestamp = pd.Timestamp(row[timestamp_column]).to_pydatetime()

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=UTC)
            else:
                timestamp = timestamp.astimezone(UTC)

            normalized_points.append(
                MarketDataPoint(
                    timestamp=timestamp,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                )
            )

        return normalized_points
