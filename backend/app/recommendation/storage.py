from __future__ import annotations

import json
from pathlib import Path

from app.models.recommendation import RecommendationResult
from app.models.signal import SignalResult
from app.recommendation.exceptions import RecommendationError, SignalReadError


class LocalSignalReader:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def read(self, ticker: str) -> SignalResult:
        input_path = self.base_dir / ticker.upper() / "latest.json"

        try:
            payload = json.loads(input_path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise SignalReadError(
                f"Failed to read processed signals for ticker '{ticker.upper()}'."
            ) from exc
        except json.JSONDecodeError as exc:
            raise SignalReadError(
                f"Processed signals for ticker '{ticker.upper()}' are not valid JSON."
            ) from exc

        return SignalResult.model_validate(payload)


class LocalRecommendationReader:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def read(self, ticker: str) -> RecommendationResult:
        input_path = self.base_dir / ticker.upper() / "latest.json"

        try:
            payload = json.loads(input_path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise SignalReadError(
                f"Failed to read recommendation for ticker '{ticker.upper()}'."
            ) from exc
        except json.JSONDecodeError as exc:
            raise SignalReadError(
                f"Recommendation for ticker '{ticker.upper()}' is not valid JSON."
            ) from exc

        return RecommendationResult.model_validate(payload)


class LocalRecommendationStorage:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def write(self, recommendation: RecommendationResult) -> Path:
        ticker_dir = self.base_dir / recommendation.ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)

        output_path = ticker_dir / "latest.json"

        try:
            output_path.write_text(
                json.dumps(recommendation.model_dump(mode="json"), indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            raise RecommendationError(
                f"Failed to write recommendation for ticker '{recommendation.ticker}'."
            ) from exc

        return output_path
