from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_price_snapshot_service, get_signal_reader
from app.models.api import ErrorResponse, PriceSnapshotResponse
from app.models.signal import SignalResult
from app.processing.exceptions import MarketDataReadError
from app.recommendation.exceptions import SignalReadError
from app.recommendation.storage import LocalSignalReader
from app.storage.local_queries import PriceSnapshotService


router = APIRouter()


@router.get(
    "/price/{ticker}",
    response_model=PriceSnapshotResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_price(
    ticker: str,
    service: PriceSnapshotService = Depends(get_price_snapshot_service),
) -> PriceSnapshotResponse:
    try:
        return service.get_snapshot(ticker)
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
    signal_reader: LocalSignalReader = Depends(get_signal_reader),
) -> SignalResult:
    try:
        return signal_reader.read(ticker)
    except SignalReadError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

