from __future__ import annotations

import logging
from datetime import datetime, timedelta

from app.ingestion.cache import FileCache
from app.ingestion.client import ElexonClient
from app.ingestion.date_ranges import chunk_range
from app.ingestion.models import ForecastGenerationRecord, RejectedRecord
from app.ingestion.normalize import normalize_forecast_generation

logger = logging.getLogger("windlens.ingestion.forecasts")

DATASET = "WINDFOR"
_MAX_CHUNK_SPAN = timedelta(days=14)


async def fetch_forecast_wind_generation(
    client: ElexonClient,
    publish_from: datetime,
    publish_to: datetime,
    cache: FileCache | None = None,
) -> tuple[list[ForecastGenerationRecord], list[RejectedRecord]]:
    """Retrieve and normalize wind forecast vintages published in [publish_from, publish_to).

    `publish_from`/`publish_to` bound the *publication* window, not delivery.
    Callers evaluating January 2026 decisions must widen this window back
    into December 2025 to see forecasts that were already available -- see
    Settings.forecast_history_lookback_days.
    """
    cache = cache or FileCache()
    all_raw: list[dict] = []

    for chunk_start, chunk_end in chunk_range(publish_from, publish_to, _MAX_CHUNK_SPAN):
        cache_key = f"windfor_{chunk_start.isoformat()}_{chunk_end.isoformat()}"
        raw = cache.get(cache_key)
        if raw is None:
            raw = await client.fetch_stream(DATASET, chunk_start, chunk_end)
            cache.set(cache_key, raw)
        else:
            logger.info("cache_hit dataset=%s range=%s..%s", DATASET, chunk_start, chunk_end)
        all_raw.extend(raw)

    return normalize_forecast_generation(all_raw)
