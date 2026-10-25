from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_analysis_service
from app.api.health import router as health_router
from app.api.v1 import router as v1_router
from app.core.config import settings
from app.services.analysis_service import DataUnavailableError

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("windlens.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_refresh_on_startup:
        service = get_analysis_service()
        try:
            await service.ensure_loaded()
        except DataUnavailableError as exc:
            logger.warning("startup_ingestion_failed error=%s", exc)
    yield


app = FastAPI(title="WindLens API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(v1_router, prefix="/api/v1")
