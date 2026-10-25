from datetime import datetime, timedelta, timezone

from app.ingestion.date_ranges import chunk_range, month_bounds


def test_month_bounds_january_2026():
    start, end = month_bounds(2026, 1)
    assert start == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert end == datetime(2026, 2, 1, tzinfo=timezone.utc)


def test_month_bounds_handles_leap_february():
    start, end = month_bounds(2024, 2)
    assert start == datetime(2024, 2, 1, tzinfo=timezone.utc)
    assert end == datetime(2024, 3, 1, tzinfo=timezone.utc)


def test_chunk_range_splits_into_bounded_spans():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 31, tzinfo=timezone.utc)
    chunks = chunk_range(start, end, timedelta(days=14))
    assert chunks[0] == (start, start + timedelta(days=14))
    assert chunks[-1][1] == end
    for chunk_start, chunk_end in chunks:
        assert chunk_end - chunk_start <= timedelta(days=14)


def test_chunk_range_empty_when_end_not_after_start():
    same = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert chunk_range(same, same, timedelta(days=1)) == []
