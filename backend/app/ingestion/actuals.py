from __future__ import annotations

import logging
from datetime import datetime, timedelta

from app.ingestion.cache import FileCache
from app.ingestion.client import ElexonClient
from app.ingestion.date_ranges import chunk_range
from app.ingestion.models import ActualGenerationRecord, RejectedRecord
from app.ingestion.normalize import normalize_actual_generation

logger = logging.getLogger("windlens.ingestion.actuals")

DATASET = "FUELHH"
_MAX_CHUNK_SPAN = timedelta(days=14)


async def fetch_actual_wind_generation(
    client: ElexonClient,
    start: datetime,
    end: datetime,
    cache: FileCache | None = None,
) -> tuple[list[ActualGenerationRecord], list[RejectedRecord]]:
    """Retrieve and normalize actual wind generation for [start, end)."""
    cache = cache or FileCache()
    all_raw: list[dict] = []

    for chunk_start, chunk_end in chunk_range(start, end, _MAX_CHUNK_SPAN):
        cache_key = f"fuelhh_{chunk_start.isoformat()}_{chunk_end.isoformat()}"
        raw = cache.get(cache_key)
        if raw is None:
            raw = await client.fetch_stream(DATASET, chunk_start, chunk_end)
            cache.set(cache_key, raw)
        else:
            logger.info("cache_hit dataset=%s range=%s..%s", DATASET, chunk_start, chunk_end)
        all_raw.extend(raw)

    return normalize_actual_generation(all_raw)
