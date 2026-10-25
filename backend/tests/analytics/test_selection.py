from datetime import datetime, timezone

from app.analytics.selection import (
    default_decision_cutoff,
    group_forecasts_by_delivery,
    select_forecast_for_interval,
    select_latest_eligible_forecast,
)
from app.ingestion.models import ForecastGenerationRecord


def _forecast(delivery_start: str, publish_time: str, generation: float) -> ForecastGenerationRecord:
    return ForecastGenerationRecord(
        delivery_start=datetime.fromisoformat(delivery_start),
        publish_time=datetime.fromisoformat(publish_time),
        generation_mw=generation,
    )


def test_selects_latest_eligible_forecast_not_newest_overall():
    candidates = [
        _forecast("2026-01-10T00:00:00+00:00", "2026-01-08T10:00:00+00:00", 100.0),
        _forecast("2026-01-10T00:00:00+00:00", "2026-01-09T10:00:00+00:00", 110.0),
        _forecast("2026-01-10T00:00:00+00:00", "2026-01-09T20:00:00+00:00", 120.0),  # too late
    ]
    cutoff = datetime(2026, 1, 9, 11, 0, tzinfo=timezone.utc)
    selected = select_latest_eligible_forecast(candidates, cutoff)
    assert selected is not None
    assert selected.generation_mw == 110.0


def test_never_selects_forecast_published_after_cutoff():
    candidates = [_forecast("2026-01-10T00:00:00+00:00", "2026-01-09T23:00:00+00:00", 999.0)]
    cutoff = datetime(2026, 1, 9, 11, 0, tzinfo=timezone.utc)
    assert select_latest_eligible_forecast(candidates, cutoff) is None


def test_returns_none_when_no_eligible_forecast_exists():
    assert select_latest_eligible_forecast([], datetime(2026, 1, 9, tzinfo=timezone.utc)) is None


def test_boundary_timestamp_equal_to_cutoff_is_eligible():
    cutoff = datetime(2026, 1, 9, 11, 0, tzinfo=timezone.utc)
    candidates = [_forecast("2026-01-10T00:00:00+00:00", "2026-01-09T11:00:00+00:00", 100.0)]
    selected = select_latest_eligible_forecast(candidates, cutoff)
    assert selected is not None
    assert selected.generation_mw == 100.0


def test_half_hour_delivery_maps_to_containing_forecast_hour():
    grouped = group_forecasts_by_delivery(
        [_forecast("2026-01-10T00:00:00+00:00", "2026-01-09T20:00:00+00:00", 150.0)]
    )
    half_hour_delivery = datetime(2026, 1, 10, 0, 30, tzinfo=timezone.utc)
    cutoff = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
    selected = select_forecast_for_interval(grouped, half_hour_delivery, cutoff)
    assert selected is not None
    assert selected.generation_mw == 150.0


def test_default_decision_cutoff_is_gate_closure_day_before_in_london_time():
    delivery_start = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)
    cutoff = default_decision_cutoff(delivery_start)
    # January is GMT (UTC+0), so 11:00 Europe/London == 11:00 UTC.
    assert cutoff == datetime(2026, 1, 14, 11, 0, tzinfo=timezone.utc)
