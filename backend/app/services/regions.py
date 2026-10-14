"""Place search with a bounded in-process cache; Open-Meteo terms gate availability."""

import asyncio
from collections import OrderedDict
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.providers.geocoding import search_places
from app.settings import WeatherSettings

CACHE_TTL = timedelta(hours=24)
CACHE_SIZE = 512
SEARCH_BUDGET_SECONDS = 15


class SearchUnavailable(Exception):
    pass


class RegionSearchService:
    def __init__(
        self,
        settings: WeatherSettings,
        http,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        lookup=search_places,
    ):
        self.settings = settings
        self.http = http
        self.clock = clock
        self.lookup = lookup
        self.cache: OrderedDict[str, tuple[datetime, list[dict]]] = OrderedDict()

    async def search(self, query: str) -> list[dict]:
        # Open-Meteo geocoding shares the free non-commercial terms of its weather API.
        if not self.settings.open_meteo_noncommercial_use:
            raise SearchUnavailable()
        text = " ".join(query.split())
        key, now = text.casefold(), self.clock()
        cached = self.cache.get(key)
        if cached and cached[0] > now:
            self.cache.move_to_end(key)
            return cached[1]
        deadline = asyncio.get_running_loop().time() + SEARCH_BUDGET_SECONDS
        results = await self.lookup(self.http, text, deadline)
        self.cache[key] = (now + CACHE_TTL, results)
        self.cache.move_to_end(key)
        while len(self.cache) > CACHE_SIZE:
            self.cache.popitem(last=False)
        return results
