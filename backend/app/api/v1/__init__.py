from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.v1.accuracy import router as accuracy_router
from app.api.v1.forecasts import router as forecasts_router
from app.api.v1.metadata import router as metadata_router
from app.api.v1.overview import router as overview_router
from app.api.v1.refresh import router as refresh_router

router = APIRouter()
router.include_router(health_router)
router.include_router(overview_router)
router.include_router(forecasts_router)
router.include_router(accuracy_router)
router.include_router(metadata_router)
router.include_router(refresh_router)
