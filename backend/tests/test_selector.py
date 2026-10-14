import asyncio
from datetime import UTC, date, datetime

import pytest

from app.database import DatabaseUnavailable
from app.ingestion import DailySeries, normalize
from app.providers.transport import ProviderError
from app.selector import SourcesFailed, eligible_providers, required_intervals, select_source
from app.settings import WeatherSettings

FALLBACK = WeatherSettings(weather_fallback_enabled=True, open_meteo_noncommercial_use=True)


def series(provider, start, end, missing_every=0):
    span = (end - start).days + 1
    records = [
        (start.fromordinal(start.toordinal() + i),
         None if missing_every and i % missing_every == 0 else 30.0)
        for i in range(span)
    ]
    return DailySeries(provider, (28.6139, 77.209), None, None, datetime.now(UTC),
                       normalize(records, start, end))


def loader(outcomes):
    calls = []

    async def load(provider, start, end, deadline):
        calls.append((provider, start, end))
        outcome = outcomes[provider]
        if isinstance(outcome, BaseException):
            raise outcome
        if callable(outcome):
            return outcome(provider, start, end, len(calls))
        return series(provider, start, end, outcome)

    return load, calls


def select(providers, intervals, outcomes):
    load, calls = loader(outcomes)
    try:
        return asyncio.run(select_source(providers, intervals, load, 0.0, 95)), calls
    except SourcesFailed as error:
        return error, calls


@pytest.mark.parametrize("start,end,expected", [
    (1990, 2020, [("1990-01-01", "2020-12-31")]),
    (2021, 2025, [("1991-01-01", "2025-12-31")]),
    (1975, 1995, [("1975-01-01", "2020-12-31")]),
    (1950, 1960, [("1950-01-01", "1960-12-31"), ("1991-01-01", "2020-12-31")]),
    (2000, 2010, [("1991-01-01", "2020-12-31")]),
])
def test_required_intervals_merge_baseline_without_extra_years(start, end, expected):
    assert [(a.isoformat(), b.isoformat()) for a, b in required_intervals(start, end)] == expected


@pytest.mark.parametrize("settings,start,expected", [
    (WeatherSettings(), 1990, ("nasa_power",)), (WeatherSettings(), 1975, ()),
    (FALLBACK, 1990, ("nasa_power", "open_meteo")), (FALLBACK, 1981, ("nasa_power", "open_meteo")),
    (FALLBACK, 1980, ("open_meteo",)),
])
def test_eligibility_depends_on_coverage_and_enabled_fallback(settings, start, expected):
    assert eligible_providers(settings, start) == expected


INTERVALS = required_intervals(1950, 1960)


def test_primary_success_loads_only_primary():
    result, calls = select(("nasa_power", "open_meteo"), INTERVALS,
                           {"nasa_power": 0, "open_meteo": 0})
    assert result.provider == "nasa_power" and result.failures == ()
    assert {provider for provider, *_ in calls} == {"nasa_power"} and len(calls) == 2


@pytest.mark.parametrize("kind", ["timeout", "unavailable", "invalid_response"])
def test_primary_failure_on_later_interval_refetches_everything_from_fallback(kind):
    def fail_second(provider, start, end, call):
        if call == 2:
            raise ProviderError(provider, kind)
        return series(provider, start, end)

    result, calls = select(("nasa_power", "open_meteo"), INTERVALS,
                           {"nasa_power": fail_second, "open_meteo": 0})
    assert result.provider == "open_meteo"
    assert {s.provider for s in result.series} == {"open_meteo"} and len(result.series) == 2
    assert result.failures == (("nasa_power", kind),)
    assert [p for p, *_ in calls] == ["nasa_power", "nasa_power", "open_meteo", "open_meteo"]


def test_unusable_primary_coverage_triggers_fallback():
    result, _ = select(("nasa_power", "open_meteo"), INTERVALS,
                       {"nasa_power": 10, "open_meteo": 0})
    assert result.provider == "open_meteo"
    assert result.failures == (("nasa_power", "unusable"),)


def test_all_sources_failing_is_controlled():
    error, _ = select(("nasa_power", "open_meteo"), INTERVALS, {
        "nasa_power": ProviderError("nasa_power", "timeout"),
        "open_meteo": ProviderError("open_meteo", "invalid_response"),
    })
    assert isinstance(error, SourcesFailed)
    assert error.failures == (("nasa_power", "timeout"), ("open_meteo", "invalid_response"))
    assert error.timed_out is True


@pytest.mark.parametrize("failure", [DatabaseUnavailable("x"), asyncio.CancelledError()])
def test_storage_failures_and_cancellation_never_trigger_fallback(failure):
    load, calls = loader({"nasa_power": failure, "open_meteo": 0})
    with pytest.raises(type(failure)):
        asyncio.run(select_source(("nasa_power", "open_meteo"), INTERVALS, load, 0.0, 95))
    assert {p for p, *_ in calls} == {"nasa_power"}


def test_no_eligible_provider_is_a_caller_error():
    load, calls = loader({})
    with pytest.raises(ValueError):
        asyncio.run(select_source((), INTERVALS, load, 0.0, 95))
    assert calls == []
    assert date(1991, 1, 1) == INTERVALS[1][0]
