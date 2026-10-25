async def test_forecasts_lists_expected_interval_count(client, seeded_service):
    response = await client.get(
        "/api/v1/forecasts",
        params={"start_date": "2026-01-10", "end_date": "2026-01-11", "limit": "2000"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_count"] == 48  # one day of half-hour intervals
    assert len(body["records"]) == 48


async def test_forecasts_pagination_limit_and_offset(client, seeded_service):
    response = await client.get(
        "/api/v1/forecasts",
        params={"start_date": "2026-01-10", "end_date": "2026-01-11", "limit": "5", "offset": "10"},
    )
    body = response.json()
    assert body["limit"] == 5
    assert body["offset"] == 10
    assert len(body["records"]) == 5


async def test_forecasts_missing_actual_is_null_not_zero(client, seeded_service):
    response = await client.get(
        "/api/v1/forecasts",
        params={"start_date": "2026-01-10", "end_date": "2026-01-11", "limit": "2000"},
    )
    records = response.json()["records"]
    late_interval = next(r for r in records if r["delivery_start"] == "2026-01-10T23:00:00Z")
    assert late_interval["actual_generation_mw"] is None
    assert late_interval["status"] == "both_unavailable"


async def test_forecasts_rejects_limit_above_max(client, seeded_service):
    response = await client.get(
        "/api/v1/forecasts",
        params={"start_date": "2026-01-10", "end_date": "2026-01-11", "limit": "50000"},
    )
    assert response.status_code == 422
