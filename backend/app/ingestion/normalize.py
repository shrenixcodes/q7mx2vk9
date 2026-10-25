from __future__ import annotations

import logging
from datetime import datetime

from pydantic import ValidationError

from app.ingestion.models import ActualGenerationRecord, ForecastGenerationRecord, RejectedRecord

logger = logging.getLogger("windlens.ingestion.normalize")


def _parse_timestamp(raw: object) -> datetime:
    if not isinstance(raw, str):
        raise ValueError(f"timestamp must be a string, got {type(raw).__name__}")
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def _parse_generation(raw: object) -> float:
    if isinstance(raw, bool) or not isinstance(raw, (int, float, str)):
        raise ValueError(f"generation must be numeric, got {type(raw).__name__}")
    return float(raw)


def normalize_actual_generation(
    raw_records: list[dict],
) -> tuple[list[ActualGenerationRecord], list[RejectedRecord]]:
    """Normalize FUELHH records: filter to WIND, parse timestamps/generation.

    Dedup policy: FUELHH re-publishes settlement periods as figures are
    revised, so (delivery_start, settlement_period) is not unique across the
    raw feed. We keep the record with the latest source_publish_time per key
    -- the most recently published figure for that interval -- and treat
    this as a documented "latest revision wins" policy, not silent data loss.
    """
    accepted: dict[tuple[datetime, int], ActualGenerationRecord] = {}
    rejected: list[RejectedRecord] = []

    for raw in raw_records:
        if raw.get("fuelType") != "WIND":
            continue
        try:
            delivery_start = _parse_timestamp(raw.get("startTime"))
            publish_time = _parse_timestamp(raw.get("publishTime"))
            generation_mw = _parse_generation(raw.get("generation"))
            record = ActualGenerationRecord(
                delivery_start=delivery_start,
                settlement_period=int(raw["settlementPeriod"]),
                generation_mw=generation_mw,
                source_publish_time=publish_time,
            )
        except (ValueError, KeyError, TypeError, ValidationError) as exc:
            rejected.append(RejectedRecord(raw=raw, reason=str(exc)))
            continue

        key = (record.delivery_start, record.settlement_period)
        existing = accepted.get(key)
        if existing is None or record.source_publish_time > existing.source_publish_time:
            accepted[key] = record

    result = sorted(accepted.values(), key=lambda r: r.delivery_start)
    wind_raw_count = sum(1 for r in raw_records if r.get("fuelType") == "WIND")
    logger.info(
        "normalized_actuals wind_raw=%d accepted=%d rejected=%d duplicates_resolved=%d",
        wind_raw_count,
        len(result),
        len(rejected),
        wind_raw_count - len(result) - len(rejected),
    )
    return result, rejected


def normalize_forecast_generation(
    raw_records: list[dict],
) -> tuple[list[ForecastGenerationRecord], list[RejectedRecord]]:
    """Normalize WINDFOR records, preserving every distinct publish vintage.

    Dedup policy: only exact duplicate (delivery_start, publish_time,
    generation_mw) rows are collapsed -- these arise from overlapping
    date-range requests, not genuinely distinct forecasts. Two records that
    share a delivery_start but differ in publish_time are different
    forecast vintages and are both kept.
    """
    seen: dict[tuple[datetime, datetime], ForecastGenerationRecord] = {}
    rejected: list[RejectedRecord] = []

    for raw in raw_records:
        try:
            delivery_start = _parse_timestamp(raw.get("startTime"))
            publish_time = _parse_timestamp(raw.get("publishTime"))
            generation_mw = _parse_generation(raw.get("generation"))
            record = ForecastGenerationRecord(
                delivery_start=delivery_start,
                publish_time=publish_time,
                generation_mw=generation_mw,
            )
        except (ValueError, KeyError, TypeError, ValidationError) as exc:
            rejected.append(RejectedRecord(raw=raw, reason=str(exc)))
            continue

        key = (record.delivery_start, record.publish_time)
        if key in seen and seen[key].generation_mw != record.generation_mw:
            logger.warning(
                "forecast_conflicting_duplicate delivery_start=%s publish_time=%s kept=%s dropped=%s",
                record.delivery_start,
                record.publish_time,
                seen[key].generation_mw,
                record.generation_mw,
            )
            continue
        seen[key] = record

    result = sorted(seen.values(), key=lambda r: (r.delivery_start, r.publish_time))
    logger.info(
        "normalized_forecasts accepted=%d rejected=%d",
        len(result),
        len(rejected),
    )
    return result, rejected
