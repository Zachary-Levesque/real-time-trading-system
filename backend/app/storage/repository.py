from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.models.market_data import NormalizedMarketData
from app.models.recommendation import RecommendationResult
from app.models.signal import SignalResult
from app.storage.models import Base, MarketDataRecord, RecommendationRecord, SignalRecord


class PostgresStorageRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def create_schema(self) -> None:
        engine = self.session_factory.kw["bind"]
        Base.metadata.create_all(bind=engine)

    def upsert_market_data(self, market_data: NormalizedMarketData) -> None:
        payload = market_data.model_dump(mode="json")
        with self.session_factory() as session:
            record = session.get(MarketDataRecord, market_data.ticker)
            if record is None:
                record = MarketDataRecord(
                    ticker=market_data.ticker,
                    timestamp=market_data.timestamp,
                    payload=payload,
                )
                session.add(record)
            else:
                record.timestamp = market_data.timestamp
                record.payload = payload
            session.commit()

    def upsert_signal(self, signal_result: SignalResult) -> None:
        payload = signal_result.model_dump(mode="json")
        with self.session_factory() as session:
            record = session.get(SignalRecord, signal_result.ticker)
            if record is None:
                record = SignalRecord(
                    ticker=signal_result.ticker,
                    timestamp=signal_result.timestamp,
                    payload=payload,
                )
                session.add(record)
            else:
                record.timestamp = signal_result.timestamp
                record.payload = payload
            session.commit()

    def upsert_recommendation(self, recommendation: RecommendationResult) -> None:
        payload = recommendation.model_dump(mode="json")
        with self.session_factory() as session:
            record = session.get(RecommendationRecord, recommendation.ticker)
            if record is None:
                record = RecommendationRecord(
                    ticker=recommendation.ticker,
                    timestamp=recommendation.timestamp,
                    payload=payload,
                )
                session.add(record)
            else:
                record.timestamp = recommendation.timestamp
                record.payload = payload
            session.commit()

    def get_market_data(self, ticker: str) -> NormalizedMarketData | None:
        with self.session_factory() as session:
            record = session.get(MarketDataRecord, ticker.upper())
            return NormalizedMarketData.model_validate(record.payload) if record else None

    def get_signal(self, ticker: str) -> SignalResult | None:
        with self.session_factory() as session:
            record = session.get(SignalRecord, ticker.upper())
            return SignalResult.model_validate(record.payload) if record else None

    def get_recommendation(self, ticker: str) -> RecommendationResult | None:
        with self.session_factory() as session:
            record = session.get(RecommendationRecord, ticker.upper())
            return RecommendationResult.model_validate(record.payload) if record else None
