async def test_overview_decision_time_reports_no_eligible_forecast(client, seeded_service):
    # Fixture forecasts were published on 2026-01-10, after the default
    # day-ahead cutoff (2026-01-09T11:00Z) for deliveries that same day, so
    # decision-time mode must not leak them in.
    response = await client.get(
        "/api/v1/overview", params={"start_date": "2026-01-10", "end_date": "2026-01-11"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "decision_time"
    assert body["matched_intervals"] == 0
    assert body["mae"] is None
    assert body["warnings"]


async def test_overview_as_of_mode_matches_once_forecast_is_eligible(client, seeded_service):
    response = await client.get(
        "/api/v1/overview",
        params={
            "start_date": "2026-01-10",
            "end_date": "2026-01-11",
            "mode": "as_of",
            "as_of": "2026-01-10T05:00:00Z",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "as_of"
    assert body["matched_intervals"] == 4
    assert body["mae"] is not None


async def test_overview_without_loaded_data_returns_503(client, unloaded_service):
    response = await client.get(
        "/api/v1/overview", params={"start_date": "2026-01-10", "end_date": "2026-01-11"}
    )
    assert response.status_code == 503


async def test_overview_rejects_invalid_date_range(client, seeded_service):
    response = await client.get(
        "/api/v1/overview", params={"start_date": "2026-01-11", "end_date": "2026-01-10"}
    )
    assert response.status_code == 400


async def test_overview_as_of_mode_without_as_of_is_rejected(client, seeded_service):
    response = await client.get(
        "/api/v1/overview",
        params={"start_date": "2026-01-10", "end_date": "2026-01-11", "mode": "as_of"},
    )
    assert response.status_code == 400


async def test_overview_rejects_malformed_mode(client, seeded_service):
    response = await client.get(
        "/api/v1/overview",
        params={"start_date": "2026-01-10", "end_date": "2026-01-11", "mode": "not-a-mode"},
    )
    assert response.status_code == 422
