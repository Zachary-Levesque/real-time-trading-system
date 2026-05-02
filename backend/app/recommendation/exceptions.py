class RecommendationError(Exception):
    """Base exception for recommendation failures."""


class SignalReadError(RecommendationError):
    """Raised when processed signals cannot be read from local storage."""

