from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import create_app
from app.security import CapacityGuard, RateLimiter
from app.settings import ApiSettings, load_api_settings
from tests.fakes import service

URL = "/api/v1/analyses/heatwaves"
ORIGIN = "http://127.0.0.1:5173"
BODY = {
    "hazard": "heatwave",
    "region": {"kind": "point", "label": "New Delhi", "latitude": 28.6139, "longitude": 77.209},
    "period": {"start_year": 2001, "end_year": 2010},
}


def client(db_settings, analysis=None, regions=None, **api):
    @asynccontextmanager
    async def factory(database, weather_settings):
        yield SimpleNamespace(analysis=analysis or service()[0], regions=regions)

    database = Mock(open=AsyncMock(), ping=AsyncMock(), close=AsyncMock())
    config = ApiSettings(**api)
    app = create_app(db_settings, lambda c: database, services_factory=factory, api_settings=config)
    return TestClient(app, raise_server_exceptions=False)


def error_code(response):
    assert response.headers["Cache-Control"] == "no-store"
    assert response.json()["error"]["request_id"] == response.headers["X-Request-ID"]
    return response.json()["error"]["code"]


def test_declared_and_streamed_oversize_bodies_are_rejected(db_settings):
    with client(db_settings) as api:
        declared = api.post(URL, content=b"{}", headers={
            "Content-Type": "application/json", "Content-Length": "9000"})
        streamed = api.post(URL, content=iter([b" " * 5000, b" " * 5000]),
                            headers={"Content-Type": "application/json"})
    assert declared.status_code == streamed.status_code == 413
    assert error_code(declared) == error_code(streamed) == "PAYLOAD_TOO_LARGE"


@pytest.mark.parametrize("content_type", ["text/plain", "application/x-www-form-urlencoded", None])
def test_non_json_bodies_are_unsupported_media(db_settings, content_type):
    headers = {"Content-Type": content_type} if content_type else {}
    with client(db_settings) as api:
        response = api.post(URL, content=b'{"x":1}', headers=headers)
    assert response.status_code == 415 and error_code(response) == "UNSUPPORTED_MEDIA_TYPE"


def test_unexpected_errors_are_safe_logged_and_keep_cors(db_settings, caplog):
    analysis = Mock(analyze=AsyncMock(side_effect=RuntimeError("secret internal detail")))
    with client(db_settings, analysis) as api:
        response = api.post(URL, json=BODY, headers={"Origin": ORIGIN})
    assert response.status_code == 500 and error_code(response) == "INTERNAL_ERROR"
    assert "secret internal detail" not in response.text
    assert response.headers["Access-Control-Allow-Origin"] == ORIGIN
    record = next(r for r in caplog.records if r.name == "climate_hazard")
    assert response.headers["X-Request-ID"] in record.getMessage()
    assert record.exc_info and "secret internal detail" in str(record.exc_info[1])


def test_cors_is_exact_and_covers_errors(db_settings):
    with client(db_settings) as api:
        allowed = api.post(URL, json={**BODY, "hazard": "flood"}, headers={"Origin": ORIGIN})
        denied = api.get("/api/v1/health", headers={"Origin": "https://evil.example"})
        preflight = api.options(URL, headers={
            "Origin": ORIGIN, "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"})
        bad_preflight = api.options(URL, headers={
            "Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert allowed.status_code == 422
    assert allowed.headers["Access-Control-Allow-Origin"] == ORIGIN
    assert {"x-request-id", "retry-after"} <= {
        h.strip().lower() for h in allowed.headers["Access-Control-Expose-Headers"].split(",")}
    assert "Access-Control-Allow-Origin" not in denied.headers
    assert preflight.status_code == 200
    assert "POST" in preflight.headers["Access-Control-Allow-Methods"]
    assert "Access-Control-Allow-Credentials" not in preflight.headers
    assert bad_preflight.status_code == 400


def test_analysis_rate_limit_returns_retry_after(db_settings):
    with client(db_settings, analysis_rate_per_minute=2) as api:
        statuses = [api.post(URL, json=BODY).status_code for _ in range(2)]
        limited = api.post(URL, json=BODY)
    assert statuses == [200, 200]
    assert limited.status_code == 429 and error_code(limited) == "RATE_LIMITED"
    assert limited.json()["error"]["retryable"] is True
    assert 1 <= int(limited.headers["Retry-After"]) <= 60


def test_forwarded_identity_is_trusted_only_when_configured(db_settings):
    spoof = [{"X-Forwarded-For": f"10.0.0.{i}"} for i in range(3)]
    with client(db_settings, analysis_rate_per_minute=1) as api:
        ignored = [api.post(URL, json=BODY, headers=h).status_code for h in spoof]
    with client(db_settings, analysis_rate_per_minute=1, trusted_proxy_hops=1) as api:
        trusted = [api.post(URL, json=BODY, headers=h).status_code for h in spoof]
    assert ignored == [200, 429, 429]
    assert trusted == [200, 200, 200]


def test_search_has_its_own_limit(db_settings):
    regions = Mock(search=AsyncMock(return_value=[]))
    with client(db_settings, regions=regions, search_rate_per_minute=1) as api:
        first = api.get("/api/v1/regions/search", params={"q": "Delhi"})
        second = api.get("/api/v1/regions/search", params={"q": "Delhi"})
        analysis = api.post(URL, json=BODY)
    assert (first.status_code, second.status_code, analysis.status_code) == (200, 429, 200)


def test_full_capacity_returns_503(db_settings, monkeypatch):
    with client(db_settings) as api:
        monkeypatch.setattr(api.app.state.capacity, "available", 0)
        response = api.post(URL, json=BODY)
    assert response.status_code == 503 and error_code(response) == "CAPACITY_EXCEEDED"


def test_rate_limiter_windows_and_bounded_memory():
    now = [0.0]
    limiter = RateLimiter(2, clock=lambda: now[0], max_clients=3)
    assert [limiter.check("a") for _ in range(3)] == [None, None, 60]
    now[0] = 59.5
    assert limiter.check("a") == 1
    now[0] = 60.0
    assert limiter.check("a") is None
    for name in "bcdefg":
        limiter.check(name)
    assert len(limiter.windows) <= 3


def test_capacity_guard_releases_on_exit_and_errors():
    guard = CapacityGuard(1)
    with guard.slot() as acquired:
        assert acquired is True
        with guard.slot() as second:
            assert second is False
    with pytest.raises(RuntimeError), guard.slot():
        raise RuntimeError
    assert guard.available == 1


@pytest.mark.parametrize("origins", ["*", "http://127.0.0.1:5173/path", "ftp://x.example",
                                      "http://127.0.0.1:5173,https://"])
def test_origins_must_be_exact(origins):
    with pytest.raises(ValidationError):
        ApiSettings(allowed_origins=origins)


def test_api_settings_load_from_environment(tmp_path):
    env = tmp_path / ".env"
    env.write_text("ALLOWED_ORIGINS=https://app.example, http://127.0.0.1:5173\n"
                   "ANALYSIS_RATE_PER_MINUTE=7\n")
    loaded = load_api_settings(env)
    assert loaded.origins == ("https://app.example", "http://127.0.0.1:5173")
    assert loaded.analysis_rate_per_minute == 7
