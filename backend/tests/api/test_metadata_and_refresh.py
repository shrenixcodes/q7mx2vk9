from app.services.analysis_service import MIN_REFRESH_INTERVAL


async def test_metadata_discloses_resolution_mismatch_and_units(client, seeded_service):
    response = await client.get("/api/v1/metadata")
    assert response.status_code == 200
    body = response.json()
    assert body["generation_unit"] == "MW"
    assert body["actual_interval_resolution_minutes"] == 30
    assert body["forecast_interval_resolution_minutes"] == 60
    assert any("hourly" in limitation for limitation in body["limitations"])


async def test_refresh_is_throttled_within_cooldown(client, seeded_service):
    # seeded_service already has _loaded_at set but no _last_refresh_attempt,
    # so the first refresh call would normally proceed; force a recent
    # attempt to exercise the cooldown path without a real network call.
    import datetime as dt

    seeded_service._last_refresh_attempt = dt.datetime.now(dt.timezone.utc)

    response = await client.post("/api/v1/refresh")
    assert response.status_code == 429
    assert MIN_REFRESH_INTERVAL.total_seconds() == 60
