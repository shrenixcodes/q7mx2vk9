from datetime import datetime, timedelta, timezone

from app.ingestion.actuals import fetch_actual_wind_generation
from app.ingestion.cache import FileCache
from app.ingestion.forecasts import fetch_forecast_wind_generation


class _StubClient:
    def __init__(self, records_by_call: list[list[dict]]) -> None:
        self._records_by_call = records_by_call
        self.calls: list[tuple[str, datetime, datetime]] = []

    async def fetch_stream(self, dataset, start, end):
        self.calls.append((dataset, start, end))
        return self._records_by_call[len(self.calls) - 1]


async def test_fetch_actuals_chunks_wide_ranges_and_normalizes(tmp_path, fuelhh_wind_sample):
    client = _StubClient([fuelhh_wind_sample, []])
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(days=20)  # wider than the 14-day chunk size

    accepted, rejected = await fetch_actual_wind_generation(
        client, start, end, cache=FileCache(directory=tmp_path)
    )

    assert len(client.calls) == 2  # bounded date-range retrieval, chunked
    assert rejected == []
    assert len(accepted) == 4


async def test_fetch_actuals_uses_cache_on_second_call(tmp_path, fuelhh_wind_sample):
    client = _StubClient([fuelhh_wind_sample])
    cache = FileCache(directory=tmp_path)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    await fetch_actual_wind_generation(client, start, end, cache=cache)
    await fetch_actual_wind_generation(client, start, end, cache=cache)

    assert len(client.calls) == 1  # second call was served from cache


async def test_fetch_forecasts_preserves_vintages(tmp_path, windfor_two_vintages_sample):
    client = _StubClient([windfor_two_vintages_sample])
    start = datetime(2026, 1, 10, tzinfo=timezone.utc)
    end = start + timedelta(hours=6)

    accepted, rejected = await fetch_forecast_wind_generation(
        client, start, end, cache=FileCache(directory=tmp_path)
    )

    assert rejected == []
    delivery = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
    assert len([r for r in accepted if r.delivery_start == delivery]) == 2
