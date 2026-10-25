from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_analysis_service
from app.api.v1.params import AnalysisParams, parse_analysis_params
from app.api.v1.schemas import OverviewResponse
from app.services.analysis_service import AnalysisService, DataUnavailableError

router = APIRouter(tags=["overview"])


@router.get("/overview", response_model=OverviewResponse)
async def get_overview(
    params: AnalysisParams = Depends(parse_analysis_params),
    service: AnalysisService = Depends(get_analysis_service),
) -> OverviewResponse:
    try:
        result = service.get_backtest(params.range_start, params.range_end, params.mode, params.as_of)
    except DataUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    warnings: list[str] = []
    unmatched = result.coverage.expected_intervals - result.coverage.matched_intervals
    if unmatched > 0:
        warnings.append(
            f"{unmatched} of {result.coverage.expected_intervals} delivery intervals "
            "are not fully matched to both a forecast and an actual."
        )
    if service.last_error:
        warnings.append(f"Last source refresh failed: {service.last_error}")

    return OverviewResponse(
        mode=result.mode,
        as_of=result.as_of,
        delivery_range_start=result.delivery_range_start,
        delivery_range_end=result.delivery_range_end,
        expected_intervals=result.coverage.expected_intervals,
        matched_intervals=result.coverage.matched_intervals,
        coverage_percent=result.coverage.coverage_percent,
        unit=result.accuracy.unit,
        mae=result.accuracy.mae,
        rmse=result.accuracy.rmse,
        bias=result.accuracy.bias,
        total_wind_shortfall=result.exposure.total_wind_shortfall,
        total_wind_surplus=result.exposure.total_wind_surplus,
        source_loaded_at=service.loaded_at,
        warnings=warnings,
    )
