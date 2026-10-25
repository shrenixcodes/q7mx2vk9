from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_analysis_service
from app.api.v1.params import AnalysisParams, parse_analysis_params
from app.api.v1.schemas import AccuracyResponse
from app.services.analysis_service import AnalysisService, DataUnavailableError

router = APIRouter(tags=["accuracy"])


@router.get("/accuracy", response_model=AccuracyResponse)
async def get_accuracy(
    params: AnalysisParams = Depends(parse_analysis_params),
    service: AnalysisService = Depends(get_analysis_service),
) -> AccuracyResponse:
    try:
        result = service.get_backtest(params.range_start, params.range_end, params.mode, params.as_of)
    except DataUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    warnings: list[str] = []
    if result.coverage.coverage_percent < 100:
        warnings.append(
            "Coverage is incomplete for the requested range; metrics are computed "
            "only over matched intervals, not the full expected range."
        )

    return AccuracyResponse(
        mode=result.mode,
        as_of=result.as_of,
        sample_count=result.accuracy.sample_count,
        unit=result.accuracy.unit,
        mae=result.accuracy.mae,
        rmse=result.accuracy.rmse,
        bias=result.accuracy.bias,
        mape_percent=result.accuracy.mape_percent,
        mape_excluded_low_actual_count=result.accuracy.mape_excluded_low_actual_count,
        coverage_percent=result.coverage.coverage_percent,
        warnings=warnings,
    )
