import math
from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import create_app
from app.schemas import (
    AnalysisRequest,
    ErrorResponse,
    Source,
    UnsupportedRequest,
    ensure_supported,
    last_complete_year,
)

TODAY = date(2026, 10, 14)
DELETE = object()
PROBE = "/test/analyses"


def payload(path=None, value=None):
    body = {
        "hazard": "heatwave",
        "region": {"kind": "point", "label": "New Delhi", "latitude": 28.6139, "longitude": 77.209},
        "period": {"start_year": 1990, "end_year": 2020},
    }
    if path:
        *parents, key = path.split(".")
        target = body
        for name in parents:
            target = target[name]
        if value is DELETE:
            del target[key]
        else:
            target[key] = value
    return body


def parse(path=None, value=None):
    return AnalysisRequest.model_validate(payload(path, value))


def bbox():
    return {"kind": "bbox", "label": "Box", "south": 28, "west": 77, "north": 29, "east": 78}


@pytest.fixture
def client(db_settings):
    database = Mock(open=AsyncMock(), ping=AsyncMock(), close=AsyncMock())
    app = create_app(db_settings, lambda config: database)

    # Test-only route; the public analysis endpoint belongs to BE-007.
    @app.post(PROBE)
    async def probe(body: AnalysisRequest):
        ensure_supported(body, TODAY)
        return body.model_dump()

    with TestClient(app) as test_client:
        yield test_client


def error_of(response, status, code):
    assert response.status_code == status
    assert response.headers["Cache-Control"] == "no-store"
    error = ErrorResponse.model_validate(response.json()).error
    assert error.code == code
    assert error.request_id == response.headers["X-Request-ID"]
    return error


def test_point_request_is_canonicalized():
    body = payload()
    body["region"].update(label="  New Delhi  ", latitude=-0.00004, longitude=77)
    region = AnalysisRequest.model_validate(body).region
    assert region.label == "New Delhi"
    assert region.latitude == 0.0 and math.copysign(1.0, region.latitude) == 1.0
    assert region.longitude == 77.0
    assert parse("region.latitude", 28.61394999).region.latitude == 28.6139
    assert parse("region.latitude", 89.99996).region.latitude == 90.0
    assert parse("region.label", "x" * 120).region.label == "x" * 120


@pytest.mark.parametrize("path,value", [
    ("region.latitude", 90.0001), ("region.latitude", float("nan")),
    ("region.longitude", float("inf")), ("region.longitude", -180.5),
    ("region.latitude", "28.6"), ("region.longitude", True),
    ("region.label", "   "), ("region.label", "x" * 121), ("region.label", "a\nb"),
    ("region.label", "a\u0085b"), ("region.label", "\ud800"),
    ("region.extra", 1), ("region.kind", "polygon"), ("region.kind", DELETE),
    ("hazard", "flood"), ("period", DELETE), ("period.start_year", 1990.0),
    ("period.end_year", "2020"), ("period.start_year", 2021), ("unexpected", True),
])
def test_invalid_input_is_rejected(path, value):
    with pytest.raises(ValidationError):
        parse(path, value)


@pytest.mark.parametrize("today,year", [
    (date(2026, 10, 14), 2025), (date(2027, 1, 7), 2026), (date(2027, 1, 6), 2025),
])
def test_last_complete_year_keeps_seven_day_availability_margin(today, year):
    assert last_complete_year(today) == year


@pytest.mark.parametrize("start,end", [(1940, 1940), (1976, 2025)])
def test_supported_period_boundaries(start, end):
    ensure_supported(parse("period", {"start_year": start, "end_year": end}), TODAY)


@pytest.mark.parametrize("start,end,field", [
    (1939, 1950, "period.start_year"), (2000, 2026, "period.end_year"), (1975, 2025, "period"),
])
def test_unsupported_period(start, end, field):
    request = parse("period", {"start_year": start, "end_year": end})
    with pytest.raises(UnsupportedRequest) as error:
        ensure_supported(request, TODAY)
    assert error.value.code == "UNSUPPORTED_PERIOD"
    assert [detail.field for detail in error.value.details] == [field]


def test_bbox_is_explicitly_unsupported_not_a_point():
    request = parse("region", bbox())
    assert request.region.kind == "bbox"
    with pytest.raises(UnsupportedRequest) as error:
        ensure_supported(request, TODAY)
    assert error.value.code == "UNSUPPORTED_REGION"


def test_valid_request_round_trips_canonical_values(client):
    response = client.post(PROBE, json=payload("region.latitude", 28.61394))
    assert response.status_code == 200
    assert response.json()["region"]["latitude"] == 28.6139


