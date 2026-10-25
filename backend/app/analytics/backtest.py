from __future__ import annotations

from datetime import datetime

from app.analytics.exposure import compute_exposure
from app.analytics.matching import build_matched_intervals, compute_coverage
from app.analytics.metrics import compute_accuracy_metrics
from app.analytics.models import AnalysisMode, BacktestResult
from app.analytics.selection import default_decision_cutoff
from app.core.time_grid import half_hour_grid
from app.ingestion.models import ActualGenerationRecord, ForecastGenerationRecord


def run_backtest(
    actuals: list[ActualGenerationRecord],
    forecasts: list[ForecastGenerationRecord],
    delivery_range_start: datetime,
    delivery_range_end: datetime,
    mode: AnalysisMode,
    as_of: datetime | None = None,
) -> BacktestResult:
    """Decision-time backtest (default per-interval gate-closure cutoff) or
    as-of analysis (single fixed cutoff shared by every interval).

    These are never interchangeable: decision-time answers "what was known
    before the procurement decision for *this* interval", as-of answers
    "what was known by *this one* timestamp for every interval in range".
    """
    if mode == AnalysisMode.AS_OF:
        if as_of is None:
            raise ValueError("as_of is required when mode is AS_OF")
        cutoff_for = lambda _delivery_start: as_of  # noqa: E731
    elif mode == AnalysisMode.DECISION_TIME:
        cutoff_for = default_decision_cutoff
    else:
        raise ValueError(f"unsupported analysis mode: {mode}")

    expected_delivery_starts = half_hour_grid(delivery_range_start, delivery_range_end)
    intervals = build_matched_intervals(expected_delivery_starts, forecasts, actuals, cutoff_for)
    coverage = compute_coverage(intervals)
    accuracy = compute_accuracy_metrics(intervals)
    exposure = compute_exposure(intervals)

    return BacktestResult(
        mode=mode,
        delivery_range_start=delivery_range_start,
        delivery_range_end=delivery_range_end,
        as_of=as_of,
        intervals=intervals,
        coverage=coverage,
        accuracy=accuracy,
        exposure=exposure,
    )
