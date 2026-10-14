from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from app.climate import InsufficientBaseline, InsufficientData
from app.database import DatabaseUnavailable
from app.main import create_app
from app.schemas import AnalysisResponse, ErrorResponse
from app.selector import SourcesFailed
from tests.fakes import service

URL = "/api/v1/analyses/heatwaves"
BODY = {
    "hazard": "heatwave",
    "region": {"kind": "point", "label": "New Delhi", "latitude": 28.6139, "longitude": 77.209},
    "period": {"start_year": 2001, "end_year": 2010},
}


def client(db_settings, analysis):
    @asynccontextmanager
    async def factory(database, weather_settings):
        yield SimpleNamespace(analysis=analysis, regions=None)

    database = Mock(open=AsyncMock(), ping=AsyncMock(), close=AsyncMock())
    return TestClient(create_app(db_settings, lambda config: database, services_factory=factory))


def failing(exc):
    return Mock(analyze=AsyncMock(side_effect=exc))


def test_full_point_analysis_round_trip_and_cache_hit(db_settings):
    analysis, calls = service()
    with client(db_settings, analysis) as api:
        first = api.post(URL, json=BODY)
        second = api.post(URL, json={**BODY, "region": {**BODY["region"], "label": "Delhi"}})
    assert first.status_code == second.status_code == 200
    one = AnalysisResponse.model_validate(first.json())
    two = AnalysisResponse.model_validate(second.json())
    assert one.request_id == first.headers["X-Request-ID"] != two.request_id
    assert (one.cache.hit, two.cache.hit) == (False, True)
    assert two.region.label == "Delhi" and len(calls) == 1
    assert first.headers["Cache-Control"] == "no-store"
    assert first.json()["contract_version"] == "0.2"


@pytest.mark.parametrize("exc,status,code,retryable", [
    (InsufficientBaseline((1995, 1996)), 422, "INSUFFICIENT_BASELINE", False),
    (InsufficientData(), 422, "INSUFFICIENT_DATA", False),
    (SourcesFailed((("nasa_power", "invalid_response"),)), 502, "PROVIDER_ERROR", True),
    (SourcesFailed((("nasa_power", "timeout"),)), 504, "UPSTREAM_TIMEOUT", True),
    (TimeoutError(), 504, "ANALYSIS_TIMEOUT", True),
    (DatabaseUnavailable("readback_incomplete"), 503, "STORAGE_UNAVAILABLE", True),
])
def test_domain_failures_map_to_safe_typed_errors(db_settings, exc, status, code, retryable):
    with client(db_settings, failing(exc)) as api:
        response = api.post(URL, json=BODY)
    assert response.status_code == status
    error = ErrorResponse.model_validate(response.json()).error
    assert (error.code, error.retryable) == (code, retryable)
    assert error.request_id == response.headers["X-Request-ID"]
    assert "readback_incomplete" not in response.text and "Traceback" not in response.text


def test_insufficient_baseline_names_years_and_provider_errors_name_sources(db_settings):
    with client(db_settings, failing(InsufficientBaseline((1995,)))) as api:
        baseline = api.post(URL, json=BODY).json()["error"]["details"]
    with client(db_settings, failing(SourcesFailed((("nasa_power", "timeout"),)))) as api:
        provider = api.post(URL, json=BODY).json()["error"]["details"]
    assert baseline == [{"field": "baseline", "message": "Years below coverage gates: 1995"}]
    assert provider == [{"field": "source", "message": "NASA POWER: timeout"}]


def test_invalid_body_never_reaches_the_service(db_settings):
    analysis = failing(AssertionError("must not be called"))
    with client(db_settings, analysis) as api:
        response = api.post(URL, json={**BODY, "hazard": "flood"})
    assert response.status_code == 422
    analysis.analyze.assert_not_awaited()