def test_validation_errors_use_safe_fixed_details(client):
    body = payload("region.latitude", "SECRETVALUE")
    body["period"]["start_year"] = 1990.5
    body["evil<script>key"] = "SECRETVALUE"
    response = client.post(PROBE, json=body)
    error = error_of(response, 422, "VALIDATION_ERROR")
    assert error.retryable is False
    fields = {detail.field for detail in error.details}
    assert fields == {"region.latitude", "period.start_year", "*"}
    assert "SECRETVALUE" not in response.text and "<script>" not in response.text

    tagged = client.post(PROBE, json=payload("region.kind", "SECRET-TAG"))
    assert [d.field for d in error_of(tagged, 422, "VALIDATION_ERROR").details] == ["region"]
    assert "SECRET-TAG" not in tagged.text


def test_validation_details_are_bounded(client):
    body = payload()
    body.update({f"extra_{index}": index for index in range(30)})
    assert len(error_of(client.post(PROBE, json=body), 422, "VALIDATION_ERROR").details) == 20


@pytest.mark.parametrize("raw,field", [
    (b'{"hazard": ', "body"),
    (b'{"hazard":"heatwave","region":{"kind":"point","label":"x","latitude":NaN,'
     b'"longitude":0},"period":{"start_year":1990,"end_year":2000}}', "region.latitude"),
])
def test_malformed_and_nonfinite_json(client, raw, field):
    response = client.post(PROBE, content=raw, headers={"Content-Type": "application/json"})
    assert [d.field for d in error_of(response, 422, "VALIDATION_ERROR").details] == [field]


@pytest.mark.parametrize("body,code", [
    (payload("region", bbox()), "UNSUPPORTED_REGION"),
    (payload("period.start_year", 1930), "UNSUPPORTED_PERIOD"),
])
def test_unsupported_requests_use_typed_422(client, body, code):
    error = error_of(client.post(PROBE, json=body), 422, code)
    assert error.details and error.retryable is False


def test_missing_route_and_method_use_envelope(client):
    error_of(client.get("/api/v1/missing"), 404, "NOT_FOUND")
    response = client.post("/api/v1/health")
    error_of(response, 405, "METHOD_NOT_ALLOWED")
    assert "GET" in response.headers["Allow"]


def source(kind="nasa_power", **changes):
    nasa = kind == "nasa_power"
    body = {
        "provider": kind,
        "model": "MERRA-2" if nasa else "ERA5",
        "dataset_kind": "reanalysis",
        "grid_degrees": {"latitude": 0.5, "longitude": 0.625} if nasa else
                        {"latitude": 0.25, "longitude": 0.25},
        "time_standard": "UTC",
        "temperature_unit": "celsius",
        "normalization_version": "daily-tmax-v1",
        "sample_points": [{
            "requested": {"latitude": 28.6139, "longitude": 77.209},
            "resolved": None if nasa else {"latitude": 28.625, "longitude": 77.25},
            "elevation_m": 206.37,
        }],
        "attribution_url": "https://power.larc.nasa.gov/" if nasa else "https://open-meteo.com/",
        "retrieved_at": "2026-10-14T06:00:00Z",
    }
    body.update(changes)
    return body


@pytest.mark.parametrize("provider", ["nasa_power", "open_meteo"])
def test_source_profiles_serialize_truthfully(provider):
    serialized = Source.model_validate(source(provider)).model_dump(mode="json")
    assert serialized == source(provider)


@pytest.mark.parametrize("provider,changes", [
    ("nasa_power", {"model": "ERA5"}), ("open_meteo", {"model": "MERRA-2"}),
    ("nasa_power", {"grid_degrees": {"latitude": 0.25, "longitude": 0.25}}),
    ("open_meteo", {"attribution_url": "https://evil.example/"}),
    ("nasa_power", {"sample_points": source("open_meteo")["sample_points"]}),
    ("nasa_power", {"sample_points": []}), ("nasa_power", {"time_standard": "GMT"}),
    ("open_meteo", {"provider": "visual_crossing"}), ("nasa_power", {"unexpected": 1}),
    ("nasa_power", {"retrieved_at": "2026-10-14T06:00:00+05:30"}),
    ("nasa_power", {"retrieved_at": "2026-10-14T06:00:00"}),
])
def test_mismatched_source_metadata_is_rejected(provider, changes):
    with pytest.raises(ValidationError):
        Source.model_validate(source(provider, **changes))
