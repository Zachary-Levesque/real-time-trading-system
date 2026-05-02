class IngestionError(Exception):
    """Base exception for market data ingestion failures."""


class MarketDataNotFoundError(IngestionError):
    """Raised when a ticker returns no usable market data."""


class MarketDataPersistenceError(IngestionError):
    """Raised when normalized market data cannot be written locally."""

