from __future__ import annotations

import asyncio
import logging
from datetime import datetime

import httpx

from app.core.config import settings
from app.ingestion.exceptions import (
    ElexonHTTPError,
    ElexonRateLimitedError,
    ElexonTimeoutError,
)

logger = logging.getLogger("windlens.ingestion.client")

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class ElexonClient:
    """Thin async wrapper over the Elexon Insights Solution `/stream` endpoints.

    Verified live against data.elexon.co.uk on 2026-10-25: public, unauthenticated,
    GET requests with `publishDateTimeFrom`/`publishDateTimeTo` ISO-8601 UTC params,
    returning an un-paginated JSON array for the requested range.
    """

    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(
            base_url=settings.elexon_base_url,
            timeout=settings.elexon_request_timeout_seconds,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "ElexonClient":
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.aclose()

    async def fetch_stream(
        self,
        dataset: str,
        publish_from: datetime,
        publish_to: datetime,
    ) -> list[dict]:
        """GET /datasets/{dataset}/stream for the given publish-time window."""
        params = {
            "publishDateTimeFrom": publish_from.isoformat().replace("+00:00", "Z"),
            "publishDateTimeTo": publish_to.isoformat().replace("+00:00", "Z"),
        }
        path = f"/datasets/{dataset}/stream"

        last_error: Exception | None = None
        for attempt in range(1, settings.elexon_max_retries + 1):
            try:
                response = await self._client.get(path, params=params)
            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning(
                    "elexon_request_timeout dataset=%s attempt=%d/%d",
                    dataset,
                    attempt,
                    settings.elexon_max_retries,
                )
                await self._backoff(attempt)
                continue
            except httpx.TransportError as exc:
                last_error = exc
                logger.warning(
                    "elexon_request_transport_error dataset=%s attempt=%d/%d error=%s",
                    dataset,
                    attempt,
                    settings.elexon_max_retries,
                    exc,
                )
                await self._backoff(attempt)
                continue

            if response.status_code == 200:
                records = response.json()
                logger.info(
                    "elexon_request_ok dataset=%s range=%s..%s records=%d",
                    dataset,
                    params["publishDateTimeFrom"],
                    params["publishDateTimeTo"],
                    len(records),
                )
                return records

            if response.status_code in _RETRYABLE_STATUS_CODES:
                logger.warning(
                    "elexon_request_retryable_status dataset=%s status=%d attempt=%d/%d",
                    dataset,
                    response.status_code,
                    attempt,
                    settings.elexon_max_retries,
                )
                last_error = ElexonRateLimitedError(response.status_code, response.text[:200])
                await self._backoff(attempt)
                continue

            # Non-retryable client error - fail fast, do not retry.
            raise ElexonHTTPError(response.status_code, response.text[:200])

        if isinstance(last_error, httpx.TimeoutException):
            raise ElexonTimeoutError(str(last_error)) from last_error
        if last_error is not None:
            raise last_error
        raise ElexonHTTPError(0, "exhausted retries with no response")

    async def _backoff(self, attempt: int) -> None:
        delay = settings.elexon_retry_backoff_seconds * (2 ** (attempt - 1))
        await asyncio.sleep(delay)
