from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter

from app.core.config import get_settings
from app.models.api import CompanyOption, TickerCatalogData, TickerCatalogResponse
from app.universe import SP500_COMPANIES, SP500_TICKERS


router = APIRouter()


def list_saved_tickers(base_dir: Path) -> list[str]:
    if not base_dir.exists():
        return []

    return sorted(
        {
            entry.name.upper()
            for entry in base_dir.iterdir()
            if entry.is_dir() and not entry.name.startswith(".")
        }
    )


@router.get("/tickers", response_model=TickerCatalogResponse)
def get_ticker_catalog() -> TickerCatalogResponse:
    settings = get_settings()

    configured_tickers = sorted({ticker.upper() for ticker in settings.resolved_background_worker_tickers})
    searchable_tickers = settings.searchable_ticker_universe
    featured_tickers = settings.featured_tickers
    company_name_by_ticker = {company["ticker"]: company["name"] for company in SP500_COMPANIES}
    companies = [
        CompanyOption(ticker=ticker, name=company_name_by_ticker[ticker])
        for ticker in SP500_TICKERS
        if ticker in set(searchable_tickers)
    ]
    saved_market_tickers = list_saved_tickers(Path(settings.market_data_dir))
    saved_signal_tickers = list_saved_tickers(Path(settings.signal_data_dir))
    saved_recommendation_tickers = list_saved_tickers(Path(settings.recommendation_data_dir))
    available_tickers = sorted(
        set(searchable_tickers)
        | set(configured_tickers)
        | set(saved_market_tickers)
        | set(saved_signal_tickers)
        | set(saved_recommendation_tickers)
    )

    return TickerCatalogResponse(
        timestamp=datetime.now(UTC),
        data=TickerCatalogData(
            universe_name=settings.ticker_universe,
            featured_tickers=featured_tickers,
            searchable_tickers=searchable_tickers,
            companies=companies,
            configured_tickers=configured_tickers,
            saved_market_tickers=saved_market_tickers,
            saved_signal_tickers=saved_signal_tickers,
            saved_recommendation_tickers=saved_recommendation_tickers,
            available_tickers=available_tickers,
        ),
    )
