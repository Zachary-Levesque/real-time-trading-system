class SignalProcessingError(Exception):
    """Base exception for signal processing failures."""


class InsufficientMarketDataError(SignalProcessingError):
    """Raised when there are not enough market data points to compute signals."""


class MarketDataReadError(SignalProcessingError):
    """Raised when normalized market data cannot be read from local storage."""

