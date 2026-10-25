from datetime import datetime, timezone

import httpx
import pytest

from app.core.config import settings
from app.ingestion.client import ElexonClient
from app.ingestion.exceptions import ElexonHTTPError, ElexonTimeoutError

START = datetime(2026, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 1, 2, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _fast_retries(monkeypatch):
    monkeypatch.setattr(settings, "elexon_retry_backoff_seconds", 0.0)
    monkeypatch.setattr(settings, "elexon_max_retries", 3)


def _client_with(handler) -> ElexonClient:
    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.test")
    return ElexonClient(http_client=async_client)


async def test_successful_fetch_returns_parsed_records():
    def handler(request):
        return httpx.Response(200, json=[{"dataset": "FUELHH"}])

    async with _client_with(handler) as client:
        records = await client.fetch_stream("FUELHH", START, END)
    assert records == [{"dataset": "FUELHH"}]


async def test_empty_result_is_not_an_error():
    def handler(request):
        return httpx.Response(200, json=[])

    async with _client_with(handler) as client:
        records = await client.fetch_stream("WINDFOR", START, END)
    assert records == []


async def test_retries_on_server_error_then_succeeds():
    calls = {"count": 0}

    def handler(request):
        calls["count"] += 1
        if calls["count"] < 3:
            return httpx.Response(503, text="temporarily unavailable")
        return httpx.Response(200, json=[{"ok": True}])

    async with _client_with(handler) as client:
        records = await client.fetch_stream("FUELHH", START, END)
    assert records == [{"ok": True}]
    assert calls["count"] == 3


async def test_exhausts_retries_and_raises():
    calls = {"count": 0}

    def handler(request):
        calls["count"] += 1
        return httpx.Response(429, text="rate limited")

    async with _client_with(handler) as client:
        with pytest.raises(ElexonHTTPError):
            await client.fetch_stream("FUELHH", START, END)
    assert calls["count"] == settings.elexon_max_retries


async def test_non_retryable_client_error_fails_fast():
    calls = {"count": 0}

    def handler(request):
        calls["count"] += 1
        return httpx.Response(400, text='{"errors": "bad date"}')

    async with _client_with(handler) as client:
        with pytest.raises(ElexonHTTPError) as exc_info:
            await client.fetch_stream("FUELHH", START, END)
    assert calls["count"] == 1
    assert exc_info.value.status_code == 400


async def test_timeout_is_retried_then_raises_typed_error():
    def handler(request):
        raise httpx.ReadTimeout("no response")

    async with _client_with(handler) as client:
        with pytest.raises(ElexonTimeoutError):
            await client.fetch_stream("FUELHH", START, END)
