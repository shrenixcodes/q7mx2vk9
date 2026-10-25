import math
from datetime import datetime, timezone

from app.analytics.exposure import compute_exposure
from app.analytics.metrics import compute_accuracy_metrics
from app.analytics.models import IntervalStatus, MatchedInterval

T0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
CUTOFF = datetime(2026, 1, 9, 23, 0, tzinfo=timezone.utc)
PUBLISH = datetime(2026, 1, 9, 20, 0, tzinfo=timezone.utc)


def _matched(forecast, actual):
    error = forecast - actual
    return MatchedInterval(
        delivery_start=T0,
        decision_cutoff=CUTOFF,
        forecast_generation_mw=forecast,
        forecast_publish_time=PUBLISH,
        actual_generation_mw=actual,
        status=IntervalStatus.MATCHED,
        error_mw=error,
        wind_shortfall_mw=max(error, 0.0),
        wind_surplus_mw=max(-error, 0.0),
    )


def _unmatched(status: IntervalStatus) -> MatchedInterval:
    return MatchedInterval(
        delivery_start=T0,
        decision_cutoff=CUTOFF,
        forecast_generation_mw=None,
        forecast_publish_time=None,
        actual_generation_mw=None,
        status=status,
        error_mw=None,
        wind_shortfall_mw=None,
        wind_surplus_mw=None,
    )


def test_exact_mae_rmse_bias():
    # errors: +20 (over), -10 (under)
    intervals = [_matched(120, 100), _matched(90, 100)]
    metrics = compute_accuracy_metrics(intervals)
    assert metrics.sample_count == 2
    assert metrics.mae == 15.0
    assert metrics.rmse == math.sqrt((400 + 100) / 2)
    assert metrics.bias == 5.0  # mean(+20, -10)


def test_empty_matched_dataset_returns_null_metrics_not_an_error():
    metrics = compute_accuracy_metrics([_unmatched(IntervalStatus.FORECAST_UNAVAILABLE)])
    assert metrics.sample_count == 0
    assert metrics.mae is None
    assert metrics.rmse is None
    assert metrics.bias is None
    assert metrics.mape_percent is None


def test_mape_excludes_near_zero_actual_denominator():
    intervals = [_matched(120, 100), _matched(10, 5)]  # second: actual=5 MW, below threshold
    metrics = compute_accuracy_metrics(intervals)
    assert metrics.mape_excluded_low_actual_count == 1
    assert metrics.mape_percent == abs((120 - 100) / 100) * 100


def test_wind_shortfall_and_surplus_totals():
    intervals = [_matched(120, 100), _matched(90, 100)]
    exposure = compute_exposure(intervals)
    assert exposure.total_wind_shortfall == 20.0
    assert exposure.total_wind_surplus == 10.0
    assert exposure.mean_wind_shortfall == 10.0
    assert exposure.mean_wind_surplus == 5.0


def test_exposure_on_empty_matched_dataset_is_null_not_zero():
    exposure = compute_exposure([_unmatched(IntervalStatus.BOTH_UNAVAILABLE)])
    assert exposure.sample_count == 0
    assert exposure.total_wind_shortfall is None
    assert exposure.total_wind_surplus is None
