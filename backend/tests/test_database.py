import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import dns.asyncresolver
import pytest
from pymongo.errors import ConfigurationError, OperationFailure, ServerSelectionTimeoutError

from app.database import Database, DatabaseUnavailable, get_database


def fake_client():
    client = Mock()
    client.admin.command = AsyncMock()
    client.close = AsyncMock()
    client.__getitem__ = Mock(return_value=object())
    return client


def test_one_client_reused_and_closed_idempotently(db_settings):
    async def scenario():
        client = fake_client()
        factory = Mock(return_value=client)
        database = Database(db_settings, factory)
        await database.open()
        await database.open()
        handle = database.handle
        assert get_database(SimpleNamespace(app=SimpleNamespace(
            state=SimpleNamespace(database=database)
        ))) is handle
        await database.ping()
        await database.close()
        await database.close()
        factory.assert_called_once()
        options = factory.call_args.kwargs
        assert options["tls"] is True
        assert options["tlsAllowInvalidCertificates"] is False
        assert options["tlsAllowInvalidHostnames"] is False
        assert options["maxPoolSize"] == 10
        assert options["server_api"].strict is True
        for option in ("serverSelectionTimeoutMS", "connectTimeoutMS", "socketTimeoutMS",
                       "timeoutMS", "waitQueueTimeoutMS"):
            assert options[option] == 100
        client.close.assert_awaited_once()
        with pytest.raises(DatabaseUnavailable):
            _ = database.handle
        with pytest.raises(DatabaseUnavailable):
            await database.ping()
    asyncio.run(scenario())


@pytest.mark.parametrize("failure,reason", [
    (OperationFailure("sensitive-uri", code=18), "authentication_or_permissions"),
    (OperationFailure("sensitive-uri", code=13), "authentication_or_permissions"),
    (ServerSelectionTimeoutError("sensitive-uri"), "network_or_availability"),
    (ConfigurationError("sensitive-uri"), "configuration_or_dns"),
])
def test_failed_startup_closes_and_sanitizes(db_settings, failure, reason):
    async def scenario():
        client = fake_client()
        client.admin.command.side_effect = failure
        database = Database(db_settings, Mock(return_value=client))
        with pytest.raises(DatabaseUnavailable) as error:
            await database.open()
        assert error.value.reason == reason
        assert "sensitive-uri" not in str(error.value)
        assert error.value.__suppress_context__ is True
        assert database.client is None
        client.close.assert_awaited_once()
    asyncio.run(scenario())


def test_constructor_failure_is_safe(db_settings):
    async def scenario():
        database = Database(db_settings, Mock(side_effect=ConfigurationError("sensitive-uri")))
        with pytest.raises(DatabaseUnavailable, match="configuration_or_dns"):
            await database.open()
        assert database.client is None
    asyncio.run(scenario())


async def never_finishes(*args, **kwargs):
    await asyncio.Event().wait()


@pytest.mark.parametrize("operation", ["ping", "close"])
def test_elapsed_deadline(db_settings, operation):
    async def scenario():
        client = fake_client()
        database = Database(db_settings, Mock(return_value=client))
        await database.open()
        if operation == "ping":
            client.admin.command.side_effect = never_finishes
        else:
            client.close.side_effect = never_finishes
        start = asyncio.get_running_loop().time()
        with pytest.raises(DatabaseUnavailable):
            async with asyncio.timeout(1):  # Independent guard for a missing application deadline.
                await getattr(database, operation)()
        assert asyncio.get_running_loop().time() - start < 0.75
        await database.close()
    asyncio.run(scenario())


def test_cancelled_startup_closes_without_swallowing_cancellation(db_settings):
    async def scenario():
        entered = asyncio.Event()
        async def ping(*args):
            entered.set()
            await never_finishes()
        client = fake_client()
        client.admin.command.side_effect = ping
        database = Database(db_settings, Mock(return_value=client))
        task = asyncio.create_task(database.open())
        await entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        client.close.assert_awaited_once()
        assert database.client is None
    asyncio.run(scenario())


def test_actual_driver_dns_is_cancellable_and_does_not_block_loop(db_settings, monkeypatch):
    async def scenario():
        entered = asyncio.Event()
        cancelled = asyncio.Event()
        ticks = 0
        async def stalled_dns(*args, **kwargs):
            entered.set()
            try:
                await never_finishes()
            finally:
                cancelled.set()
        async def heartbeat():
            nonlocal ticks
            while not cancelled.is_set():
                ticks += 1
                await asyncio.sleep(0.005)
        monkeypatch.setattr(dns.asyncresolver, "resolve", stalled_dns)
        database = Database(db_settings)  # Real installed PyMongo, mocked DNS only.
        pulse = asyncio.create_task(heartbeat())
        try:
            with pytest.raises(DatabaseUnavailable):
                async with asyncio.timeout(1):
                    await database.open()
            assert entered.is_set() and cancelled.is_set()
            assert ticks > 1
            assert database.client is None
        finally:
            pulse.cancel()
            await asyncio.gather(pulse, return_exceptions=True)
            await database.close()
    asyncio.run(scenario())
