"""Open-Meteo archive ERA5 daily temperature_2m_max (Celsius, GMT) adapter."""

import math
import re
from datetime import UTC, date, datetime

from app.ingestion import DailySeries, normalize
from app.providers.transport import ProviderError, ProviderHttp, require_supported_range

PROVIDER = "open_meteo"
ISO_DAY = re.compile(r"\d{4}-\d{2}-\d{2}")


def _day(value: str) -> date:
    if not ISO_DAY.fullmatch(value):
        raise ValueError("Malformed Open-Meteo date")
    return date.fromisoformat(value)


def _coordinate(value, limit: float) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError("Malformed coordinate")
    if not math.isfinite(value) or abs(value) > limit:
        raise ValueError("Coordinate out of range")
    return float(value)


def _parse(data, start: date, end: date):
    if (
        data["utc_offset_seconds"] != 0
        or data["timezone"] not in ("GMT", "UTC")
        or data["daily_units"]["temperature_2m_max"] != "°C"
    ):
        raise ValueError("Unexpected Open-Meteo metadata")
    times, values = data["daily"]["time"], data["daily"]["temperature_2m_max"]
    if not isinstance(times, list) or not isinstance(values, list):
        raise ValueError("Malformed Open-Meteo arrays")
    records = [(_day(t), value) for t, value in zip(times, values, strict=True)]
    resolved = (_coordinate(data["latitude"], 90), _coordinate(data["longitude"], 180))
    elevation = data.get("elevation")
    finite = isinstance(elevation, int | float) and math.isfinite(elevation)
    return resolved, (float(elevation) if finite else None), normalize(records, start, end)


async def fetch_open_meteo(
    http: ProviderHttp, latitude: float, longitude: float, start: date, end: date, deadline: float
) -> DailySeries:
    require_supported_range(PROVIDER, start, end)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "temperature_2m_max",
        "models": http.settings.open_meteo_model,
        "timezone": "GMT",
        "temperature_unit": "celsius",
    }
    data = await http.get_json(PROVIDER, http.settings.open_meteo_base_url, params, deadline)
    retrieved_at = datetime.now(UTC)
    try:
        resolved, elevation, days = _parse(data, start, end)
    except (KeyError, IndexError, TypeError, ValueError, AttributeError):
        raise ProviderError(PROVIDER, "invalid_response") from None
    return DailySeries(PROVIDER, (latitude, longitude), resolved, elevation, retrieved_at, days)
