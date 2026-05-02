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

    def list_history(self, ticker: str, limit: int = 10) -> list[RecommendationResult]:
        ticker_dir = self.base_dir / ticker.upper()
        history_dir = ticker_dir / "history"
        history_results: list[RecommendationResult] = []

        if history_dir.exists():
            for path in sorted(history_dir.glob("*.json"), reverse=True):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                history_results.append(RecommendationResult.model_validate(payload))
                if len(history_results) >= limit:
                    return history_results

        latest_path = ticker_dir / "latest.json"
        if latest_path.exists():
            try:
                latest_payload = json.loads(latest_path.read_text(encoding="utf-8"))
                latest = RecommendationResult.model_validate(latest_payload)
            except (OSError, json.JSONDecodeError) as exc:
                raise SignalReadError(
                    f"Recommendation for ticker '{ticker.upper()}' is not valid JSON."
                ) from exc

            if not history_results or history_results[0].timestamp != latest.timestamp:
                history_results.insert(0, latest)

        if history_results:
            return history_results[:limit]

        raise SignalReadError(f"Failed to read recommendation for ticker '{ticker.upper()}'.")


class LocalRecommendationStorage:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def write(self, recommendation: RecommendationResult) -> Path:
        ticker_dir = self.base_dir / recommendation.ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)
        history_dir = ticker_dir / "history"
        history_dir.mkdir(parents=True, exist_ok=True)

        output_path = ticker_dir / "latest.json"
        history_path = history_dir / f"{recommendation.timestamp.strftime('%Y%m%dT%H%M%S%fZ')}.json"
        payload = json.dumps(recommendation.model_dump(mode="json"), indent=2)

        try:
            output_path.write_text(payload, encoding="utf-8")
            if not self._matches_latest_history(history_dir, recommendation):
                history_path.write_text(payload, encoding="utf-8")
        except OSError as exc:
            raise RecommendationError(
                f"Failed to write recommendation for ticker '{recommendation.ticker}'."
            ) from exc

        return output_path

    def _matches_latest_history(self, history_dir: Path, recommendation: RecommendationResult) -> bool:
        latest_history = next(iter(sorted(history_dir.glob("*.json"), reverse=True)), None)
        if latest_history is None:
            return False

        try:
            payload = json.loads(latest_history.read_text(encoding="utf-8"))
            latest_recommendation = RecommendationResult.model_validate(payload)
        except (OSError, json.JSONDecodeError, ValueError):
            return False

        return self._history_signature(latest_recommendation) == self._history_signature(recommendation)

    @staticmethod
    def _history_signature(recommendation: RecommendationResult) -> tuple:
        return (
            recommendation.recommendation,
            recommendation.confidence,
            recommendation.risk,
            recommendation.reason,
            recommendation.signals.momentum,
            recommendation.signals.trend,
            recommendation.signals.volatility,
            recommendation.signals.volume,
        )
