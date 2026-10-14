"""Open-Meteo geocoding adapter: bounded, disambiguated place search."""

import math

from app.providers.transport import ProviderError, ProviderHttp

PROVIDER = "open_meteo"
MAX_RESULTS = 10
MAX_TEXT = 200


def _text(value) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing text")
    return value.strip()[:MAX_TEXT]


def _coordinate(value, limit: float) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError("Malformed coordinate")
    if not math.isfinite(value) or abs(value) > limit:
        raise ValueError("Coordinate out of range")
    return round(value, 4) + 0.0


def _entry(item) -> dict:
    if (
        not isinstance(item, dict)
        or isinstance(item["id"], bool)
        or not isinstance(item["id"], int)
    ):
        raise ValueError("Malformed place")
    code = _text(item["country_code"])
    if len(code) != 2 or not code.isalpha():
        raise ValueError("Malformed country code")
    admin1 = item.get("admin1")
    return {
        "id": item["id"],
        "name": _text(item["name"]),
        "admin1": _text(admin1) if isinstance(admin1, str) and admin1.strip() else None,
        "country": _text(item["country"]),
        "country_code": code.upper(),
        "latitude": _coordinate(item["latitude"], 90),
        "longitude": _coordinate(item["longitude"], 180),
    }


async def search_places(http: ProviderHttp, query: str, deadline: float) -> list[dict]:
    params = {"name": query, "count": MAX_RESULTS, "language": "en", "format": "json"}
    data = await http.get_json(PROVIDER, http.settings.open_meteo_geocoding_url, params, deadline)
    try:
        items = data.get("results", [])
        if not isinstance(items, list):
            raise ValueError("Malformed results")
    except (AttributeError, ValueError):
        raise ProviderError(PROVIDER, "invalid_response") from None
    results = []
    for item in items:
        try:
            results.append(_entry(item))
        except (KeyError, TypeError, ValueError):
            continue
        if len(results) == MAX_RESULTS:
            break
    return results
