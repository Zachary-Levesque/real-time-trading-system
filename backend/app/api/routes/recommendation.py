from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_storage_read_service
from app.models.api import ErrorResponse
from app.models.recommendation import RecommendationResult
from app.recommendation.exceptions import SignalReadError
from app.storage.service import StorageBackedReadService


router = APIRouter()


@router.get(
    "/recommendation/{ticker}",
    response_model=RecommendationResult,
    responses={404: {"model": ErrorResponse}},
)
def get_recommendation(
    ticker: str,
    service: StorageBackedReadService = Depends(get_storage_read_service),
) -> RecommendationResult:
    try:
        return service.get_recommendation(ticker)
    except SignalReadError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
