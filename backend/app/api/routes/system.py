from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.models.runtime import SystemStatusResponse, WorkerCycleStatus
from app.runtime.state import worker_state


router = APIRouter()


@router.get("/system/status", response_model=SystemStatusResponse)
def get_system_status() -> SystemStatusResponse:
    settings = get_settings()

    return SystemStatusResponse(
        service=settings.app_name,
        environment=settings.app_env,
        timestamp=datetime.now(UTC),
        worker=WorkerCycleStatus(
            enabled=worker_state.enabled,
            interval_seconds=worker_state.interval_seconds,
            tickers=worker_state.tickers,
            last_started_at=worker_state.last_started_at,
            last_completed_at=worker_state.last_completed_at,
            last_synced_tickers=worker_state.last_synced_tickers,
            last_unsynced_tickers=worker_state.last_unsynced_tickers,
            last_error=worker_state.last_error,
        ),
    )
