from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.analytics.backtest import run_backtest
from app.analytics.models import AnalysisMode, BacktestResult
from app.core.config import settings
from app.ingestion.actuals import fetch_actual_wind_generation
from app.ingestion.client import ElexonClient
from app.ingestion.exceptions import ElexonAPIError
from app.ingestion.forecasts import fetch_forecast_wind_generation
from app.ingestion.models import ActualGenerationRecord, ForecastGenerationRecord

logger = logging.getLogger("windlens.services.analysis")

MIN_REFRESH_INTERVAL = timedelta(seconds=60)


class DataUnavailableError(RuntimeError):
    pass


class RefreshThrottledError(RuntimeError):
    def __init__(self, min_interval: timedelta) -> None:
        super().__init__(f"refresh attempted within the {int(min_interval.total_seconds())}s cooldown window")


class AnalysisService:
    """Holds the one in-memory copy of normalized ingestion data used by every
    dashboard request, so filter changes (date range / mode) never trigger a
    fresh Elexon fetch -- only /refresh and the startup load do.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._actuals: list[ActualGenerationRecord] = []
        self._forecasts: list[ForecastGenerationRecord] = []
        self._loaded_at: datetime | None = None
        self._last_refresh_attempt: datetime | None = None
        self._last_error: str | None = None

    @property
    def loaded_at(self) -> datetime | None:
        return self._loaded_at

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def has_data(self) -> bool:
        return self._loaded_at is not None

    def load_for_testing(
        self,
        actuals: list[ActualGenerationRecord],
        forecasts: list[ForecastGenerationRecord],
    ) -> None:
        """Seam for tests: seed data without a network call or asyncio.Lock."""
        self._actuals = actuals
        self._forecasts = forecasts
        self._loaded_at = datetime.now(timezone.utc)
        self._last_error = None

    async def ensure_loaded(self) -> None:
        if not self.has_data():
            await self.refresh(force=True)

    async def refresh(self, force: bool = False) -> None:
        now = datetime.now(timezone.utc)
        if not force and self._last_refresh_attempt is not None:
            elapsed = now - self._last_refresh_attempt
            if elapsed < MIN_REFRESH_INTERVAL:
                raise RefreshThrottledError(MIN_REFRESH_INTERVAL - elapsed)

        async with self._lock:
            self._last_refresh_attempt = datetime.now(timezone.utc)
            delivery_start = datetime.combine(
                settings.analysis_range_start, datetime.min.time(), tzinfo=timezone.utc
            )
            delivery_end = datetime.combine(
                settings.analysis_range_end, datetime.min.time(), tzinfo=timezone.utc
            )
            publish_from = delivery_start - timedelta(days=settings.forecast_history_lookback_days)

            try:
                async with ElexonClient() as client:
                    actuals, actual_rejected = await fetch_actual_wind_generation(
                        client, delivery_start, delivery_end
                    )
                    forecasts, forecast_rejected = await fetch_forecast_wind_generation(
                        client, publish_from, delivery_end
                    )
            except ElexonAPIError as exc:
                self._last_error = str(exc)
                logger.error("analysis_refresh_failed error=%s", exc)
                raise DataUnavailableError(str(exc)) from exc

            self._actuals = actuals
            self._forecasts = forecasts
            self._loaded_at = datetime.now(timezone.utc)
            self._last_error = None
            logger.info(
                "analysis_refresh_ok actuals=%d forecasts=%d actual_rejected=%d forecast_rejected=%d",
                len(actuals),
                len(forecasts),
                len(actual_rejected),
                len(forecast_rejected),
            )

    def get_backtest(
        self,
        delivery_range_start: datetime,
        delivery_range_end: datetime,
        mode: AnalysisMode,
        as_of: datetime | None,
    ) -> BacktestResult:
        if not self.has_data():
            raise DataUnavailableError("ingestion data has not been loaded yet")
        return run_backtest(
            self._actuals, self._forecasts, delivery_range_start, delivery_range_end, mode, as_of
        )
