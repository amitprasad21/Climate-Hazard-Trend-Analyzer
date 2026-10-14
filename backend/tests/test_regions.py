import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.providers.geocoding import search_places
from app.providers.transport import ProviderError, ProviderHttp
from app.schemas import ErrorResponse, RegionSearch
from app.services.regions import RegionSearchService, SearchUnavailable
from app.settings import WeatherSettings

ENABLED = WeatherSettings(open_meteo_noncommercial_use=True)
DELHI = {"id": 1261481, "name": "New Delhi", "latitude": 28.62137, "longitude": 77.2148,
         "country": "India", "country_code": "IN", "admin1": "National Capital Territory of Delhi"}


def mock_http(body, status=200, settings=ENABLED):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(status, json=body)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return ProviderHttp(client, settings, sleep=AsyncMock()), requests


def search(body, query="New Delhi", status=200):
    async def scenario():
        http, requests = mock_http(body, status)
        async with http.client:
            limit = asyncio.get_running_loop().time() + 5
            try:
                return await search_places(http, query, limit), requests
            except ProviderError as error:
                return error, requests
    return asyncio.run(scenario())


def test_request_is_fixed_and_results_are_canonical():
    results, requests = search({"results": [DELHI]})
    request = requests[0]
    assert (request.url.host, request.url.path) == ("geocoding-api.open-meteo.com", "/v1/search")
    assert dict(request.url.params) == {
        "name": "New Delhi", "count": "10", "language": "en", "format": "json"}
    assert results == [{
        "id": 1261481, "name": "New Delhi", "admin1": "National Capital Territory of Delhi",
        "country": "India", "country_code": "IN", "latitude": 28.6214, "longitude": 77.2148,
    }]


def test_no_match_is_empty_and_malformed_entries_are_skipped():
    assert search({"generationtime_ms": 0.1})[0] == []
    items = [
        {**DELHI, "admin1": None}, {**DELHI, "latitude": 91}, {**DELHI, "name": ""},
        {**DELHI, "id": "x"}, {key: value for key, value in DELHI.items() if key != "country"},
        "junk", *[{**DELHI, "id": i} for i in range(20)],
    ]
    results, _ = search({"results": items})
    assert len(results) == 10
    assert results[0]["admin1"] is None
    assert all(r["country"] for r in results)


@pytest.mark.parametrize("body,status", [({"results": "x"}, 200), ([], 200), ({}, 400)])
def test_bad_shapes_and_permanent_errors_are_invalid(body, status):
    error, requests = search(body, status=status)
    assert isinstance(error, ProviderError) and error.kind == "invalid_response"
    assert len(requests) == 1


def service(settings=ENABLED, now=datetime(2026, 10, 14, tzinfo=UTC)):
    clock = Mock(return_value=now)
    lookup = AsyncMock(return_value=[{"id": 1}])
    return RegionSearchService(settings, http=None, clock=clock, lookup=lookup), lookup, clock


def test_service_caches_normalized_queries_and_expires():
    svc, lookup, clock = service()

    async def scenario():
        first = await svc.search("  New   Delhi ")
        second = await svc.search("new delhi")
        clock.return_value += timedelta(hours=25)
        third = await svc.search("New Delhi")
        return first, second, third

    first, second, third = asyncio.run(scenario())
    assert first == second == third == [{"id": 1}]
    assert lookup.await_count == 2
    assert lookup.await_args_list[0].args[1] == "New Delhi"


def test_service_cache_is_bounded():
    svc, lookup, _ = service()

    async def scenario():
        for index in range(600):
            await svc.search(f"place {index}")
        await svc.search("place 0")

    asyncio.run(scenario())
    assert len(svc.cache) <= 512 and lookup.await_count == 601


def test_search_is_disabled_without_permitted_open_meteo_use():
    svc, lookup, _ = service(WeatherSettings())
    with pytest.raises(SearchUnavailable):
        asyncio.run(svc.search("New Delhi"))
    lookup.assert_not_awaited()


def api(db_settings, regions):
    @asynccontextmanager
    async def factory(database, weather_settings):
        yield SimpleNamespace(analysis=None, regions=regions)

    database = Mock(open=AsyncMock(), ping=AsyncMock(), close=AsyncMock())
    return TestClient(create_app(db_settings, lambda config: database, services_factory=factory))


@pytest.mark.parametrize("query,field", [("a", "q"), (" " * 5, "q"), ("x" * 101, "q"),
                                          ("ab\u0000c", "q"), (None, "q")])
def test_search_query_validation(db_settings, query, field):
    regions = Mock(search=AsyncMock())
    with api(db_settings, regions) as client:
        params = {} if query is None else {"q": query}
        response = client.get("/api/v1/regions/search", params=params)
    assert response.status_code == 422
    assert [d["field"] for d in response.json()["error"]["details"]] == [field]
    regions.search.assert_not_awaited()


@pytest.mark.parametrize("outcome,status,code", [
    ([{**DELHI, "latitude": 28.6214}], 200, None), ([], 200, None),
    (ProviderError("open_meteo", "timeout"), 504, "UPSTREAM_TIMEOUT"),
    (ProviderError("open_meteo", "invalid_response"), 502, "PROVIDER_ERROR"),
    (SearchUnavailable(), 503, "SEARCH_UNAVAILABLE"),
])
def test_search_responses(db_settings, outcome, status, code):
    behaviour = {"side_effect": outcome} if isinstance(outcome, Exception) else {
        "return_value": outcome}
    with api(db_settings, Mock(search=AsyncMock(**behaviour))) as client:
        response = client.get("/api/v1/regions/search", params={"q": "  New Delhi  "})
    assert response.status_code == status
    if code:
        assert ErrorResponse.model_validate(response.json()).error.code == code
    else:
        assert RegionSearch.model_validate(response.json()).results == [
            *(RegionSearch.model_validate({"results": outcome}).results)]
