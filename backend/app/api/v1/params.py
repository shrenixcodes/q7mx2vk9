from __future__ import annotations

from datetime import date, datetime, timezone
from typing import NamedTuple

from fastapi import HTTPException, Query

from app.analytics.models import AnalysisMode

MAX_RANGE_DAYS = 62


class AnalysisParams(NamedTuple):
    range_start: datetime
    range_end: datetime
    mode: AnalysisMode
    as_of: datetime | None


def parse_analysis_params(
    start_date: date = Query(..., description="Delivery range start, UTC date, inclusive"),
    end_date: date = Query(..., description="Delivery range end, UTC date, exclusive"),
    mode: AnalysisMode = Query(AnalysisMode.DECISION_TIME),
    as_of: datetime | None = Query(
        None, description="Required when mode=as_of: treat forecasts published by this UTC timestamp as known"
    ),
) -> AnalysisParams:
    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")
    if (end_date - start_date).days > MAX_RANGE_DAYS:
        raise HTTPException(
            status_code=400, detail=f"requested range exceeds the {MAX_RANGE_DAYS}-day limit"
        )
    if mode == AnalysisMode.AS_OF and as_of is None:
        raise HTTPException(status_code=400, detail="as_of is required when mode=as_of")

    if as_of is not None and as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)

    range_start = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
    range_end = datetime.combine(end_date, datetime.min.time(), tzinfo=timezone.utc)
    return AnalysisParams(range_start=range_start, range_end=range_end, mode=mode, as_of=as_of)
