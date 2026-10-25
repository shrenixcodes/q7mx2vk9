from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.analytics.models import AnalysisMode, IntervalStatus


class OverviewResponse(BaseModel):
    mode: AnalysisMode
    as_of: datetime | None
    delivery_range_start: datetime
    delivery_range_end: datetime
    expected_intervals: int
    matched_intervals: int
    coverage_percent: float
    unit: str
    mae: float | None
    rmse: float | None
    bias: float | None
    total_wind_shortfall: float | None
    total_wind_surplus: float | None
    source_loaded_at: datetime | None
    warnings: list[str]


class ForecastIntervalResponse(BaseModel):
    delivery_start: datetime
    forecast_generation_mw: float | None
    actual_generation_mw: float | None
    forecast_publish_time: datetime | None
    error_mw: float | None
    wind_shortfall_mw: float | None
    wind_surplus_mw: float | None
    status: IntervalStatus


class ForecastsResponse(BaseModel):
    mode: AnalysisMode
    as_of: datetime | None
    total_count: int
    limit: int
    offset: int
    records: list[ForecastIntervalResponse]


class AccuracyResponse(BaseModel):
    mode: AnalysisMode
    as_of: datetime | None
    sample_count: int
    unit: str
    mae: float | None
    rmse: float | None
    bias: float | None
    mape_percent: float | None
    mape_excluded_low_actual_count: int
    coverage_percent: float
    warnings: list[str]


class MetadataResponse(BaseModel):
    datasets: list[str]
    analysis_range_start: date
    analysis_range_end: date
    generation_unit: str
    actual_interval_resolution_minutes: int
    forecast_interval_resolution_minutes: int
    timezone_note: str
    decision_cutoff_methodology: str
    source_loaded_at: datetime | None
    source_load_error: str | None
    limitations: list[str]


class RefreshResponse(BaseModel):
    status: str
    loaded_at: datetime | None
