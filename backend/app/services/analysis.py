"""Point heatwave analysis: validate, cache, select one source, persist, read back, compute."""

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import UTC, date, datetime, timedelta

from app import climate
from app import schemas as wire
from app.database import DatabaseUnavailable
from app.ingestion import NORMALIZATION_VERSION, DailySeries
from app.providers.nasa_power import fetch_nasa_power
from app.providers.open_meteo import fetch_open_meteo
from app.selector import (
    earliest_start_year,
    eligible_providers,
    required_intervals,
    select_source,
)
from app.settings import WeatherSettings
from app.spatial import aggregate_regional_days, cosine_weights, sample_centers

FETCHERS = {"nasa_power": fetch_nasa_power, "open_meteo": fetch_open_meteo}
RESULT_TTL = timedelta(hours=24)
ANALYSIS_BUDGET_SECONDS = 90
PROVIDER_LABELS = {"nasa_power": "NASA POWER", "open_meteo": "Open-Meteo"}


class KeyedLocks:
    """Per-key locks that disappear when no request holds or awaits them."""

    def __init__(self) -> None:
        self._locks: dict[str, tuple[asyncio.Lock, int]] = {}

    @asynccontextmanager
    async def hold(self, key: str) -> AsyncIterator[None]:
        lock, users = self._locks.get(key, (asyncio.Lock(), 0))
        self._locks[key] = (lock, users + 1)
        try:
            async with lock:
                yield
        finally:
            lock, users = self._locks[key]
            if users == 1:
                del self._locks[key]
            else:
                self._locks[key] = (lock, users - 1)


def _round(value: float | None, digits: int) -> float | None:
    return None if value is None else round(value, digits) + 0.0


