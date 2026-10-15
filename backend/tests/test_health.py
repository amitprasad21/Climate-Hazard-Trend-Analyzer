import pytest
from fastapi.testclient import TestClient

from app.database import DatabaseUnavailable
from app.main import create_app
from app.settings import WeatherSettings
from tests.fakes import no_services


class FakeDatabase:
    def __init__(self, fail_open=False):
        self.fail_open = fail_open
        self.available = True
        self.pings = 0
        self.closes = 0

    async def open(self):
        if self.fail_open:
            raise DatabaseUnavailable("network_or_availability")

    async def ping(self):
        self.pings += 1
        if not self.available:
            raise DatabaseUnavailable("network_or_availability")

    async def close(self):
        self.closes += 1


def client_for(db_settings, database):
    app = create_app(db_settings, lambda config: database, services_factory=no_services)
    return TestClient(app)


def test_liveness_performs_no_database_io(db_settings):
    database = FakeDatabase()
    with client_for(db_settings, database) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "api_version": "v1", "earliest_start_year": 1981}
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Request-ID"]
    assert database.pings == 0
    assert database.closes == 1


def test_liveness_reports_the_earliest_year_of_the_enabled_sources(db_settings):
    fallback = WeatherSettings(weather_fallback_enabled=True, open_meteo_noncommercial_use=True)
    app = create_app(
        db_settings,
        lambda config: FakeDatabase(),
        weather_settings=fallback,
        services_factory=no_services,
    )
    with TestClient(app) as client:
        assert client.get("/api/v1/health").json()["earliest_start_year"] == 1940


def test_readiness_detects_outage_with_safe_envelope(db_settings):
    database = FakeDatabase()
    with client_for(db_settings, database) as client:
        ready = client.get("/api/v1/health/ready")
        database.available = False
        first = client.get("/api/v1/health/ready")
        second = client.get("/api/v1/health/ready")
    assert ready.status_code == 200
    assert ready.json() == {"status": "ok", "api_version": "v1", "database": "available"}
    assert first.status_code == 503
    error = first.json()["error"]
    assert error["code"] == "STORAGE_UNAVAILABLE"
    assert error["retryable"] is True
    assert error["details"] == []
    assert error["request_id"] == first.headers["X-Request-ID"]
    assert first.headers["Cache-Control"] == "no-store"
    assert second.json()["error"]["request_id"] != error["request_id"]
    for private in ("cluster.example.mongodb.net", "encoded%40secret", "climate_hazard_analyzer"):
        assert private not in first.text
    assert database.closes == 1


def test_startup_refuses_unavailable_database_and_closes(db_settings):
    database = FakeDatabase(fail_open=True)
    with pytest.raises(DatabaseUnavailable):
        with client_for(db_settings, database):
            pass
    assert database.closes == 1
