from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.models.market_data import MarketDataPayload, MarketDataPoint, NormalizedMarketData
from app.processing.calculations import SignalCalculator
from app.processing.exceptions import InsufficientMarketDataError
from app.processing.service import SignalProcessingService
from app.processing.storage import LocalMarketDataReader, LocalSignalStorage


def build_market_data(*, closes: list[float], volume_tail: int = 1_000_000) -> NormalizedMarketData:
    start = datetime(2026, 5, 1, 13, 30, tzinfo=UTC)
    points: list[MarketDataPoint] = []

    for index, close in enumerate(closes):
        timestamp = start + timedelta(hours=index)
        spread = 0.4 if index < len(closes) - 1 else 0.3
        high = close * (1 + spread / 100)
        low = close * (1 - spread / 100)
        volume = volume_tail if index < len(closes) - 1 else int(volume_tail * 1.8)
        points.append(
            MarketDataPoint(
                timestamp=timestamp,
                open=close - 0.2,
                high=high,
                low=low,
                close=close,
                volume=volume,
            )
        )

    return NormalizedMarketData(
        ticker="AAPL",
        timestamp=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
        data=MarketDataPayload(
            source="test",
            currency="USD",
            exchange_timezone="America/New_York",
            period="5d",
            interval="1h",
            points=points,
        ),
    )


def test_signal_calculator_generates_expected_signal_labels() -> None:
    closes = [
        100.0,
        100.4,
        100.8,
        101.2,
        101.6,
        102.0,
        102.5,
        103.0,
        103.5,
        104.0,
        104.5,
        105.0,
        105.5,
        106.0,
        106.4,
        106.8,
        107.2,
        107.7,
        108.1,
        108.6,
    ]
    calculator = SignalCalculator()

    signals = calculator.calculate(build_market_data(closes=closes))

    assert signals.momentum == "positive"
    assert signals.trend == "bullish"
    assert signals.volatility == "stable"
    assert signals.volume == "above_average"


def test_signal_calculator_rejects_insufficient_points() -> None:
    calculator = SignalCalculator()
    market_data = build_market_data(closes=[100.0 + index for index in range(10)])

    with pytest.raises(InsufficientMarketDataError):
        calculator.calculate(market_data)


def test_signal_processing_service_writes_signal_output(tmp_path: Path) -> None:
    market_dir = tmp_path / "market"
    signal_dir = tmp_path / "signals"
    market_dir.mkdir(parents=True, exist_ok=True)

    market_data = build_market_data(
        closes=[
            100.0,
            100.4,
            100.8,
            101.2,
            101.6,
            102.0,
            102.5,
            103.0,
            103.5,
            104.0,
            104.5,
            105.0,
            105.5,
            106.0,
            106.4,
            106.8,
            107.2,
            107.7,
            108.1,
            108.6,
        ]
    )
    market_file = market_dir / "AAPL" / "latest.json"
    market_file.parent.mkdir(parents=True, exist_ok=True)
    market_file.write_text(market_data.model_dump_json(indent=2), encoding="utf-8")

    service = SignalProcessingService(
        market_data_reader=LocalMarketDataReader(market_dir),
        signal_storage=LocalSignalStorage(signal_dir),
    )

    run = service.process("AAPL")

    assert run.output_path == signal_dir / "AAPL" / "latest.json"
    assert run.output_path.exists()
    contents = run.output_path.read_text(encoding="utf-8")
    assert '"momentum": "positive"' in contents
    assert '"trend": "bullish"' in contents
