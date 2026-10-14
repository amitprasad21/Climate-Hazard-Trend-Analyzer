"""Bounded provider HTTP: fixed URLs, retries, deadlines and a streamed size cap."""

import asyncio
import json
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from email.utils import parsedate_to_datetime
from typing import Any, Literal

import httpx

from app.schemas import SOURCE_PROFILES, ProviderName
from app.settings import WeatherSettings

MAX_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_SPAN_DAYS = 80 * 366
INITIAL_BACKOFF_SECONDS = 0.5
TRANSIENT_STATUSES = {429, 500, 502, 503, 504}
FailureKind = Literal["timeout", "unavailable", "invalid_response"]


class ProviderError(RuntimeError):
    def __init__(self, provider: ProviderName, kind: FailureKind):
        self.provider = provider
        self.kind = kind
        super().__init__(f"{provider}: {kind}")


class _Pairs(dict):
    # Keeps every key/value pair so duplicate provider dates stay detectable.
    def __init__(self, pairs: list[tuple[str, Any]]):
        super().__init__(pairs)
        self.pairs = pairs


def require_supported_range(provider: ProviderName, start: date, end: date) -> None:
    if start > end or (end - start).days >= MAX_SPAN_DAYS:
        raise ValueError("Requested provider range is reversed or too long")
    if start.year < SOURCE_PROFILES[provider].first_year:
        raise ValueError("Requested range starts before the provider's coverage")


def _retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    if value.isascii() and value.isdigit():
        return float(value)
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None
    if when.tzinfo is None:
        return None
    return max(0.0, (when - datetime.now(UTC)).total_seconds())


@dataclass(frozen=True)
class ProviderHttp:
    client: httpx.AsyncClient
    settings: WeatherSettings
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep
    jitter: Callable[[], float] = random.random

    async def _read(self, provider: ProviderName, url: str, params: dict) -> tuple[int, Any, bytes]:
        timeout = self.settings.weather_provider_timeout_seconds
        async with self.client.stream(
            "GET", url, params=params, follow_redirects=False, timeout=timeout
        ) as response:
            if response.status_code != 200:
                return response.status_code, response.headers, b""
            media_type = response.headers.get("Content-Type", "").split(";")[0].strip()
            declared = response.headers.get("Content-Length", "")
            if media_type != "application/json" or (
                declared.isdigit() and int(declared) > MAX_RESPONSE_BYTES
            ):
                raise ProviderError(provider, "invalid_response")
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body += chunk
                if len(body) > MAX_RESPONSE_BYTES:
                    raise ProviderError(provider, "invalid_response")
            return 200, response.headers, bytes(body)

    async def get_json(
        self, provider: ProviderName, url: str, params: dict, deadline: float
    ) -> Any:
        loop = asyncio.get_running_loop()
        attempts = self.settings.weather_provider_max_retries + 1
        for attempt in range(attempts):
            failure: FailureKind = "unavailable"
            retry_after = None
            attempt_deadline = loop.time() + self.settings.weather_provider_timeout_seconds
            try:
                async with asyncio.timeout_at(min(deadline, attempt_deadline)):
                    status, headers, body = await self._read(provider, url, params)
            except (TimeoutError, httpx.TimeoutException):
                failure = "timeout"
            except httpx.TransportError:
                pass
            else:
                if status == 200:
                    try:
                        return json.loads(body, object_pairs_hook=_Pairs)
                    except (ValueError, RecursionError):
                        raise ProviderError(provider, "invalid_response") from None
                if status not in TRANSIENT_STATUSES:
                    raise ProviderError(provider, "invalid_response")
                retry_after = _retry_after(headers.get("Retry-After"))
            if attempt + 1 == attempts:
                raise ProviderError(provider, failure) from None
            base = INITIAL_BACKOFF_SECONDS * 2**attempt
            delay = retry_after if retry_after is not None else base / 2 * (1 + self.jitter())
            if loop.time() + delay >= deadline:
                raise ProviderError(provider, failure) from None
            await self.sleep(delay)
        raise AssertionError("unreachable")
