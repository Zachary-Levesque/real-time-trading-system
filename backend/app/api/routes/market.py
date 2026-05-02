from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_storage_read_service
from app.models.api import ErrorResponse, PriceSnapshotResponse
from app.models.signal import SignalResult
from app.processing.exceptions import MarketDataReadError
from app.recommendation.exceptions import SignalReadError
from app.storage.service import StorageBackedReadService


router = APIRouter()


@router.get(
    "/price/{ticker}",
    response_model=PriceSnapshotResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_price(
    ticker: str,
    service: StorageBackedReadService = Depends(get_storage_read_service),
) -> PriceSnapshotResponse:
    try:
        return service.get_price_snapshot(ticker)
    except MarketDataReadError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/signals/{ticker}",
    response_model=SignalResult,
    responses={404: {"model": ErrorResponse}},
)
def get_signals(
    ticker: str,
    service: StorageBackedReadService = Depends(get_storage_read_service),
) -> SignalResult:
    try:
        return service.get_signal(ticker)
    except SignalReadError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
