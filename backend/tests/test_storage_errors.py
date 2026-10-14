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


def test_saves_are_written_in_one_year_batches():
    collection = MagicMock(bulk_write=AsyncMock())
    repository = WeatherRepository(database(collection))
    asyncio.run(repository.save(series(date(1991, 1, 1), date(1993, 12, 31))))
    sizes = [len(call.args[0]) for call in collection.bulk_write.await_args_list]
    assert sizes == [365, 366, 365]
    assert all(call.kwargs == {"ordered": False} for call in collection.bulk_write.await_args_list)


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
        weather.save(series(date(2000, 1, 1), date(2000, 1, 3))),
        weather.load("nasa_power", 28.6, 77.2, date(2000, 1, 1), date(2000, 1, 3), NOW),
        cache.get("k", NOW),
        cache.put("k", {}, NOW, NOW, "f"),
    ]
    for call in calls:
        with pytest.raises(DatabaseUnavailable) as error:
            asyncio.run(call)
        assert error.value.reason == reason
        assert "127.0.0.1" not in str(error.value)
