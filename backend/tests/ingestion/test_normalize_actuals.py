from datetime import datetime, timezone

from app.ingestion.normalize import normalize_actual_generation


def test_filters_to_wind_only(fuelhh_mixed_fuel_sample):
    accepted, rejected = normalize_actual_generation(fuelhh_mixed_fuel_sample)
    assert len(accepted) == 1
    assert accepted[0].generation_mw == 11309
    assert rejected == []


def test_normalizes_real_wind_sample(fuelhh_wind_sample):
    accepted, rejected = normalize_actual_generation(fuelhh_wind_sample)
    assert rejected == []
    assert len(accepted) == 4
    assert accepted[0].delivery_start == datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
    assert accepted[0].generation_mw == 11309
    # sorted ascending by delivery_start
    assert [r.delivery_start for r in accepted] == sorted(r.delivery_start for r in accepted)


def test_rejects_invalid_timestamp():
    raw = [
        {
            "fuelType": "WIND",
            "startTime": "not-a-timestamp",
            "publishTime": "2026-01-10T00:30:00Z",
            "settlementPeriod": 1,
            "generation": 11309,
        }
    ]
    accepted, rejected = normalize_actual_generation(raw)
    assert accepted == []
    assert len(rejected) == 1


def test_rejects_nonnumeric_generation():
    raw = [
        {
            "fuelType": "WIND",
            "startTime": "2026-01-10T00:00:00Z",
            "publishTime": "2026-01-10T00:30:00Z",
            "settlementPeriod": 1,
            "generation": "not-a-number",
        }
    ]
    accepted, rejected = normalize_actual_generation(raw)
    assert accepted == []
    assert len(rejected) == 1


def test_empty_input_returns_empty_lists():
    accepted, rejected = normalize_actual_generation([])
    assert accepted == []
    assert rejected == []


def test_duplicate_settlement_period_keeps_latest_published_revision():
    key = dict(
        fuelType="WIND",
        startTime="2026-01-10T00:00:00Z",
        settlementPeriod=1,
    )
    raw = [
        {**key, "publishTime": "2026-01-10T00:30:00Z", "generation": 11309},
        {**key, "publishTime": "2026-01-10T06:00:00Z", "generation": 11400},  # later revision
    ]
    accepted, rejected = normalize_actual_generation(raw)
    assert rejected == []
    assert len(accepted) == 1
    assert accepted[0].generation_mw == 11400
