import asyncio
import json
import time
from datetime import UTC, date, datetime
from email.utils import format_datetime

import httpx
import pytest

from app.ingestion import normalize
from app.providers.nasa_power import fetch_nasa_power
from app.providers.open_meteo import fetch_open_meteo
from app.providers.transport import MAX_RESPONSE_BYTES, ProviderError, ProviderHttp
from app.settings import WeatherSettings

START, END = date(2000, 1, 1), date(2000, 1, 3)


def nasa_body(values=None, units="C", **header):
    if values is None:
        values = {"20000101": 25.15, "20000102": -999.0, "20000103": 24.68}
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [77.209, 28.614, 206.37]},
        "properties": {"parameter": {"T2M_MAX": values}},
        "header": {
            "api": {"version": "v2.10.0", "name": "POWER Daily API"},
            "sources": ["MERRA2", "POWER"], "fill_value": -999.0, "time_standard": "UTC",
            "start": "20000101", "end": "20000103", **header,
        },
        "messages": [],
        "parameters": {"T2M_MAX": {"units": units, "longname": "T2M max"}},
    }


def era5_body(**changes):
    body = {
        "latitude": 28.625, "longitude": 77.25, "utc_offset_seconds": 0, "timezone": "GMT",
        "elevation": 213.0, "daily_units": {"time": "iso8601", "temperature_2m_max": "°C"},
        "daily": {"time": ["2000-01-01", "2000-01-02", "2000-01-03"],
                  "temperature_2m_max": [24.1, None, 23.9]},
    }
    body.update(changes)
    return body


def respond(body=None, status=200, headers=None, content=None):
    def handler(request):
        if content is not None:
            return httpx.Response(status, headers=headers, content=content)
        return httpx.Response(status, json=body, headers=headers)
    return handler


def sequence(*handlers):
    pending = list(handlers)
    return lambda request: pending.pop(0)(request)


async def never_finishes(request):
    await asyncio.Event().wait()


def run(handler, fetch=fetch_nasa_power, start=START, end=END, deadline=5.0, **settings):
    requests, sleeps = [], []

    async def recording(request):
        requests.append(request)
        response = handler(request)
        return await response if asyncio.iscoroutine(response) else response

    async def sleep(delay):
        sleeps.append(delay)

    async def scenario():
        config = WeatherSettings(**{"weather_provider_timeout_seconds": 0.2, **settings})
        async with httpx.AsyncClient(transport=httpx.MockTransport(recording)) as client:
            http = ProviderHttp(client, config, sleep=sleep, jitter=lambda: 0.5)
            limit = asyncio.get_running_loop().time() + deadline
            try:
                return await fetch(http, 28.6139, 77.209, start, end, limit)
            except ProviderError as error:
                return error

    return asyncio.run(scenario()), requests, sleeps


def test_normalize_builds_full_utc_sequence_with_explicit_quality():
    records = [
        (date(2020, 2, 28), 30.0), (date(2020, 2, 29), 65.0), (date(2020, 3, 2), None),
        (date(2020, 3, 3), 65.01), (date(2020, 3, 4), -90.01), (date(2020, 3, 5), True),
        (date(2020, 3, 6), "31"), (date(2020, 3, 7), float("nan")),
        (date(2020, 3, 8), 20.0), (date(2020, 3, 8), 20.0),
        (date(2020, 3, 9), 20.0), (date(2020, 3, 9), 21.0),
    ]
    days = normalize(records, date(2020, 2, 28), date(2020, 3, 9))
    assert [d.day.isoformat() for d in days][:3] == ["2020-02-28", "2020-02-29", "2020-03-01"]
    assert [(d.quality, d.duplicate) for d in days] == [
        ("valid", False), ("valid", False), ("missing", False), ("missing", False),
        ("invalid", False), ("invalid", False), ("invalid", False), ("invalid", False),
        ("invalid", False), ("valid", True), ("invalid", True),
    ]
    assert days[1].tmax_c == 65.0 and days[9].tmax_c == 20.0
    assert all(d.tmax_c is None for d in days if d.quality != "valid")


def test_normalize_rejects_dates_outside_request():
    with pytest.raises(ValueError):
        normalize([(date(2020, 1, 2), 1.0)], date(2020, 1, 1), date(2020, 1, 1))


