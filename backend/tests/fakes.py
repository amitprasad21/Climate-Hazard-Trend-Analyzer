"""Shared synthetic fixtures for service and API tests; never used by the application."""

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

from app.ingestion import DailySeries, normalize
from app.services.analysis import AnalysisService
from app.settings import WeatherSettings

NOW = datetime(2026, 10, 14, 6, 0, tzinfo=UTC)


@asynccontextmanager
async def no_services(database, weather_settings):
    yield None


def synthetic(provider, latitude, longitude, start, end, missing=()):
    """Synthetic test fixture: 20 °C everywhere, a 25 °C 3-day July run each year from 2001."""
    records = []
    current = start
    while current <= end:
        hot = current.year >= 2001 and current.month == 7 and current.day <= 3
        records.append((current, None if current in missing else 25.0 if hot else 20.0))
        current += timedelta(days=1)
    resolved = None if provider == "nasa_power" else (28.5, 77.25)
    return DailySeries(provider, (latitude, longitude), resolved, 206.0, NOW,
                       normalize(records, start, end))


class FakeWeather:
    def __init__(self, readback=True):
        self.rows, self.readback, self.saves = {}, readback, 0

    async def load(self, provider, latitude, longitude, start, end, now):
        stored = self.rows.get((provider, latitude, longitude, start, end))
        if stored is None:
            return None
        series, expires_at = stored
        return (series, expires_at) if expires_at > now else None

    async def save(self, series):
        self.saves += 1
        if self.readback:
            missing = any(day.quality != "valid" for day in series.days)
            ttl = timedelta(hours=1) if missing else timedelta(days=30)
            start, end = series.days[0].day, series.days[-1].day
            self.rows[(series.provider, *series.requested, start, end)] = (
                series, series.retrieved_at + ttl)


class FakeCache:
    def __init__(self):
        self.rows, self.puts = {}, 0

    async def get(self, key, now):
        stored = self.rows.get(key)
        return stored[0] if stored and stored[1] > now else None

    async def put(self, key, result, created_at, expires_at, fingerprint):
        self.puts += 1
        assert created_at == NOW and len(fingerprint) == 64
        self.rows[key] = (result, expires_at)


def service(settings=None, fetchers=None, weather=None, cache=None, clock=lambda: NOW):
    calls = []

    def recording(provider, behaviour=None):
        async def fetch(http, latitude, longitude, start, end, deadline):
            calls.append((provider, start, end))
            await asyncio.sleep(0)
            if isinstance(behaviour, BaseException):
                raise behaviour
            return synthetic(provider, latitude, longitude, start, end, behaviour or ())
        return fetch

    fetchers = fetchers or {}
    built = AnalysisService(
        settings or WeatherSettings(),
        http=None,
        weather=weather or FakeWeather(),
        cache=cache or FakeCache(),
        clock=clock,
        fetchers={p: recording(p, fetchers.get(p)) for p in ("nasa_power", "open_meteo")},
    )
    return built, calls


