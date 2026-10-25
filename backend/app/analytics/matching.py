from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from app.analytics.models import CoverageStats, IntervalStatus, MatchedInterval
from app.analytics.selection import group_forecasts_by_delivery, select_forecast_for_interval
from app.ingestion.models import ActualGenerationRecord, ForecastGenerationRecord


def build_matched_intervals(
    expected_delivery_starts: list[datetime],
    forecasts: list[ForecastGenerationRecord],
    actuals: list[ActualGenerationRecord],
    cutoff_for: Callable[[datetime], datetime],
) -> list[MatchedInterval]:
    """One row per expected delivery interval: at most one forecast, one actual.

    Actuals are keyed by delivery_start (already deduplicated upstream in
    normalize_actual_generation), so this is a one-to-one join by
    construction, not a many-to-many merge.
    """
    grouped_forecasts = group_forecasts_by_delivery(forecasts)
    actuals_by_start = {a.delivery_start: a for a in actuals}

    results: list[MatchedInterval] = []
    for delivery_start in expected_delivery_starts:
        cutoff = cutoff_for(delivery_start)
        forecast = select_forecast_for_interval(grouped_forecasts, delivery_start, cutoff)
        actual = actuals_by_start.get(delivery_start)

        if forecast is not None and actual is not None:
            error = forecast.generation_mw - actual.generation_mw
            status = IntervalStatus.MATCHED
        elif forecast is None and actual is not None:
            error = None
            status = IntervalStatus.FORECAST_UNAVAILABLE
        elif forecast is not None and actual is None:
            error = None
            status = IntervalStatus.ACTUAL_UNAVAILABLE
        else:
            error = None
            status = IntervalStatus.BOTH_UNAVAILABLE

        results.append(
            MatchedInterval(
                delivery_start=delivery_start,
                decision_cutoff=cutoff,
                forecast_generation_mw=forecast.generation_mw if forecast else None,
                forecast_publish_time=forecast.publish_time if forecast else None,
                actual_generation_mw=actual.generation_mw if actual else None,
                status=status,
                error_mw=error,
                wind_shortfall_mw=max(error, 0.0) if error is not None else None,
                wind_surplus_mw=max(-error, 0.0) if error is not None else None,
            )
        )
    return results


def compute_coverage(intervals: list[MatchedInterval]) -> CoverageStats:
    expected = len(intervals)
    matched = sum(1 for i in intervals if i.status == IntervalStatus.MATCHED)
    forecast_unavailable = sum(1 for i in intervals if i.status == IntervalStatus.FORECAST_UNAVAILABLE)
    actual_unavailable = sum(1 for i in intervals if i.status == IntervalStatus.ACTUAL_UNAVAILABLE)
    both_unavailable = sum(1 for i in intervals if i.status == IntervalStatus.BOTH_UNAVAILABLE)
    coverage_percent = (matched / expected * 100) if expected else 0.0
    return CoverageStats(
        expected_intervals=expected,
        matched_intervals=matched,
        forecast_unavailable_intervals=forecast_unavailable,
        actual_unavailable_intervals=actual_unavailable,
        both_unavailable_intervals=both_unavailable,
        coverage_percent=coverage_percent,
    )
