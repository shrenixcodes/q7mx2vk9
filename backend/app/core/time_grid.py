from __future__ import annotations

from datetime import datetime, timedelta, timezone

HALF_HOUR = timedelta(minutes=30)


def half_hour_grid(start: datetime, end: datetime) -> list[datetime]:
    """UTC half-hour delivery-interval starts covering [start, end).

    Pure UTC stepping, so this is unaffected by Europe/London DST clock
    changes; only *local-time interpretation* of a UTC instant (done
    separately where decision cutoffs are computed) needs the timezone.
    """
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start/end must be timezone-aware UTC")
    grid: list[datetime] = []
    cursor = start.astimezone(timezone.utc)
    end_utc = end.astimezone(timezone.utc)
    while cursor < end_utc:
        grid.append(cursor)
        cursor += HALF_HOUR
    return grid


def hour_bucket(timestamp: datetime) -> datetime:
    """Floor a UTC timestamp to the start of its clock hour.

    Used to align WINDFOR's hourly forecast delivery intervals (verified
    live, 2026-10-25) with FUELHH's half-hourly actual delivery intervals:
    the two half-hours within a clock hour share one hourly forecast value.
    """
    return timestamp.replace(minute=0, second=0, microsecond=0)
