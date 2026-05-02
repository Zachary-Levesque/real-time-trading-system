from datetime import datetime

from pydantic import BaseModel


class WorkerCycleStatus(BaseModel):
    enabled: bool
    interval_seconds: int | None = None
    tickers: list[str] = []
    last_started_at: datetime | None = None
    last_completed_at: datetime | None = None
    last_synced_tickers: list[str] = []
    last_unsynced_tickers: list[str] = []
    last_error: str | None = None


class SystemStatusResponse(BaseModel):
    service: str
    environment: str
    timestamp: datetime
    worker: WorkerCycleStatus

