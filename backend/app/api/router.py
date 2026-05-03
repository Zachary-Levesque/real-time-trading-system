from fastapi import APIRouter

from app.api.routes.analysis import router as analysis_router
from app.api.routes.health import router as health_router
from app.api.routes.market import router as market_router
from app.api.routes.recommendation import router as recommendation_router
from app.api.routes.system import router as system_router
from app.api.routes.tickers import router as tickers_router


api_router = APIRouter()
api_router.include_router(analysis_router, tags=["analysis"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(market_router, tags=["market"])
api_router.include_router(recommendation_router, tags=["recommendation"])
api_router.include_router(system_router, tags=["system"])
api_router.include_router(tickers_router, tags=["tickers"])
