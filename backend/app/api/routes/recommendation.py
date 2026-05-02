from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_recommendation_reader
from app.models.api import ErrorResponse
from app.models.recommendation import RecommendationResult
from app.recommendation.exceptions import SignalReadError
from app.recommendation.storage import LocalRecommendationReader


router = APIRouter()


@router.get(
    "/recommendation/{ticker}",
    response_model=RecommendationResult,
    responses={404: {"model": ErrorResponse}},
)
def get_recommendation(
    ticker: str,
    recommendation_reader: LocalRecommendationReader = Depends(get_recommendation_reader),
) -> RecommendationResult:
    try:
        return recommendation_reader.read(ticker)
    except SignalReadError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

