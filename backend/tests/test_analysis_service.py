import asyncio
from datetime import date, timedelta

import pytest

from app.climate import InsufficientBaseline
from app.database import DatabaseUnavailable
from app.providers.transport import ProviderError
from app.schemas import AnalysisRequest, AnalysisResponse, UnsupportedRequest
from app.selector import SourcesFailed
from app.settings import WeatherSettings
from tests.fakes import NOW, FakeCache, FakeWeather, service

FALLBACK = WeatherSettings(weather_fallback_enabled=True, open_meteo_noncommercial_use=True)


def request(label="New Delhi", start=2001, end=2010, region=None):
    return AnalysisRequest.model_validate({
        "hazard": "heatwave",
        "region": region or {"kind": "point", "label": label, "latitude": 28.6139,
                             "longitude": 77.209},
        "period": {"start_year": start, "end_year": end},
    })


def analyze(svc, req=None, request_id="req-1"):
    return asyncio.run(svc.analyze(req or request(), request_id))


def test_nasa_analysis_persists_reads_back_and_reports_truthful_source():
    weather, cache = FakeWeather(), FakeCache()
    svc, calls = service(weather=weather, cache=cache)
    result = analyze(svc)
    assert isinstance(result, AnalysisResponse)
    assert calls == [("nasa_power", date(1991, 1, 1), date(2020, 12, 31))]
    assert weather.saves == 1 and cache.puts == 1
    assert result.contract_version == "0.2" and result.request_id == "req-1"
    assert (result.source.provider, result.source.model) == ("nasa_power", "MERRA-2")
    assert result.source.sample_points[0].resolved is None
    codes = {w.code for w in result.warnings}
    assert {"RESOLVED_LOCATION_UNKNOWN", "GRID_CELL_REPRESENTATION"} <= codes
    assert result.summary.threshold_c == 20.0 and result.summary.event_count == 10
    assert result.summary.trend_direction == "flat"
    assert [e.start_date for e in result.events][:2] == [date(2001, 7, 1), date(2002, 7, 1)]
    assert result.cache.hit is False and result.cache.generated_at == NOW
    assert result.cache.expires_at == NOW + timedelta(hours=24)


def test_cache_hit_reuses_result_with_fresh_request_id_and_current_label():
    cache = FakeCache()
    svc, calls = service(cache=cache)
    first = analyze(svc, request("New Delhi"), "req-1")
    second = analyze(svc, request("Delhi NCR"), "req-2")
    assert len(calls) == 1 and cache.puts == 1
    assert second.cache.hit is True and second.request_id == "req-2"
    assert second.region.label == "Delhi NCR"
    assert second.cache.generated_at == first.cache.generated_at
    stored = next(iter(cache.rows.values()))[0]
    assert "request_id" not in stored and "label" not in stored["region"]
    assert "hit" not in stored["cache"]


def test_concurrent_identical_misses_fetch_once():
    svc, calls = service()

    async def both():
        return await asyncio.gather(svc.analyze(request(), "a"), svc.analyze(request(), "b"))

    first, second = asyncio.run(both())
    assert len(calls) == 1
    assert {first.cache.hit, second.cache.hit} == {False, True}


def test_stored_weather_is_reused_without_fetching():
    weather = FakeWeather()
    svc, calls = service(weather=weather)
    analyze(svc)
    fresh, fresh_calls = service(weather=weather)
    analyze(fresh, request(start=2002))
    assert len(calls) == 1 and fresh_calls == []


@pytest.mark.parametrize("req,code", [
    (request(region={"kind": "bbox", "label": "Box", "south": 28, "west": 77,
                     "north": 31, "east": 78}), "UNSUPPORTED_REGION"),
    (request(start=1975, end=1990), "UNSUPPORTED_PERIOD"),
    (request(start=2000, end=2026), "UNSUPPORTED_PERIOD"),
])
def test_unsupported_requests_cause_no_io(req, code):
    weather, cache = FakeWeather(), FakeCache()
    svc, calls = service(weather=weather, cache=cache)
    with pytest.raises(UnsupportedRequest) as error:
        analyze(svc, req)
    assert error.value.code == code
    assert calls == [] and weather.saves == 0 and cache.rows == {}


def test_primary_failure_falls_back_to_whole_era5_dataset():
    svc, calls = service(FALLBACK, {"nasa_power": ProviderError("nasa_power", "timeout")})
    result = analyze(svc)
    assert [p for p, *_ in calls] == ["nasa_power", "open_meteo"]
    assert (result.source.provider, result.source.model) == ("open_meteo", "ERA5")
    assert result.source.sample_points[0].resolved.latitude == 28.5
    assert "SOURCE_FALLBACK" in {w.code for w in result.warnings}


def test_pre_1981_period_uses_era5_only_when_enabled():
    svc, calls = service(FALLBACK)
    result = analyze(svc, request(start=1975, end=1985))
    assert {p for p, *_ in calls} == {"open_meteo"}
    assert result.source.provider == "open_meteo"


@pytest.mark.parametrize("failure,expected", [
    ({"nasa_power": ProviderError("nasa_power", "unavailable")}, SourcesFailed),
    ({"nasa_power": {date(1995, m, d) for m in range(1, 13) for d in range(1, 5)}},
     InsufficientBaseline),
])
def test_failures_are_never_cached(failure, expected):
    cache = FakeCache()
    svc, _ = service(fetchers=failure, cache=cache)
    with pytest.raises(expected):
        analyze(svc)
    assert cache.puts == 0


def test_failed_readback_is_a_storage_error_not_a_result():
    cache = FakeCache()
    svc, _ = service(weather=FakeWeather(readback=False), cache=cache)
    with pytest.raises(DatabaseUnavailable):
        analyze(svc)
    assert cache.puts == 0


def test_result_expiry_never_outlives_negative_weather_entries():
    missing = {date(2005, 3, 3)}
    svc, _ = service(fetchers={"nasa_power": missing})
    result = analyze(svc)
    assert result.cache.expires_at == NOW + timedelta(hours=1)
    assert result.status == "partial"


def test_response_values_are_rounded_for_serialization():
    svc, _ = service()
    payload = analyze(svc).model_dump(mode="json")
    assert payload["summary"]["threshold_c"] == 20.0
    assert payload["events"][0] == {
        "start_date": "2001-07-01", "end_date": "2001-07-03", "duration_days": 3,
        "mean_excess_c": 5.0, "max_excess_c": 5.0, "boundary_censored": False,
    }
    assert payload["cache"]["generated_at"].endswith("Z")
    assert payload["data_quality"]["analysis"]["coverage_fraction"] == 1.0
