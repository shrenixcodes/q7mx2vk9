from __future__ import annotations

import numpy as np

from app.analytics.models import ExposureSummary, MatchedInterval


def compute_exposure(intervals: list[MatchedInterval]) -> ExposureSummary:
    """Forecast-vs-actual generation deviation -- not a procurement cost estimate.

    No price, demand, or other-generation data is in scope for this
    assignment, so these totals describe wind-only generation deviation,
    not the utility's verified additional electricity purchase or its cost.
    """
    matched = [i for i in intervals if i.error_mw is not None]
    if not matched:
        return ExposureSummary(
            sample_count=0,
            total_wind_shortfall=None,
            total_wind_surplus=None,
            mean_wind_shortfall=None,
            mean_wind_surplus=None,
        )

    shortfalls = np.array([i.wind_shortfall_mw for i in matched], dtype=float)
    surpluses = np.array([i.wind_surplus_mw for i in matched], dtype=float)

    return ExposureSummary(
        sample_count=len(matched),
        total_wind_shortfall=float(np.sum(shortfalls)),
        total_wind_surplus=float(np.sum(surpluses)),
        mean_wind_shortfall=float(np.mean(shortfalls)),
        mean_wind_surplus=float(np.mean(surpluses)),
    )
