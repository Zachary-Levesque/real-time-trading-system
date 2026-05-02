from datetime import UTC, datetime
from pathlib import Path

from app.models.signal import SignalData, SignalPayload, SignalResult
from app.recommendation.engine import RecommendationEngine
from app.recommendation.service import RecommendationService
from app.recommendation.storage import LocalRecommendationStorage, LocalSignalReader


def make_signal_result(
    *,
    momentum: str,
    trend: str,
    volatility: str,
    volume: str,
) -> SignalResult:
    return SignalResult(
        ticker="AAPL",
        timestamp=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
        data=SignalPayload(
            source="signal_processor_v1",
            lookback_points=20,
            data_points_used=35,
            values=SignalData(
                momentum=momentum,
                trend=trend,
                volatility=volatility,
                volume=volume,
            ),
        ),
    )


def test_recommendation_engine_generates_buy() -> None:
    engine = RecommendationEngine()

    recommendation = engine.generate(
        make_signal_result(
            momentum="positive",
            trend="bullish",
            volatility="stable",
            volume="above_average",
        )
    )

    assert recommendation.recommendation == "BUY"
    assert recommendation.risk == "low"
    assert recommendation.confidence == 0.76


def test_recommendation_engine_generates_sell() -> None:
    engine = RecommendationEngine()

    recommendation = engine.generate(
        make_signal_result(
            momentum="negative",
            trend="bearish",
            volatility="high",
            volume="low",
        )
    )

    assert recommendation.recommendation == "SELL"
    assert recommendation.risk == "high"
    assert recommendation.confidence == 1.0


def test_recommendation_service_writes_output(tmp_path: Path) -> None:
    signal_dir = tmp_path / "signals"
    recommendation_dir = tmp_path / "recommendations"
    signal_file = signal_dir / "AAPL" / "latest.json"
    signal_file.parent.mkdir(parents=True, exist_ok=True)
    signal_file.write_text(
        make_signal_result(
            momentum="positive",
            trend="bullish",
            volatility="stable",
            volume="average",
        ).model_dump_json(indent=2),
        encoding="utf-8",
    )

    service = RecommendationService(
        signal_reader=LocalSignalReader(signal_dir),
        recommendation_storage=LocalRecommendationStorage(recommendation_dir),
    )

    run = service.generate("AAPL")

    assert run.output_path == recommendation_dir / "AAPL" / "latest.json"
    assert run.output_path.exists()
    contents = run.output_path.read_text(encoding="utf-8")
    assert '"recommendation": "BUY"' in contents
    assert '"signals"' in contents
