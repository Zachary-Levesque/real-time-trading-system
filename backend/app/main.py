from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.runtime.worker import BackgroundUpdateWorker, UpdatePipelineService


configure_logging()
settings = get_settings()
worker: BackgroundUpdateWorker | None = None
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global worker

    if settings.enable_background_worker:
        worker = BackgroundUpdateWorker(
            pipeline_service=UpdatePipelineService(),
            tickers=settings.background_worker_tickers,
            interval_seconds=settings.background_worker_interval_seconds,
            run_immediately=settings.background_worker_run_immediately,
        )
        await worker.start()

    try:
        yield
    finally:
        if worker is not None:
            await worker.stop()
            worker = None


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {
        "message": "Real-Time Trading System API",
        "docs": "/docs",
    }