def cache_key(request: wire.AnalysisRequest, providers: tuple[str, ...], minimum: float) -> str:
    region = request.region
    if region.kind == "point":
        region_desc = [region.kind, f"{region.latitude:.4f}", f"{region.longitude:.4f}"]
    else:
        region_desc = [
            region.kind,
            f"{region.south:.4f}",
            f"{region.west:.4f}",
            f"{region.north:.4f}",
            f"{region.east:.4f}",
        ]
    canonical = {
        "contract": wire.CONTRACT_VERSION,
        "method": climate.METHOD_VERSION,
        "normalization": NORMALIZATION_VERSION,
        "region": region_desc,
        "period": [request.period.start_year, request.period.end_year],
        "baseline": [climate.BASELINE_START.isoformat(), climate.BASELINE_END.isoformat()],
        "rules": [climate.PERCENTILE, climate.MIN_RUN_DAYS, "strictly_greater", "utc"],
        "quality": [str(climate.YEAR_MIN_VALID), str(climate.MONTH_MIN_VALID), minimum],
        "providers": list(providers),
    }
    encoded = json.dumps(canonical, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(encoded.encode()).hexdigest()


def _fingerprint(series: tuple[DailySeries, ...]) -> str:
    digest = hashlib.sha256()
    for part in series:
        digest.update(f"{part.provider}|{part.requested}|{part.retrieved_at.isoformat()}".encode())
        for day in part.days:
            digest.update(f"{day.day}|{day.tmax_c}|{day.quality}|{day.duplicate}".encode())
    return digest.hexdigest()


def _coverage(cover: climate.Coverage) -> dict:
    return {
        "expected_days": cover.expected_days,
        "valid_days": cover.valid_days,
        "missing_days": cover.missing_days,
        "invalid_days": cover.invalid_days,
        "duplicate_dates": cover.duplicate_dates,
        "coverage_fraction": round(cover.coverage_fraction, 6),
    }


def _source_warnings(
    selection_provider: str, failures, sample_series: Sequence[DailySeries]
) -> list[dict]:
    profile = wire.SOURCE_PROFILES[selection_provider]
    lat_step, lon_step = profile.grid_degrees
    point_text = "the point" if len(sample_series) == 1 else "each sampled point"
    warnings = [
        {
            "code": "GRID_CELL_REPRESENTATION",
            "message": f"Values describe a {profile.model} reanalysis grid cell of about "
            f"{lat_step}° x {lon_step}° around {point_text}, not a weather station.",
            "years": [],
        }
    ]
    if any(s.resolved is None for s in sample_series):
        warnings.append(
            {
                "code": "RESOLVED_LOCATION_UNKNOWN",
                "message": f"{PROVIDER_LABELS[selection_provider]} does not report which grid cell "
                "it used, so only the requested coordinates are shown.",
                "years": [],
            }
        )
    if failures:
        tried = ", ".join(PROVIDER_LABELS[p] for p, _ in failures)
        warnings.append(
            {
                "code": "SOURCE_FALLBACK",
                "message": f"{tried} could not supply usable data, so every value, including the "
                f"baseline, came from {PROVIDER_LABELS[selection_provider]}.",
                "years": [],
            }
        )
    return warnings


def build_payload(
    request: wire.AnalysisRequest,
    result: climate.HeatwaveResult,
    provider: str,
    failures,
    series: tuple[DailySeries, ...],
    sample_point_series: Sequence[DailySeries],
    unique_cell_count: int,
    generated_at: datetime,
    expires_at: datetime,
) -> dict:
    profile = wire.SOURCE_PROFILES[provider]
    sample_points = [
        {
            "requested": {
                "latitude": s.requested[0],
                "longitude": s.requested[1],
            },
            "resolved": (
                None
                if s.resolved is None
                else {"latitude": s.resolved[0], "longitude": s.resolved[1]}
            ),
            "elevation_m": s.elevation_m,
        }
        for s in sample_point_series
    ]
    aggregation = "point" if request.region.kind == "point" else "nine_point_cosine_weighted_mean"
    region_warnings = []
    if request.region.kind == "bbox":
        region_warnings.append(
            {
                "code": "REGIONAL_APPROXIMATION",
                "message": (
                    "Regional series is a 3x3 cosine-weighted mean of daily maxima, "
                    "not a station observation or area maximum."
                ),
                "years": [],
            }
        )
        if unique_cell_count < len(sample_point_series):
            diff = len(sample_point_series) - unique_cell_count
            plural = "s" if diff > 1 else ""
            region_warnings.append(
                {
                    "code": "SHARED_GRID_CELLS",
                    "message": (
                        f"{diff} sample point{plural} shared provider grid cells "
                        f"and their weights were combined "
                        f"({unique_cell_count} unique cells sampled)."
                    ),
                    "years": [],
                }
            )

    payload = {
        "contract_version": wire.CONTRACT_VERSION,
        "region": request.region.model_dump(exclude={"label"}),
        "period": request.period.model_dump(),
        "status": result.status,
        "summary": {
            "event_count": result.event_count,
            "mean_duration_days": _round(result.mean_duration_days, 3),
            "threshold_c": _round(result.threshold_c, 3),
            "trend_direction": result.trend_direction,
            "frequency_slope_per_year": _round(result.frequency_slope_per_year, 6),
            "trend_year_count": result.trend_year_count,
        },
        "annual": [
            {
                **asdict(row),
                "coverage_fraction": round(row.coverage_fraction, 6),
                "mean_duration_days": _round(row.mean_duration_days, 3),
                "mean_tmax_c": _round(row.mean_tmax_c, 3),
                "tmax_anomaly_c": _round(row.tmax_anomaly_c, 3),
                "frequency_rolling_5y": _round(row.frequency_rolling_5y, 3),
            }
            for row in result.annual
        ],
        "events": [
            {
                "start_date": event.start.isoformat(),
                "end_date": event.end.isoformat(),
                "duration_days": event.duration_days,
                "mean_excess_c": _round(event.mean_excess_c, 3),
                "max_excess_c": _round(event.max_excess_c, 3),
                "boundary_censored": event.boundary_censored,
            }
            for event in result.events
        ],
        "insights": [
            {
                "code": insight.code,
                "text": insight.text,
                "evidence": [
                    {**asdict(item), "value": _round(item.value, 6), "years": list(item.years)}
                    for item in insight.evidence
                ],
            }
            for insight in result.insights
        ],
        "warnings": [
            {"code": w.code, "message": w.message, "years": list(w.years)} for w in result.warnings
        ]
        + region_warnings
        + _source_warnings(provider, failures, sample_point_series),
        "methodology": wire.Methodology(aggregation=aggregation).model_dump(),
        "data_quality": {
            "baseline": _coverage(result.baseline),
            "analysis": _coverage(result.analysis),
            "years": [
                {
                    **_coverage(cover),
                    "year": cover.year,
                    "eligible": cover.eligible,
                    "excluded_reasons": list(cover.excluded_reasons),
                }
                for cover in result.years
            ],
            "eligible_year_count": result.trend_year_count,
        },
        "source": {
            "provider": provider,
            "model": profile.model,
            "dataset_kind": "reanalysis",
            "grid_degrees": {
                "latitude": profile.grid_degrees[0],
                "longitude": profile.grid_degrees[1],
            },
            "time_standard": "UTC",
            "temperature_unit": "celsius",
            "normalization_version": NORMALIZATION_VERSION,
            "sample_points": sample_points,
            "attribution_url": profile.attribution_url,
            "retrieved_at": min(part.retrieved_at for part in series).isoformat(),
        },
        "cache": {"generated_at": generated_at.isoformat(), "expires_at": expires_at.isoformat()},
    }
    return payload


def respond(payload: dict, request: wire.AnalysisRequest, request_id: str, hit: bool):
    region = {**payload["region"], "label": request.region.label}
    return wire.AnalysisResponse.model_validate(
        {
            **payload,
            "request_id": request_id,
            "region": region,
            "cache": {**payload["cache"], "hit": hit},
        }
    )


Fetcher = Callable[..., Awaitable[DailySeries]]


class AnalysisService:
    def __init__(
        self,
        settings: WeatherSettings,
        http,
        weather,
        cache,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        fetchers: dict[str, Fetcher] = FETCHERS,
    ):
        self.settings = settings
        self.http = http
        self.weather = weather
        self.cache = cache
        self.clock = clock
        self.fetchers = fetchers
        self.locks = KeyedLocks()

    async def analyze(self, request: wire.AnalysisRequest, request_id: str):
        wire.ensure_supported(request, self.clock().date())
        providers = eligible_providers(self.settings, request.period.start_year)
        if not providers:
            detail = wire.ErrorDetail(
                field="period.start_year",
                message=f"The enabled data source starts in {earliest_start_year(self.settings)}",
            )
            raise wire.UnsupportedRequest(
                "UNSUPPORTED_PERIOD", "Requested period is not supported", [detail]
            )
        key = cache_key(request, providers, self.settings.weather_min_coverage_percent)
        async with asyncio.timeout(ANALYSIS_BUDGET_SECONDS):
            payload = await self.cache.get(key, self.clock())
            hit = payload is not None
            if not hit:
                async with self.locks.hold(key):
                    payload = await self.cache.get(key, self.clock())
                    hit = payload is not None
                    if not hit:
                        payload = await self._compute(request, providers, key)
        return respond(payload, request, request_id, hit)

    async def _compute(self, request: wire.AnalysisRequest, providers, key: str) -> dict:
        region, period = request.region, request.period
        expiries: dict[str, list[datetime]] = {}
        sample_point_series: dict[str, list[DailySeries]] = {}
        unique_cells: dict[str, int] = {}

        coords = sample_centers(region)
        weights = cosine_weights(coords)

        async def load_one_point(
            provider: str, lat: float, lon: float, start: date, end: date, deadline: float
        ) -> DailySeries:
            point = (lat, lon)
            stored = await self.weather.load(provider, *point, start, end, self.clock())
            if stored is None:
                fetched = await self.fetchers[provider](self.http, *point, start, end, deadline)
                await self.weather.save(fetched)
                stored = await self.weather.load(provider, *point, start, end, self.clock())
                if stored is None:
                    raise DatabaseUnavailable("readback_incomplete")
            series, expires_at = stored
            expiries.setdefault(provider, []).append(expires_at)
            return series

        async def load(provider: str, start: date, end: date, deadline: float) -> DailySeries:
            point_series = [
                await load_one_point(
                    provider, coord.latitude, coord.longitude, start, end, deadline
                )
                for coord in coords
            ]
            sample_point_series[provider] = point_series
            aggregated_days, cell_count = aggregate_regional_days(coords, weights, point_series)
            unique_cells[provider] = cell_count
            return DailySeries(
                provider=provider,
                requested=(coords[0].latitude, coords[0].longitude),
                resolved=point_series[0].resolved if len(coords) == 1 else None,
                elevation_m=point_series[0].elevation_m if len(coords) == 1 else None,
                retrieved_at=min(s.retrieved_at for s in point_series),
                days=aggregated_days,
            )

        deadline = asyncio.get_running_loop().time() + self.settings.weather_total_timeout_seconds
        selection = await select_source(
            providers,
            required_intervals(period.start_year, period.end_year),
            load,
            deadline,
            self.settings.weather_min_coverage_percent,
        )
        days = {day.day: day for part in selection.series for day in part.days}

        def span(start: date, end: date) -> tuple:
            return tuple(days[start + timedelta(days=i)] for i in range((end - start).days + 1))

        result = climate.analyze_heatwaves(
            span(climate.BASELINE_START, climate.BASELINE_END),
            span(date(period.start_year, 1, 1), date(period.end_year, 12, 31)),
        )
        generated_at = self.clock()
        expires_at = min([generated_at + RESULT_TTL, *expiries[selection.provider]])
        payload = build_payload(
            request,
            result,
            selection.provider,
            selection.failures,
            selection.series,
            sample_point_series[selection.provider],
            unique_cells.get(selection.provider, 1),
            generated_at,
            expires_at,
        )
        # Validate the contract before persisting so an invalid result is never cached.
        respond(payload, request, "validation", hit=False)
        await self.cache.put(key, payload, generated_at, expires_at, _fingerprint(selection.series))
        return payload
