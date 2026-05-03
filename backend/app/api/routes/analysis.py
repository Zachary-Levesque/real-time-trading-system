from datetime import UTC, datetime
import re

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_storage_read_service, get_update_pipeline_service
from app.ingestion.exceptions import IngestionError, MarketDataNotFoundError
from app.models.api import AnalysisRefreshData, AnalysisRefreshResponse, ErrorResponse
from app.processing.exceptions import InsufficientMarketDataError, MarketDataReadError
from app.recommendation.exceptions import SignalReadError
from app.runtime.worker import UpdatePipelineService
from app.storage.service import StorageBackedReadService


router = APIRouter()
TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")


def normalize_ticker(ticker: str) -> str:
    normalized_ticker = ticker.strip().upper()
    if not TICKER_PATTERN.fullmatch(normalized_ticker):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ticker symbols must be 1-10 characters and contain only letters, numbers, '.', or '-'.",
        )
    return normalized_ticker


@router.post(
    "/analysis/{ticker}/refresh",
    response_model=AnalysisRefreshResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
)
def refresh_analysis(
    ticker: str,
    pipeline_service: UpdatePipelineService = Depends(get_update_pipeline_service),
    read_service: StorageBackedReadService = Depends(get_storage_read_service),
) -> AnalysisRefreshResponse:
    normalized_ticker = normalize_ticker(ticker)

    try:
        pipeline_result = pipeline_service.run_once_for_ticker(normalized_ticker)
        price_snapshot = read_service.get_price_snapshot(normalized_ticker)
        signal_result = read_service.get_signal(normalized_ticker)
        recommendation = read_service.get_recommendation(normalized_ticker)
    except MarketDataNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InsufficientMarketDataError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except (IngestionError, MarketDataReadError, SignalReadError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return AnalysisRefreshResponse(
        ticker=normalized_ticker,
        timestamp=datetime.now(UTC),
        data=AnalysisRefreshData(
            price_snapshot=price_snapshot,
            signal=signal_result,
            recommendation=recommendation,
            storage_synced=pipeline_result.storage_synced,
            persisted_market_data=(
                pipeline_result.storage_result.persisted_market_data if pipeline_result.storage_result else None
            ),
            persisted_signal=(
                pipeline_result.storage_result.persisted_signal if pipeline_result.storage_result else None
            ),
            persisted_recommendation=(
                pipeline_result.storage_result.persisted_recommendation if pipeline_result.storage_result else None
            ),
        ),
    )
