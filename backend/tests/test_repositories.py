"""Real-MongoDB repository tests; opt in with CLIMATE_TEST_MONGODB_URI (loopback only)."""

import asyncio
import os
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest
from pymongo import AsyncMongoClient
from pymongo.errors import WriteError

from app.ingestion import DailySeries, normalize
from app.repositories.analysis import AnalysisCacheRepository
from app.repositories.weather import WeatherRepository, source_key

URI = os.environ.get("CLIMATE_TEST_MONGODB_URI", "")
NOW = datetime(2026, 10, 14, 6, 0, tzinfo=UTC)
START, END = date(2020, 2, 27), date(2020, 3, 2)
POINT = (28.6139, 77.209)

pytestmark = pytest.mark.skipif(
    not URI.startswith(("mongodb://127.0.0.1", "mongodb://localhost")),
    reason="Set CLIMATE_TEST_MONGODB_URI to a loopback MongoDB to run repository tests",
)


def with_database(test):
    async def scenario():
        name = f"climate_hazard_test_{uuid4().hex[:10]}"
        client = AsyncMongoClient(URI, tz_aware=True, serverSelectionTimeoutMS=3000)
        try:
            await test(client[name])
        finally:
            await client.drop_database(name)
            await client.close()

    asyncio.run(scenario())


def series(provider="nasa_power", retrieved_at=NOW, point=POINT, start=START, end=END):
    records = [(start + timedelta(days=i), 20.0 + i) for i in range((end - start).days + 1)]
    records[1] = (records[1][0], None)
    if len(records) > 2:
        records += [(records[2][0], 99.0)]
    resolved = None if provider == "nasa_power" else (28.5, 77.25)
    return DailySeries(
        provider, point, resolved, 206.37, retrieved_at, normalize(records, start, end)
    )


def test_indexes_are_unique_ttl_and_idempotent_with_validation():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        await repo.ensure_schema()
        indexes = {i["name"]: i for i in await (await db["daily_weather"].list_indexes()).to_list()}
        assert indexes["source_day"]["unique"] is True
        assert indexes["source_day"]["key"] == {"source_key": 1, "date": 1}
        assert indexes["expiry"]["expireAfterSeconds"] == 0
        with pytest.raises(WriteError):
            await db["daily_weather"].insert_one(
                {"source_key": "x", "date": "2020-01-01", "quality": "bogus"}
            )
        cache = AnalysisCacheRepository(db)
        await cache.ensure_schema()
        await cache.ensure_schema()
        names = {i["name"] for i in await (await db["analysis_cache"].list_indexes()).to_list()}
        assert {"cache_key", "expiry"} <= names

    with_database(test)


def test_round_trip_preserves_quality_duplicates_and_provenance():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        original = series("open_meteo")
        await repo.save(original)
        loaded, expires_at = await repo.load("open_meteo", *POINT, START, END, NOW)
        assert loaded.days == original.days
        assert (loaded.provider, loaded.resolved, loaded.elevation_m) == (
            "open_meteo",
            (28.5, 77.25),
            206.37,
        )
        assert loaded.retrieved_at == NOW
        assert expires_at == NOW + timedelta(hours=1)
        assert [d.quality for d in loaded.days] == ["valid", "missing", "invalid", "valid", "valid"]

    with_database(test)


def test_upserts_are_idempotent_and_partial_writes_recover():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        await repo.save(series(start=START, end=date(2020, 2, 28)))
        assert await repo.load("nasa_power", *POINT, START, END, NOW) is None
        await repo.save(series())
        await repo.save(series())
        assert await db["daily_weather"].count_documents({}) == 5
        loaded, _ = await repo.load("nasa_power", *POINT, START, END, NOW)
        assert len(loaded.days) == 5

    with_database(test)


def test_expired_rows_are_ignored_before_ttl_cleanup():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        await repo.save(series(retrieved_at=NOW - timedelta(days=31)))
        assert await db["daily_weather"].count_documents({}) == 5
        assert await repo.load("nasa_power", *POINT, START, END, NOW) is None

    with_database(test)


def test_source_keys_isolate_provider_and_location_and_use_the_index():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        await repo.save(series("nasa_power"))
        assert await repo.load("open_meteo", *POINT, START, END, NOW) is None
        assert await repo.load("nasa_power", 28.6138, 77.209, START, END, NOW) is None
        assert source_key("nasa_power", *POINT) != source_key("open_meteo", *POINT)
        plan = (
            await db["daily_weather"]
            .find(
                {
                    "source_key": source_key("nasa_power", *POINT),
                    "date": {"$gte": START.isoformat(), "$lte": END.isoformat()},
                }
            )
            .explain()
        )
        assert "source_day" in str(plan["queryPlanner"]["winningPlan"])

    with_database(test)


def test_analysis_cache_respects_expiry_versions_and_replaces():
    async def test(db):
        cache = AnalysisCacheRepository(db)
        await cache.ensure_schema()
        await cache.put("k", {"value": 1}, NOW, NOW + timedelta(hours=1), "fp1")
        await cache.put("k", {"value": 2}, NOW, NOW + timedelta(hours=1), "fp2")
        assert await cache.get("k", NOW) == {"value": 2}
        assert await cache.get("k", NOW + timedelta(hours=2)) is None
        assert await db["analysis_cache"].count_documents({}) == 1
        await db["analysis_cache"].update_one(
            {"cache_key": "k"}, {"$set": {"method_version": "old"}}
        )
        assert await cache.get("k", NOW) is None

    with_database(test)