def test_nasa_power_request_and_normalized_series():
    series, requests, _ = run(respond(nasa_body()))
    request = requests[0]
    assert (request.url.scheme, request.url.host) == ("https", "power.larc.nasa.gov")
    assert request.url.path == "/api/temporal/daily/point"
    assert dict(request.url.params) == {
        "parameters": "T2M_MAX", "community": "AG", "latitude": "28.6139", "longitude": "77.209",
        "start": "20000101", "end": "20000103", "format": "JSON", "time-standard": "UTC",
    }
    assert series.provider == "nasa_power"
    assert series.requested == (28.6139, 77.209) and series.resolved is None
    assert series.elevation_m == 206.37
    assert series.retrieved_at.tzinfo == UTC
    assert [(d.tmax_c, d.quality) for d in series.days] == [
        (25.15, "valid"), (None, "missing"), (24.68, "valid")]


def test_nasa_power_conflicting_duplicate_json_keys_invalidate_the_day():
    raw = (b'{"type":"Feature","geometry":{"type":"Point","coordinates":[77.209,28.614,206.37]},'
           b'"properties":{"parameter":{"T2M_MAX":{"20000101":25.0,"20000101":26.0,'
           b'"20000102":24.0,"20000102":24.0,"20000103":23.0}}},'
           b'"header":{"sources":["MERRA2","POWER"],"fill_value":-999.0,"time_standard":"UTC",'
           b'"start":"20000101","end":"20000103"},"parameters":{"T2M_MAX":{"units":"C"}}}')
    series, _, _ = run(respond(content=raw, headers={"Content-Type": "application/json"}))
    assert [(d.quality, d.duplicate) for d in series.days] == [
        ("invalid", True), ("valid", True), ("valid", False)]


@pytest.mark.parametrize("body", [
    nasa_body(sources=["GEOS-IT", "POWER"]), nasa_body(time_standard="LST"), nasa_body(units="K"),
    nasa_body(start="19991231"), nasa_body({"2000-01-01": 25.0}), nasa_body({"20000104": 25.0}),
    nasa_body({"20000230": 25.0}), {"header": {}}, [],
])
def test_nasa_power_unexpected_metadata_is_rejected_not_relabeled(body):
    error, requests, _ = run(respond(body))
    assert isinstance(error, ProviderError) and error.kind == "invalid_response"
    assert len(requests) == 1


def test_open_meteo_request_and_resolved_grid_cell():
    series, requests, _ = run(respond(era5_body()), fetch=fetch_open_meteo)
    request = requests[0]
    assert (request.url.scheme, request.url.host) == ("https", "archive-api.open-meteo.com")
    assert dict(request.url.params) == {
        "latitude": "28.6139", "longitude": "77.209", "start_date": "2000-01-01",
        "end_date": "2000-01-03", "daily": "temperature_2m_max", "models": "era5",
        "timezone": "GMT", "temperature_unit": "celsius",
    }
    assert series.provider == "open_meteo"
    assert series.resolved == (28.625, 77.25) and series.elevation_m == 213.0
    assert [d.quality for d in series.days] == ["valid", "missing", "valid"]


@pytest.mark.parametrize("changes", [
    {"utc_offset_seconds": 19800}, {"timezone": "Asia/Kolkata"},
    {"daily_units": {"time": "iso8601", "temperature_2m_max": "°F"}},
    {"daily": {"time": ["2000-01-01"], "temperature_2m_max": [1.0, 2.0]}},
    {"daily": {"time": ["20000101"], "temperature_2m_max": [1.0]}},
    {"latitude": 91.0}, {"daily": None},
])
def test_open_meteo_unexpected_shape_is_rejected(changes):
    error, _, _ = run(respond(era5_body(**changes)), fetch=fetch_open_meteo)
    assert isinstance(error, ProviderError) and error.kind == "invalid_response"


@pytest.mark.parametrize("fetch,start,end", [
    (fetch_nasa_power, date(1980, 12, 31), date(1990, 1, 1)),
    (fetch_open_meteo, date(1939, 12, 31), date(1990, 1, 1)),
    (fetch_nasa_power, END, START),
    (fetch_open_meteo, date(1940, 1, 1), date(2025, 1, 1)),
])
def test_ineligible_ranges_fail_before_any_request(fetch, start, end):
    with pytest.raises(ValueError):
        run(respond(nasa_body()), fetch=fetch, start=start, end=end)


def test_transient_status_is_retried_once_with_jittered_backoff():
    series, requests, sleeps = run(sequence(respond(status=503), respond(nasa_body())))
    assert len(requests) == 2 and series.provider == "nasa_power"
    assert sleeps == [0.375]


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_exhausted_transient_failures_are_unavailable(status):
    error, requests, sleeps = run(respond(status=status))
    assert error.kind == "unavailable" and len(requests) == 2 and len(sleeps) == 1


