from datetime import datetime, timezone

import pytest

from app.analytics.backtest import run_backtest
from app.analytics.models import AnalysisMode
from app.ingestion.models import ActualGenerationRecord, ForecastGenerationRecord

RANGE_START = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
RANGE_END = datetime(2026, 1, 10, 1, 0, tzinfo=timezone.utc)  # two half-hour intervals


def _actuals():
    return [
        ActualGenerationRecord(
            delivery_start=datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
            settlement_period=1,
            generation_mw=100.0,
            source_publish_time=datetime(2026, 1, 10, 0, 30, tzinfo=timezone.utc),
        ),
        ActualGenerationRecord(
            delivery_start=datetime(2026, 1, 10, 0, 30, tzinfo=timezone.utc),
            settlement_period=2,
            generation_mw=105.0,
            source_publish_time=datetime(2026, 1, 10, 1, 0, tzinfo=timezone.utc),
        ),
    ]


def _forecasts():
    return [
        ForecastGenerationRecord(
            delivery_start=datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
            publish_time=datetime(2026, 1, 9, 10, 0, tzinfo=timezone.utc),  # before default cutoff
            generation_mw=110.0,
        ),
        ForecastGenerationRecord(
            delivery_start=datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
            publish_time=datetime(2026, 1, 9, 23, 30, tzinfo=timezone.utc),  # after default cutoff (11:00)
            generation_mw=999.0,
        ),
    ]


def test_decision_time_mode_never_leaks_future_forecast():
    result = run_backtest(_actuals(), _forecasts(), RANGE_START, RANGE_END, AnalysisMode.DECISION_TIME)
    matched = [i for i in result.intervals if i.delivery_start == RANGE_START]
    assert matched[0].forecast_generation_mw == 110.0  # not the 999.0 late-published one


def test_as_of_mode_applies_single_cutoff_to_every_interval():
    as_of = datetime(2026, 1, 9, 23, 30, tzinfo=timezone.utc)
    result = run_backtest(
        _actuals(), _forecasts(), RANGE_START, RANGE_END, AnalysisMode.AS_OF, as_of=as_of
    )
    assert result.as_of == as_of
    matched = [i for i in result.intervals if i.delivery_start == RANGE_START]
    assert matched[0].forecast_generation_mw == 999.0  # eligible once as_of allows it


def test_as_of_mode_requires_as_of_timestamp():
    with pytest.raises(ValueError):
        run_backtest(_actuals(), _forecasts(), RANGE_START, RANGE_END, AnalysisMode.AS_OF, as_of=None)


def test_decision_time_and_as_of_give_different_results_for_same_data():
    decision_time = run_backtest(_actuals(), _forecasts(), RANGE_START, RANGE_END, AnalysisMode.DECISION_TIME)
    as_of = run_backtest(
        _actuals(), _forecasts(), RANGE_START, RANGE_END, AnalysisMode.AS_OF,
        as_of=datetime(2026, 1, 9, 23, 30, tzinfo=timezone.utc),
    )
    dt_forecast = next(i.forecast_generation_mw for i in decision_time.intervals if i.delivery_start == RANGE_START)
    ao_forecast = next(i.forecast_generation_mw for i in as_of.intervals if i.delivery_start == RANGE_START)
    assert dt_forecast != ao_forecast


def test_empty_datasets_produce_valid_result_not_an_exception():
    result = run_backtest([], [], RANGE_START, RANGE_END, AnalysisMode.DECISION_TIME)
    assert result.coverage.expected_intervals == 2
    assert result.coverage.matched_intervals == 0
    assert result.accuracy.mae is None
