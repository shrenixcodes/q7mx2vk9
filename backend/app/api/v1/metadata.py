from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_analysis_service
from app.api.v1.schemas import MetadataResponse
from app.core.config import settings
from app.services.analysis_service import AnalysisService

router = APIRouter(tags=["metadata"])


@router.get("/metadata", response_model=MetadataResponse)
async def get_metadata(
    service: AnalysisService = Depends(get_analysis_service),
) -> MetadataResponse:
    return MetadataResponse(
        datasets=["FUELHH", "WINDFOR"],
        analysis_range_start=settings.analysis_range_start,
        analysis_range_end=settings.analysis_range_end,
        generation_unit="MW",
        actual_interval_resolution_minutes=30,
        forecast_interval_resolution_minutes=60,
        timezone_note=(
            "Source timestamps are UTC (verified live against the Elexon API). "
            "Decision cutoffs are computed in Europe/London local time to "
            "reflect UK day-ahead process conventions."
        ),
        decision_cutoff_methodology=(
            "decision_time mode uses an assumed default cutoff of 11:00 "
            "Europe/London on the day before delivery. This is a stated "
            "assumption for this assignment, not a verified official market "
            "rule. as_of mode instead applies one caller-supplied cutoff to "
            "every interval in the range."
        ),
        source_loaded_at=service.loaded_at,
        source_load_error=service.last_error,
        limitations=[
            "WINDFOR forecast delivery intervals are hourly while FUELHH "
            "actual generation is half-hourly (verified live); both "
            "half-hours in a clock hour are compared against the same "
            "hourly forecast value.",
            "Procurement exposure figures describe wind generation "
            "deviation only -- not a verified additional electricity "
            "purchase volume or its financial cost.",
            "The local file cache is a performance optimization, not a "
            "durable store; all data is re-derivable from the Elexon API.",
        ],
    )
