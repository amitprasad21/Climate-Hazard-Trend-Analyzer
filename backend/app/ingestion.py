"""Provider-independent daily maximum normalization (methodology steps 1-4)."""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Literal

from app.schemas import ProviderName

NORMALIZATION_VERSION = "daily-tmax-v1"
PLAUSIBLE_TMAX_C = (-90.0, 65.0)
Quality = Literal["valid", "missing", "invalid"]


@dataclass(frozen=True)
class DailyValue:
    day: date
    tmax_c: float | None
    quality: Quality
    duplicate: bool = False


@dataclass(frozen=True)
class DailySeries:
    provider: ProviderName
    requested: tuple[float, float]
    resolved: tuple[float, float] | None
    elevation_m: float | None
    retrieved_at: datetime
    days: tuple[DailyValue, ...]


def _classify(day: date, values: list[object]) -> DailyValue:
    if not values:
        return DailyValue(day, None, "missing")
    duplicate = len(values) > 1
    # Identical duplicates collapse; conflicting ones invalidate the day (no last-write-wins).
    if any(value != values[0] for value in values[1:]):
        return DailyValue(day, None, "invalid", duplicate)
    value = values[0]
    if value is None:
        return DailyValue(day, None, "missing", duplicate)
    low, high = PLAUSIBLE_TMAX_C
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(value)
        or not low <= value <= high
    ):
        return DailyValue(day, None, "invalid", duplicate)
    return DailyValue(day, float(value), "valid", duplicate)


def normalize(
    records: Iterable[tuple[date, object]], start: date, end: date
) -> tuple[DailyValue, ...]:
    by_day: dict[date, list[object]] = {}
    for day, value in records:
        if not start <= day <= end:
            raise ValueError("Provider date outside the requested range")
        by_day.setdefault(day, []).append(value)
    span = (end - start).days + 1
    return tuple(
        _classify(day, by_day.get(day, []))
        for day in (start + timedelta(days=offset) for offset in range(span))
    )
