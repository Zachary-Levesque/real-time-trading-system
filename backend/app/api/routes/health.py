from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.models.health import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()

    return HealthResponse(
        service=settings.app_name,
        status="ok",
        environment=settings.app_env,
        timestamp=datetime.now(UTC),
    )