def test_retry_count_follows_settings():
    error, requests, _ = run(respond(status=503), weather_provider_max_retries=2)
    assert error.kind == "unavailable" and len(requests) == 3


@pytest.mark.parametrize("status,headers", [
    (400, None), (404, None), (301, {"Location": "https://evil.example/"}),
])
def test_permanent_failures_and_redirects_are_not_retried(status, headers):
    error, requests, sleeps = run(respond({"error": True, "reason": "x"}, status, headers))
    assert error.kind == "invalid_response" and len(requests) == 1 and sleeps == []


def test_retry_after_seconds_and_past_dates_are_honoured():
    past = format_datetime(datetime(2000, 1, 1, tzinfo=UTC), usegmt=True)
    _, _, sleeps = run(sequence(respond(status=429, headers={"Retry-After": "2"}),
                                respond(status=429, headers={"Retry-After": past}),
                                respond(nasa_body())), weather_provider_max_retries=2)
    assert sleeps == [2.0, 0.0]


@pytest.mark.parametrize("value", ["3600", "1.5", "soon"])
def test_retry_after_beyond_budget_or_invalid(value):
    error, requests, sleeps = run(respond(status=429, headers={"Retry-After": value}))
    if value == "3600":
        assert error.kind == "unavailable" and len(requests) == 1 and sleeps == []
    else:
        assert len(requests) == 2 and sleeps == [0.375]


def test_stalled_attempts_time_out_within_bounds():
    started = time.monotonic()
    error, requests, _ = run(never_finishes)
    assert error.kind == "timeout" and len(requests) == 2
    assert time.monotonic() - started < 2


def test_total_deadline_caps_attempt_timeout():
    started = time.monotonic()
    error, requests, sleeps = run(
        never_finishes, deadline=0.15, weather_provider_timeout_seconds=10)
    assert error.kind == "timeout" and len(requests) == 1 and sleeps == []
    assert time.monotonic() - started < 1.5


def test_network_errors_are_retried_then_unavailable():
    def refuse(request):
        raise httpx.ConnectError("connection refused to secret-host", request=request)
    error, requests, _ = run(refuse)
    assert error.kind == "unavailable" and len(requests) == 2
    assert "secret-host" not in str(error) and error.__suppress_context__


def test_declared_oversize_body_is_rejected_without_retry():
    headers = {"Content-Length": str(MAX_RESPONSE_BYTES + 1), "Content-Type": "application/json"}
    error, requests, _ = run(respond(content=json.dumps(nasa_body()).encode(), headers=headers))
    assert error.kind == "invalid_response" and len(requests) == 1


def test_streamed_oversize_body_is_cut_off_and_closed():
    closed = []

    async def chunks():
        try:
            yield json.dumps(nasa_body()).encode()
            for _ in range(6):
                yield b" " * (1024 * 1024)
        finally:
            closed.append(True)

    error, _, _ = run(respond(content=chunks(), headers={"Content-Type": "application/json"}))
    assert error.kind == "invalid_response" and closed == [True]


@pytest.mark.parametrize("content,content_type", [
    (json.dumps(nasa_body()).encode(), "text/html"), (b"{not json", "application/json"),
    (b"[" * 100_000, "application/json"),
], ids=["valid-json-wrong-type", "malformed", "deeply-nested"])
def test_non_json_bodies_are_invalid(content, content_type):
    error, _, _ = run(respond(content=content, headers={"Content-Type": content_type}))
    assert error.kind == "invalid_response"


def test_cancellation_propagates_and_releases_the_request():
    released = []

    async def stalled(request):
        try:
            await asyncio.Event().wait()
        finally:
            released.append(True)

    async def scenario():
        config = WeatherSettings(weather_provider_timeout_seconds=5)
        transport = httpx.MockTransport(stalled)
        async with httpx.AsyncClient(transport=transport) as client:
            http = ProviderHttp(client, config)
            limit = asyncio.get_running_loop().time() + 5
            task = asyncio.create_task(fetch_nasa_power(http, 28.6139, 77.209, START, END, limit))
            await asyncio.sleep(0.05)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
    asyncio.run(scenario())
    assert released == [True]


def test_error_text_never_contains_request_details():
    error, _, _ = run(respond(status=404))
    assert str(error) == "nasa_power: invalid_response"
