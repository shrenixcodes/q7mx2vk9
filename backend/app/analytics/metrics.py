from __future__ import annotations

import numpy as np

from app.analytics.models import AccuracyMetrics, MatchedInterval

# Intervals with actual generation below this are excluded from MAPE: a
# small denominator makes percentage error numerically meaningless, not
# because the observation itself is invalid. MAE/RMSE/bias are unaffected.
MAPE_MIN_ACTUAL_MW = 50.0


def compute_accuracy_metrics(intervals: list[MatchedInterval]) -> AccuracyMetrics:
    matched = [i for i in intervals if i.error_mw is not None]
    if not matched:
        return AccuracyMetrics(
            sample_count=0, mae=None, rmse=None, bias=None, mape_percent=None,
            mape_excluded_low_actual_count=0,
        )

    errors = np.array([i.error_mw for i in matched], dtype=float)
    actuals = np.array([i.actual_generation_mw for i in matched], dtype=float)

    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(np.square(errors))))
    bias = float(np.mean(errors))

    mape_mask = actuals >= MAPE_MIN_ACTUAL_MW
    excluded = int((~mape_mask).sum())
    if mape_mask.any():
        mape = float(np.mean(np.abs(errors[mape_mask] / actuals[mape_mask])) * 100)
    else:
        mape = None

    return AccuracyMetrics(
        sample_count=len(matched),
        mae=mae,
        rmse=rmse,
        bias=bias,
        mape_percent=mape,
        mape_excluded_low_actual_count=excluded,
    )
