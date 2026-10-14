import asyncio
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from pymongo.errors import NetworkTimeout, OperationFailure

from app.database import DatabaseUnavailable
from app.ingestion import DailySeries, normalize
from app.repositories.analysis import AnalysisCacheRepository
from app.repositories.weather import WeatherRepository

NOW = datetime(2026, 10, 14, tzinfo=UTC)


def database(collection):
    db = MagicMock()
    db.__getitem__.return_value = collection
    return db


def series(start, end):
    days = [(start.fromordinal(start.toordinal() + i), 20.0) for i in range((end - start).days + 1)]
    return DailySeries("nasa_power", (28.6, 77.2), None, None, NOW, normalize(days, start, end))


def test_a_save_is_one_bulk_write_with_one_upsert_per_year():
    collection = MagicMock(bulk_write=AsyncMock())
    repository = WeatherRepository(database(collection))
    asyncio.run(repository.save(series(date(1991, 1, 1), date(2020, 12, 31))))
    assert collection.bulk_write.await_count == 1
    operations = collection.bulk_write.await_args.args[0]
    assert len(operations) == 30
    assert collection.bulk_write.await_args.kwargs == {"ordered": False}


@pytest.mark.parametrize("failure,reason", [
    (NetworkTimeout("127.0.0.1:27017: timed out"), "network_or_availability"),
    (OperationFailure("not authorized", code=13), "authentication_or_permissions"),
])
def test_driver_errors_become_safe_storage_errors(failure, reason):
    collection = MagicMock(bulk_write=AsyncMock(side_effect=failure),
                           find_one=AsyncMock(side_effect=failure),
                           replace_one=AsyncMock(side_effect=failure))
    collection.find.return_value.sort.return_value.to_list = AsyncMock(side_effect=failure)
    weather = WeatherRepository(database(collection))
    cache = AnalysisCacheRepository(database(collection))
    calls = [
        weather.save(series(date(2000, 1, 1), date(2000, 12, 31))),
        weather.load("nasa_power", 28.6, 77.2, date(2000, 1, 1), date(2000, 12, 31), NOW),
        cache.get("k", NOW),
        cache.put("k", {}, NOW, NOW, "f"),
    ]
    for call in calls:
        with pytest.raises(DatabaseUnavailable) as error:
            asyncio.run(call)
        assert error.value.reason == reason
        assert "127.0.0.1" not in str(error.value)
