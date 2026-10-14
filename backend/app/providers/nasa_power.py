"""NASA POWER daily T2M_MAX (MERRA-2, UTC) adapter."""

import math
import re
from datetime import UTC, date, datetime

from app.ingestion import DailySeries, normalize
from app.providers.transport import ProviderError, ProviderHttp, require_supported_range

PROVIDER = "nasa_power"
DAY_KEY = re.compile(r"\d{8}")


def _day(key: str) -> date:
    if not DAY_KEY.fullmatch(key):
        raise ValueError("Malformed NASA POWER date")
    return date(int(key[:4]), int(key[4:6]), int(key[6:]))


def _parse(data, start: date, end: date) -> tuple[float | None, tuple]:
    header = data["header"]
    fill = header["fill_value"]
    if (
        header["time_standard"] != "UTC"
        or "MERRA2" not in header["sources"]
        or (header["start"], header["end"]) != (f"{start:%Y%m%d}", f"{end:%Y%m%d}")
        or data["parameters"]["T2M_MAX"]["units"] != "C"
        or isinstance(fill, bool)
        or not isinstance(fill, int | float)
    ):
        raise ValueError("Unexpected NASA POWER metadata")
    values = data["properties"]["parameter"]["T2M_MAX"]
    records = [(_day(key), None if value == fill else value) for key, value in values.pairs]
    elevation = data["geometry"]["coordinates"][2]
    finite = isinstance(elevation, int | float) and math.isfinite(elevation)
    return (float(elevation) if finite else None), normalize(records, start, end)


async def fetch_nasa_power(
    http: ProviderHttp, latitude: float, longitude: float, start: date, end: date, deadline: float
) -> DailySeries:
    require_supported_range(PROVIDER, start, end)
    params = {
        "parameters": "T2M_MAX",
        "community": "AG",
        "latitude": latitude,
        "longitude": longitude,
        "start": f"{start:%Y%m%d}",
        "end": f"{end:%Y%m%d}",
        "format": "JSON",
        "time-standard": http.settings.nasa_power_time_standard,
    }
    data = await http.get_json(PROVIDER, http.settings.nasa_power_base_url, params, deadline)
    retrieved_at = datetime.now(UTC)
    try:
        elevation, days = _parse(data, start, end)
    except (KeyError, IndexError, TypeError, ValueError, AttributeError):
        raise ProviderError(PROVIDER, "invalid_response") from None
    # POWER echoes the requested point instead of naming a grid cell, so resolved stays unknown.
    return DailySeries(PROVIDER, (latitude, longitude), None, elevation, retrieved_at, days)
