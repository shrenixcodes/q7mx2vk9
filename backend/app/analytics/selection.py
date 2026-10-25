from __future__ import annotations

from collections import defaultdict
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.time_grid import hour_bucket
from app.ingestion.models import ForecastGenerationRecord

LONDON = ZoneInfo("Europe/London")

# Assumption, not a verified market rule: approximates a UK day-ahead
# procurement decision being made the afternoon before delivery, around
# the time day-ahead auction results / gate closure information would be
# available. Override with an explicit decision_cutoff when a specific
# process time is known. See README "Methodology" section.
DEFAULT_GATE_CLOSURE_HOUR_LOCAL = 11


def default_decision_cutoff(delivery_start_utc: datetime) -> datetime:
    """Default per-interval decision cutoff: 11:00 Europe/London, one day before delivery."""
    delivery_local_date = delivery_start_utc.astimezone(LONDON).date()
    cutoff_date = delivery_local_date - timedelta(days=1)
    cutoff_local = datetime.combine(
        cutoff_date, time(hour=DEFAULT_GATE_CLOSURE_HOUR_LOCAL), tzinfo=LONDON
    )
    return cutoff_local.astimezone(delivery_start_utc.tzinfo)


def group_forecasts_by_delivery(
    forecasts: list[ForecastGenerationRecord],
) -> dict[datetime, list[ForecastGenerationRecord]]:
    grouped: dict[datetime, list[ForecastGenerationRecord]] = defaultdict(list)
    for forecast in forecasts:
        grouped[forecast.delivery_start].append(forecast)
    return grouped


def select_latest_eligible_forecast(
    candidates: list[ForecastGenerationRecord], cutoff: datetime
) -> ForecastGenerationRecord | None:
    """Latest-published forecast with publish_time <= cutoff, or None.

    Never returns a forecast published after cutoff -- this is the sole
    mechanism preventing look-ahead bias in decision-time backtests.
    """
    eligible = [f for f in candidates if f.publish_time <= cutoff]
    if not eligible:
        return None
    return max(eligible, key=lambda f: f.publish_time)


def select_forecast_for_interval(
    grouped_forecasts: dict[datetime, list[ForecastGenerationRecord]],
    delivery_start: datetime,
    cutoff: datetime,
) -> ForecastGenerationRecord | None:
    """Resolve the half-hour `delivery_start` to its containing forecast hour.

    WINDFOR publishes hourly delivery intervals while FUELHH actuals are
    half-hourly (verified live, 2026-10-25); both half-hours in a clock
    hour share the one hourly forecast value for that hour.
    """
    candidates = grouped_forecasts.get(hour_bucket(delivery_start), [])
    return select_latest_eligible_forecast(candidates, cutoff)
