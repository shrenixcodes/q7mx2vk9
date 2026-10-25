from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone


def month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    """UTC [start, end) bounds for a calendar month. end is exclusive."""
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    next_month = date(year, month, 1) + timedelta(days=32)
    end = datetime(next_month.year, next_month.month, 1, tzinfo=timezone.utc)
    return start, end


def chunk_range(
    start: datetime, end: datetime, max_span: timedelta
) -> list[tuple[datetime, datetime]]:
    """Split [start, end) into consecutive chunks no wider than max_span.

    Elexon's /stream endpoints accepted a full month in one call in live
    testing with no documented range cap, but request-level chunking keeps
    individual calls small and retryable instead of relying on that.
    """
    if end <= start:
        return []
    chunks: list[tuple[datetime, datetime]] = []
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + max_span, end)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end
    return chunks


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("naive datetime is ambiguous; expected tz-aware UTC")
    return value.astimezone(timezone.utc)


def day_bounds_utc(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    return start, start + timedelta(days=1)
