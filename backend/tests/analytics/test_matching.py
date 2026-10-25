from datetime import datetime, timezone

from app.analytics.matching import build_matched_intervals, compute_coverage
from app.analytics.models import IntervalStatus
from app.ingestion.models import ActualGenerationRecord, ForecastGenerationRecord

T0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
T1 = datetime(2026, 1, 10, 0, 30, tzinfo=timezone.utc)
T2 = datetime(2026, 1, 10, 1, 0, tzinfo=timezone.utc)
PUBLISH = datetime(2026, 1, 9, 20, 0, tzinfo=timezone.utc)


def _actual(delivery_start, generation):
    return ActualGenerationRecord(
        delivery_start=delivery_start, settlement_period=1, generation_mw=generation, source_publish_time=PUBLISH
    )


def _forecast(delivery_start, generation, publish_time=PUBLISH):
    return ForecastGenerationRecord(delivery_start=delivery_start, publish_time=publish_time, generation_mw=generation)


def test_matched_interval_computes_error_shortfall_surplus():
    intervals = build_matched_intervals(
        [T0], [_forecast(T0, 120.0)], [_actual(T0, 100.0)], cutoff_for=lambda _: datetime(2026, 1, 9, 23, 0, tzinfo=timezone.utc)
    )
    assert intervals[0].status == IntervalStatus.MATCHED
    assert intervals[0].error_mw == 20.0
    assert intervals[0].wind_shortfall_mw == 20.0
    assert intervals[0].wind_surplus_mw == 0.0


def test_missing_actual_is_not_treated_as_zero():
    intervals = build_matched_intervals(
        [T0], [_forecast(T0, 120.0)], [], cutoff_for=lambda _: datetime(2026, 1, 9, 23, 0, tzinfo=timezone.utc)
    )
    assert intervals[0].status == IntervalStatus.ACTUAL_UNAVAILABLE
    assert intervals[0].actual_generation_mw is None
    assert intervals[0].error_mw is None


def test_missing_forecast_is_reported_not_substituted():
    intervals = build_matched_intervals(
        [T0], [], [_actual(T0, 100.0)], cutoff_for=lambda _: datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    assert intervals[0].status == IntervalStatus.FORECAST_UNAVAILABLE
    assert intervals[0].forecast_generation_mw is None


def test_one_forecast_one_actual_per_interval_no_many_to_many():
    forecasts = [_forecast(T0, 120.0), _forecast(T0, 999.0, publish_time=PUBLISH)]  # same key, handled upstream
    intervals = build_matched_intervals(
        [T0], [forecasts[0]], [_actual(T0, 100.0)], cutoff_for=lambda _: datetime(2026, 1, 9, 23, 0, tzinfo=timezone.utc)
    )
    assert len(intervals) == 1


def test_empty_expected_range_returns_empty_list():
    assert build_matched_intervals([], [], [], cutoff_for=lambda _: PUBLISH) == []


def test_coverage_counts_each_status_bucket():
    intervals = build_matched_intervals(
        [T0, T1, T2],
        [_forecast(T0, 120.0), _forecast(T1, 110.0)],
        [_actual(T0, 100.0), _actual(T2, 90.0)],
        cutoff_for=lambda _: datetime(2026, 1, 9, 23, 0, tzinfo=timezone.utc),
    )
    coverage = compute_coverage(intervals)
    assert coverage.expected_intervals == 3
    assert coverage.matched_intervals == 1  # T0
    assert coverage.actual_unavailable_intervals == 1  # T1: forecast but no actual
    assert coverage.forecast_unavailable_intervals == 1  # T2: actual but no forecast
    assert coverage.coverage_percent == (1 / 3) * 100
