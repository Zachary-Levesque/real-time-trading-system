from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings
from app.models.recommendation import RecommendationResult
from app.recommendation.engine import RecommendationEngine
from app.recommendation.storage import LocalRecommendationStorage, LocalSignalReader


@dataclass
class RecommendationRunResult:
    recommendation: RecommendationResult
    output_path: Path


class RecommendationService:
    def __init__(
        self,
        *,
        signal_reader: LocalSignalReader | None = None,
        recommendation_storage: LocalRecommendationStorage | None = None,
        engine: RecommendationEngine | None = None,
    ) -> None:
        settings = get_settings()
        self.signal_reader = signal_reader or LocalSignalReader(Path(settings.signal_data_dir))
        self.recommendation_storage = recommendation_storage or LocalRecommendationStorage(
            Path(settings.recommendation_data_dir)
        )
        self.engine = engine or RecommendationEngine()

    def generate(self, ticker: str) -> RecommendationRunResult:
        signal_result = self.signal_reader.read(ticker)
        recommendation = self.engine.generate(signal_result)
        output_path = self.recommendation_storage.write(recommendation)

        return RecommendationRunResult(recommendation=recommendation, output_path=output_path)
