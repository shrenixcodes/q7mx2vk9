from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class AnalysisMode(str, Enum):
    DECISION_TIME = "decision_time"
    AS_OF = "as_of"


class IntervalStatus(str, Enum):
    MATCHED = "matched"
    FORECAST_UNAVAILABLE = "forecast_unavailable"
    ACTUAL_UNAVAILABLE = "actual_unavailable"
    BOTH_UNAVAILABLE = "both_unavailable"


class MatchedInterval(BaseModel):
    delivery_start: datetime
    decision_cutoff: datetime
    forecast_generation_mw: float | None
    forecast_publish_time: datetime | None
    actual_generation_mw: float | None
    status: IntervalStatus
    error_mw: float | None
    wind_shortfall_mw: float | None
    wind_surplus_mw: float | None


class CoverageStats(BaseModel):
    expected_intervals: int
    matched_intervals: int
    forecast_unavailable_intervals: int
    actual_unavailable_intervals: int
    both_unavailable_intervals: int
    coverage_percent: float


class AccuracyMetrics(BaseModel):
    sample_count: int
    unit: str = "MW"
    mae: float | None
    rmse: float | None
    bias: float | None
    mape_percent: float | None
    mape_excluded_low_actual_count: int


class ExposureSummary(BaseModel):
    sample_count: int
    unit: str = "MW"
    total_wind_shortfall: float | None
    total_wind_surplus: float | None
    mean_wind_shortfall: float | None
    mean_wind_surplus: float | None


class BacktestResult(BaseModel):
    mode: AnalysisMode
    delivery_range_start: datetime
    delivery_range_end: datetime
    as_of: datetime | None
    intervals: list[MatchedInterval]
    coverage: CoverageStats
    accuracy: AccuracyMetrics
    exposure: ExposureSummary
