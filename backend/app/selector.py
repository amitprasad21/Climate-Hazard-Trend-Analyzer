"""Whole-source provider selection: every required interval comes from one provider."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date, timedelta

from app.climate import BASELINE_END, BASELINE_START
from app.ingestion import DailySeries
from app.providers.transport import ProviderError
from app.schemas import SOURCE_PROFILES, ProviderName
from app.settings import WeatherSettings

Interval = tuple[date, date]
Loader = Callable[[ProviderName, date, date, float], Awaitable[DailySeries]]


class SourcesFailed(Exception):
    def __init__(self, failures: tuple[tuple[ProviderName, str], ...]):
        self.failures = failures
        super().__init__("No eligible provider returned usable data")

    @property
    def timed_out(self) -> bool:
        return any(kind == "timeout" for _, kind in self.failures)


@dataclass(frozen=True)
class SourceSelection:
    provider: ProviderName
    series: tuple[DailySeries, ...]
    failures: tuple[tuple[ProviderName, str], ...]


def required_intervals(start_year: int, end_year: int) -> tuple[Interval, ...]:
    spans = sorted(
        [(date(start_year, 1, 1), date(end_year, 12, 31)), (BASELINE_START, BASELINE_END)]
    )
    merged = [spans[0]]
    for start, end in spans[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end + timedelta(days=1):
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return tuple(merged)


def eligible_providers(settings: WeatherSettings, start_year: int) -> tuple[ProviderName, ...]:
    first_needed = min(start_year, BASELINE_START.year)
    return tuple(
        provider
        for provider in settings.provider_order
        if SOURCE_PROFILES[provider].first_year <= first_needed
    )


def _usable(series: tuple[DailySeries, ...], minimum_percent: float) -> bool:
    days = [day for part in series for day in part.days]
    return sum(day.quality == "valid" for day in days) * 100 >= minimum_percent * len(days)


async def select_source(
    providers: tuple[ProviderName, ...],
    intervals: tuple[Interval, ...],
    load: Loader,
    deadline: float,
    minimum_percent: float,
) -> SourceSelection:
    if not providers:
        raise ValueError("No eligible provider for the requested period")
    failures: list[tuple[ProviderName, str]] = []
    for provider in providers:
        try:
            series = tuple([await load(provider, start, end, deadline) for start, end in intervals])
        except ProviderError as error:
            failures.append((provider, error.kind))
            continue
        if _usable(series, minimum_percent):
            return SourceSelection(provider, series, tuple(failures))
        failures.append((provider, "unusable"))
    raise SourcesFailed(tuple(failures))
