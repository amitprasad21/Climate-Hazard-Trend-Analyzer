"""Real-MongoDB repository tests; opt in with CLIMATE_TEST_MONGODB_URI (loopback only)."""

import asyncio
import os
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import bson
import pytest
from pymongo import AsyncMongoClient
from pymongo.errors import WriteError

from app.ingestion import DailySeries, normalize
from app.repositories.analysis import AnalysisCacheRepository
from app.repositories.weather import COLLECTION, WeatherRepository, source_key

URI = os.environ.get("CLIMATE_TEST_MONGODB_URI", "")
NOW = datetime(2026, 10, 14, 6, 0, tzinfo=UTC)
START, END = date(2020, 1, 1), date(2021, 12, 31)
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


def series(provider="nasa_power", retrieved_at=NOW, point=POINT, start=START, end=END, gaps=True):
    records = [
        (start + timedelta(days=i), 20.0 + (i % 17) / 4) for i in range((end - start).days + 1)
    ]
    if gaps:
        records = [(d, None if d == date(2020, 2, 29) else v) for d, v in records]
        extra = [(date(2020, 3, 1), 20.0 + (60 % 17) / 4), (date(2021, 6, 1), 99.0)]
        records += [(d, v) for d, v in extra if start <= d <= end]
    resolved = None if provider == "nasa_power" else (28.5, 77.25)
    return DailySeries(
        provider, point, resolved, 206.37, retrieved_at, normalize(records, start, end)
    )


def test_indexes_are_unique_ttl_and_idempotent_with_validation():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        await repo.ensure_schema()
        indexes = {i["name"]: i for i in await (await db[COLLECTION].list_indexes()).to_list()}
        assert indexes["source_year"]["unique"] is True
        assert indexes["source_year"]["key"] == {"source_key": 1, "year": 1}
        assert indexes["expiry"]["expireAfterSeconds"] == 0
        with pytest.raises(WriteError):
            await db[COLLECTION].insert_one({"source_key": "x", "year": 2020, "quality": "vxq"})
        cache = AnalysisCacheRepository(db)
        await cache.ensure_schema()
        await cache.ensure_schema()
        names = {i["name"] for i in await (await db["analysis_cache"].list_indexes()).to_list()}
        assert {"cache_key", "expiry"} <= names

    with_database(test)


def test_round_trip_is_exact_compact_and_one_document_per_year():
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
        by_day = {d.day: d for d in loaded.days}
        assert by_day[date(2020, 2, 29)].quality == "missing"
        assert (by_day[date(2020, 3, 1)].quality, by_day[date(2020, 3, 1)].duplicate) == (
            "valid",
            True,
        )
        assert (by_day[date(2021, 6, 1)].quality, by_day[date(2021, 6, 1)].duplicate) == (
            "invalid",
            True,
        )
        documents = await db[COLLECTION].find({}).to_list()
        assert [d["year"] for d in sorted(documents, key=lambda d: d["year"])] == [2020, 2021]
        assert all(len(bson.encode(d)) < 8_000 for d in documents)

    with_database(test)


def test_fully_valid_years_keep_the_long_expiry():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        await repo.save(series(gaps=False))
        _, expires_at = await repo.load("nasa_power", *POINT, START, END, NOW)
        assert expires_at == NOW + timedelta(days=30)

    with_database(test)


def test_partial_years_are_rejected_before_writing():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        with pytest.raises(ValueError):
            await repo.save(series(start=date(2020, 2, 1), end=END, gaps=False))
        with pytest.raises(ValueError):
            await repo.load("nasa_power", *POINT, date(2020, 2, 1), END, NOW)
        assert await db[COLLECTION].count_documents({}) == 0

    with_database(test)


def test_upserts_are_idempotent_and_partial_writes_recover():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        await repo.save(series(end=date(2020, 12, 31)))
        assert await repo.load("nasa_power", *POINT, START, END, NOW) is None
        await repo.save(series())
        await repo.save(series())
        assert await db[COLLECTION].count_documents({}) == 2
        loaded, _ = await repo.load("nasa_power", *POINT, START, END, NOW)
        assert len(loaded.days) == 731

    with_database(test)


def test_expired_documents_are_ignored_before_ttl_cleanup():
    async def test(db):
        repo = WeatherRepository(db)
        await repo.ensure_schema()
        await repo.save(series(retrieved_at=NOW - timedelta(days=31), gaps=False))
        assert await db[COLLECTION].count_documents({}) == 2
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
            await db[COLLECTION]
            .find({"source_key": source_key("nasa_power", *POINT), "year": {"$gte": 2020}})
            .explain()
        )
        assert "source_year" in str(plan["queryPlanner"]["winningPlan"])

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
