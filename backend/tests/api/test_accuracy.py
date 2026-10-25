async def test_accuracy_reports_null_metrics_when_nothing_matched(client, seeded_service):
    response = await client.get(
        "/api/v1/accuracy", params={"start_date": "2026-01-10", "end_date": "2026-01-11"}
    )
    body = response.json()
    assert body["sample_count"] == 0
    assert body["mae"] is None
    assert body["coverage_percent"] == 0.0


async def test_accuracy_computes_real_metrics_once_matched(client, seeded_service):
    response = await client.get(
        "/api/v1/accuracy",
        params={
            "start_date": "2026-01-10",
            "end_date": "2026-01-11",
            "mode": "as_of",
            "as_of": "2026-01-10T05:00:00Z",
        },
    )
    body = response.json()
    assert body["sample_count"] == 4
    assert body["unit"] == "MW"
    assert body["mae"] >= 0
    assert body["rmse"] >= body["mae"] - 1e-6  # RMSE >= MAE always holds


async def test_accuracy_without_loaded_data_returns_503(client, unloaded_service):
    response = await client.get(
        "/api/v1/accuracy", params={"start_date": "2026-01-10", "end_date": "2026-01-11"}
    )
    assert response.status_code == 503
