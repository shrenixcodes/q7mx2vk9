from app.core.config import settings


async def test_configured_origin_is_allowed(client):
    allowed_origin = settings.cors_allowed_origins[0]
    response = await client.get("/health", headers={"Origin": allowed_origin})
    assert response.headers.get("access-control-allow-origin") == allowed_origin


async def test_unconfigured_origin_is_not_echoed_back(client):
    response = await client.get("/health", headers={"Origin": "https://not-allowed.example"})
    assert "access-control-allow-origin" not in response.headers
