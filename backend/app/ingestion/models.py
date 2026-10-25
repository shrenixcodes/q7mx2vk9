from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, field_validator


class ActualGenerationRecord(BaseModel):
    """A normalized FUELHH record, already filtered to fuelType == WIND."""

    delivery_start: datetime
    settlement_period: int
    generation_mw: float
    source_publish_time: datetime

    @field_validator("delivery_start", "source_publish_time")
    @classmethod
    def _require_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return value.astimezone(timezone.utc)


class ForecastGenerationRecord(BaseModel):
    """A normalized WINDFOR record. publishTime identifies the vintage."""

    delivery_start: datetime
    publish_time: datetime
    generation_mw: float

    @field_validator("delivery_start", "publish_time")
    @classmethod
    def _require_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return value.astimezone(timezone.utc)


class RejectedRecord(BaseModel):
    """A raw record that failed normalization, kept for diagnostics."""

    raw: dict
    reason: str
