from __future__ import annotations

import httpx
import pytest
import pytest_asyncio

from app.api.deps import get_analysis_service
from app.ingestion.normalize import normalize_actual_generation, normalize_forecast_generation
from app.main import app
from app.services.analysis_service import AnalysisService


@pytest.fixture
def seeded_service(fuelhh_wind_sample, windfor_two_vintages_sample):
    actuals, _ = normalize_actual_generation(fuelhh_wind_sample)
    forecasts, _ = normalize_forecast_generation(windfor_two_vintages_sample)

    service = AnalysisService()
    service.load_for_testing(actuals=actuals, forecasts=forecasts)
    app.dependency_overrides[get_analysis_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_analysis_service, None)


@pytest.fixture
def unloaded_service():
    service = AnalysisService()
    app.dependency_overrides[get_analysis_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_analysis_service, None)


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
