from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkerState:
    enabled: bool
    interval_seconds: int | None = None
    tickers: list[str] = field(default_factory=list)
    last_started_at: datetime | None = None
    last_completed_at: datetime | None = None
    last_synced_tickers: list[str] = field(default_factory=list)
    last_unsynced_tickers: list[str] = field(default_factory=list)
    last_error: str | None = None


worker_state = WorkerState(enabled=False)
