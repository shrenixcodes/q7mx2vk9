from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger("windlens.ingestion.cache")


class FileCache:
    """A small JSON file cache. Performance optimization only.

    Never the system of record: a cache miss simply means we re-fetch from
    Elexon, which is why this is safe to lose on an ephemeral filesystem
    (e.g. a Render free-tier restart).
    """

    def __init__(self, directory: Path | None = None, ttl_seconds: int | None = None) -> None:
        self.directory = directory or settings.elexon_cache_dir
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else settings.elexon_cache_ttl_seconds

    def _path_for(self, key: str) -> Path:
        safe_key = key.replace(":", "-")
        return self.directory / f"{safe_key}.json"

    def get(self, key: str) -> list[dict] | None:
        path = self._path_for(key)
        if not path.exists():
            return None

        age_seconds = time.time() - path.stat().st_mtime
        if age_seconds > self.ttl_seconds:
            logger.info("cache_expired key=%s age_seconds=%.0f", key, age_seconds)
            return None

        try:
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("cache_corrupt key=%s error=%s", key, exc)
            return None

    def set(self, key: str, records: list[dict]) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self._path_for(key)
        tmp_path = path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(records, fh)
        tmp_path.replace(path)
