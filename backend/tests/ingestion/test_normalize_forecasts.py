from datetime import datetime, timezone

from app.ingestion.normalize import normalize_forecast_generation


def test_retains_multiple_vintages_for_same_delivery_interval(windfor_two_vintages_sample):
    accepted, rejected = normalize_forecast_generation(windfor_two_vintages_sample)
    assert rejected == []

    delivery = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
    vintages_for_delivery = [r for r in accepted if r.delivery_start == delivery]
    assert len(vintages_for_delivery) == 2
    publish_times = {r.publish_time for r in vintages_for_delivery}
    assert publish_times == {
        datetime(2026, 1, 10, 2, 30, tzinfo=timezone.utc),
        datetime(2026, 1, 10, 4, 30, tzinfo=timezone.utc),
    }


def test_rejects_invalid_timestamp_and_nonnumeric_generation():
    raw = [
        {"startTime": "garbage", "publishTime": "2026-01-10T02:30:00Z", "generation": 100},
        {"startTime": "2026-01-10T00:00:00Z", "publishTime": "2026-01-10T02:30:00Z", "generation": "NaN-ish"},
    ]
    accepted, rejected = normalize_forecast_generation(raw)
    assert accepted == []
    assert len(rejected) == 2


def test_exact_duplicate_rows_are_collapsed():
    row = {"startTime": "2026-01-10T00:00:00Z", "publishTime": "2026-01-10T02:30:00Z", "generation": 11949}
    accepted, rejected = normalize_forecast_generation([row, dict(row)])
    assert rejected == []
    assert len(accepted) == 1


def test_empty_input_returns_empty_lists():
    accepted, rejected = normalize_forecast_generation([])
    assert accepted == []
    assert rejected == []
