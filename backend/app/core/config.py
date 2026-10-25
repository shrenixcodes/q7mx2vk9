from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, sourced from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "production"] = "development"

    # CORS: explicit allow-list only. Production deployments must set
    # CORS_ALLOWED_ORIGINS; there is no wildcard fallback.
    cors_allowed_origins: list[str] = ["http://localhost:5173"]

    # Elexon Insights Solution API. Verified live on 2026-10-25: public,
    # unauthenticated, ISO-8601 UTC query params, no pagination on /stream.
    elexon_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    elexon_request_timeout_seconds: float = 10.0
    elexon_max_retries: int = 3
    elexon_retry_backoff_seconds: float = 1.0

    # The assignment's procurement window. End date is exclusive.
    analysis_range_start: date = date(2026, 1, 1)
    analysis_range_end: date = date(2026, 2, 1)

    # How far before analysis_range_start to pull forecast *publications* so
    # that day-ahead decisions near the start of January have real history
    # to select from (forecasts for Jan 1 delivery were published in Dec).
    forecast_history_lookback_days: int = 45

    # Performance cache only - never the system of record. See README.
    elexon_cache_dir: Path = Path(".cache/elexon")
    elexon_cache_ttl_seconds: int = 3600

    log_level: str = "INFO"

    # Disabled in tests so the suite never makes a live Elexon request.
    auto_refresh_on_startup: bool = True

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
