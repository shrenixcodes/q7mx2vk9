from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_analysis_service
from app.api.v1.params import AnalysisParams, parse_analysis_params
from app.api.v1.schemas import ForecastIntervalResponse, ForecastsResponse
from app.services.analysis_service import AnalysisService, DataUnavailableError

router = APIRouter(tags=["forecasts"])


@router.get("/forecasts", response_model=ForecastsResponse)
async def get_forecasts(
    params: AnalysisParams = Depends(parse_analysis_params),
    limit: int = Query(500, ge=1, le=2000),
    offset: int = Query(0, ge=0),
    service: AnalysisService = Depends(get_analysis_service),
) -> ForecastsResponse:
    try:
        result = service.get_backtest(params.range_start, params.range_end, params.mode, params.as_of)
    except DataUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    page = result.intervals[offset : offset + limit]
    records = [
        ForecastIntervalResponse(
            delivery_start=interval.delivery_start,
            forecast_generation_mw=interval.forecast_generation_mw,
            actual_generation_mw=interval.actual_generation_mw,
            forecast_publish_time=interval.forecast_publish_time,
            error_mw=interval.error_mw,
            wind_shortfall_mw=interval.wind_shortfall_mw,
            wind_surplus_mw=interval.wind_surplus_mw,
            status=interval.status,
        )
        for interval in page
    ]
    return ForecastsResponse(
        mode=result.mode,
        as_of=result.as_of,
        total_count=len(result.intervals),
        limit=limit,
        offset=offset,
        records=records,
    )
