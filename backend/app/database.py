"""Async Atlas lifecycle only. No collections, indexes, or document models."""

import asyncio
from collections.abc import Callable
from contextlib import suppress

from fastapi import Request
from pymongo import AsyncMongoClient
from pymongo.errors import ConfigurationError as DriverConfigurationError
from pymongo.errors import OperationFailure, PyMongoError
from pymongo.server_api import ServerApi

from app.settings import DatabaseSettings


class DatabaseUnavailable(RuntimeError):
    def __init__(self, reason: str = "unavailable"):
        self.reason = reason
        super().__init__(f"MongoDB unavailable ({reason}); see database troubleshooting")


def safe_reason(error: Exception) -> str:
    if isinstance(error, OperationFailure) and error.code in (13, 18):
        return "authentication_or_permissions"
    if isinstance(error, DriverConfigurationError):
        return "configuration_or_dns"
    return "network_or_availability"


class Database:
    def __init__(self, settings: DatabaseSettings, client_factory: Callable = AsyncMongoClient):
        self.settings = settings
        self.client_factory = client_factory
        self.client = None
        # Driver timeouts apply per phase (DNS, selection, socket); this caps total awaited I/O.
        self.deadline_seconds = settings.mongodb_timeout_ms / 1000

    _tls_options = {
        "tls": True,
        "tlsAllowInvalidCertificates": False,
        "tlsAllowInvalidHostnames": False,
    }

    async def open(self) -> None:
        if self.client is not None:
            return
        try:
            self.client = self.client_factory(
                self.settings.mongodb_uri.get_secret_value(),
                server_api=ServerApi("1", strict=True, deprecation_errors=True),
                serverSelectionTimeoutMS=self.settings.mongodb_timeout_ms,
                connectTimeoutMS=self.settings.mongodb_timeout_ms,
                socketTimeoutMS=self.settings.mongodb_timeout_ms,
                timeoutMS=self.settings.mongodb_timeout_ms,
                waitQueueTimeoutMS=self.settings.mongodb_timeout_ms,
                maxPoolSize=10,
                minPoolSize=0,
                tz_aware=True,
                **({"tls": False} if self.settings.is_local else self._tls_options),
            )
            await self.ping()
        except BaseException as exc:
            # A half-open client is closed even when startup is cancelled.
            with suppress(DatabaseUnavailable):
                await self.close()
            if isinstance(exc, PyMongoError | ValueError):
                raise DatabaseUnavailable(safe_reason(exc)) from None
            raise

    async def ping(self) -> None:
        if self.client is None:
            raise DatabaseUnavailable()
        try:
            async with asyncio.timeout(self.deadline_seconds):
                await self.client.admin.command("ping")
        except (PyMongoError, TimeoutError) as exc:
            raise DatabaseUnavailable(safe_reason(exc)) from None

    async def close(self) -> None:
        client, self.client = self.client, None
        if client is not None:
            try:
                async with asyncio.timeout(self.deadline_seconds):
                    await client.close()
            except (PyMongoError, TimeoutError):
                raise DatabaseUnavailable("shutdown_failure") from None

    @property
    def handle(self):
        if self.client is None:
            raise DatabaseUnavailable()
        # Selecting a database handle does not create a database or collection.
        return self.client[self.settings.mongodb_database]


def get_database(request: Request):
    """FastAPI dependency for future services; never constructs a per-request client."""
    return request.app.state.database.handle
