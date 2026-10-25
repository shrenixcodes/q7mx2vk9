from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app


async def test_health_ok_without_live_elexon_dependency(monkeypatch):
    monkeypatch.setattr(settings, "auto_refresh_on_startup", False)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_versioned_health_alias(monkeypatch):
    monkeypatch.setattr(settings, "auto_refresh_on_startup", False)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
