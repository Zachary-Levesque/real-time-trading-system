from __future__ import annotations

import json

from redis import Redis
from redis.exceptions import RedisError

from app.models.api import PriceSnapshotResponse
from app.models.recommendation import RecommendationResult
from app.storage.exceptions import StorageError


class RedisCache:
    def __init__(self, redis_url: str) -> None:
        self.client = Redis.from_url(redis_url, decode_responses=True)

    def get_price_snapshot(self, ticker: str) -> PriceSnapshotResponse | None:
        payload = self._read(f"price:{ticker.upper()}")
        return PriceSnapshotResponse.model_validate(payload) if payload else None

    def set_price_snapshot(self, snapshot: PriceSnapshotResponse) -> None:
        self._write(f"price:{snapshot.ticker.upper()}", snapshot.model_dump(mode="json"))

    def get_recommendation(self, ticker: str) -> RecommendationResult | None:
        payload = self._read(f"recommendation:{ticker.upper()}")
        return RecommendationResult.model_validate(payload) if payload else None

    def set_recommendation(self, recommendation: RecommendationResult) -> None:
        self._write(f"recommendation:{recommendation.ticker.upper()}", recommendation.model_dump(mode="json"))

    def _read(self, key: str) -> dict | None:
        try:
            payload = self.client.get(key)
        except RedisError as exc:
            raise StorageError("Failed to read from Redis cache.") from exc

        return json.loads(payload) if payload else None

    def _write(self, key: str, payload: dict) -> None:
        try:
            self.client.set(key, json.dumps(payload))
        except RedisError as exc:
            raise StorageError("Failed to write to Redis cache.") from exc
