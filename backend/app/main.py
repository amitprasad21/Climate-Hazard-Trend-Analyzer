"""FastAPI application: lifespan wiring, routes and the shared error envelope."""

from collections.abc import Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated

import httpx
from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from starlette.exceptions import HTTPException

from app.climate import InsufficientBaseline, InsufficientData
from app.database import Database, DatabaseUnavailable, safe_reason
from app.providers.transport import ProviderError, ProviderHttp
from app.repositories.analysis import AnalysisCacheRepository
from app.repositories.weather import WeatherRepository
from app.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ErrorBody,
    ErrorDetail,
    ErrorResponse,
    Health,
    Readiness,
    RegionSearch,
    SearchQuery,
    UnsupportedRequest,
    validation_details,
)
from app.security import (
    CapacityExceeded,
    CapacityGuard,
    RateLimited,
    RateLimiter,
    RequestContextMiddleware,
    client_identity,
)
from app.selector import SourcesFailed, earliest_start_year
from app.services.analysis import PROVIDER_LABELS, AnalysisService
from app.services.regions import RegionSearchService, SearchUnavailable
from app.settings import (
    ApiSettings,
    DatabaseSettings,
    WeatherSettings,
    load_api_settings,
    load_database_settings,
    load_weather_settings,
)

RETRYABLE_STATUSES = {429, 502, 503, 504}


HTTP_ERRORS = {
    404: ("NOT_FOUND", "Route not found"),
    405: ("METHOD_NOT_ALLOWED", "Method not allowed"),
    413: ("PAYLOAD_TOO_LARGE", "Request body is too large"),
}


def envelope(
    request_id: str,
    status: int,
    code: str,
    message: str,
    details: Sequence[ErrorDetail] = (),
    retryable: bool | None = None,
) -> dict:
    error = ErrorBody(
        code=code,
        message=message,
        request_id=request_id,
        details=list(details),
        retryable=status in RETRYABLE_STATUSES if retryable is None else retryable,
    )
    return ErrorResponse(error=error).model_dump()


def error_response(
    request: Request,
    status: int,
    code: str,
    message: str,
    details: Sequence[ErrorDetail] = (),
    retryable: bool | None = None,
) -> JSONResponse:
    body = envelope(request.state.request_id, status, code, message, details, retryable)
    return JSONResponse(status_code=status, content=body)


@dataclass(frozen=True)
class Services:
    analysis: AnalysisService
    regions: RegionSearchService


@asynccontextmanager
async def build_services(database: Database, weather_settings: WeatherSettings):
    weather = WeatherRepository(database.handle)
    cache = AnalysisCacheRepository(database.handle)
    try:
        await weather.ensure_schema()
        await cache.ensure_schema()
    except PyMongoError as exc:
        raise DatabaseUnavailable(safe_reason(exc)) from None
    # trust_env=False keeps proxy variables and .netrc credentials away from provider calls.
    async with httpx.AsyncClient(trust_env=False, follow_redirects=False) as client:
        http = ProviderHttp(client, weather_settings)
        yield Services(
            AnalysisService(weather_settings, http, weather, cache),
            RegionSearchService(weather_settings, http),
        )


def create_app(
    settings: DatabaseSettings | None = None,
    database_factory=Database,
    weather_settings: WeatherSettings | None = None,
    services_factory=build_services,
    api_settings: ApiSettings | None = None,
) -> FastAPI:
    api = api_settings or (load_api_settings() if settings is None else ApiSettings())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        config = settings if settings is not None else load_database_settings()
        weather = weather_settings or (
            load_weather_settings() if settings is None else WeatherSettings()
        )
        database = database_factory(config)
        app.state.database = database
        app.state.earliest_start_year = earliest_start_year(weather)
        try:
            await database.open()
            async with services_factory(database, weather) as services:
                app.state.services = services
                yield
        finally:
            await database.close()

    app = FastAPI(title="Climate Hazard Analyzer", lifespan=lifespan, debug=False)
    app.state.capacity = CapacityGuard(api.max_concurrent_analyses)
    limiters = {
        "analysis": RateLimiter(api.analysis_rate_per_minute),
        "search": RateLimiter(api.search_rate_per_minute),
    }
    app.add_middleware(
        RequestContextMiddleware, max_body_bytes=api.max_body_bytes, envelope=envelope
    )
    # Added last so it wraps every response, including errors from the middleware above.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(api.origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        expose_headers=["X-Request-ID", "Retry-After"],
        allow_credentials=False,
        max_age=600,
    )

    def enforce_rate(request: Request, kind: str) -> None:
        peer = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("x-forwarded-for")
        retry_after = limiters[kind].check(client_identity(peer, forwarded, api.trusted_proxy_hops))
        if retry_after is not None:
            raise RateLimited(retry_after)

    @app.exception_handler(DatabaseUnavailable)
    async def database_error(request: Request, exc: DatabaseUnavailable):
        return error_response(
            request, 503, "STORAGE_UNAVAILABLE", "Database temporarily unavailable"
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        details = validation_details(exc.errors())
        return error_response(request, 422, "VALIDATION_ERROR", "Request is invalid", details)

    @app.exception_handler(UnsupportedRequest)
    async def unsupported_request(request: Request, exc: UnsupportedRequest):
        return error_response(request, 422, exc.code, exc.message, exc.details)

    @app.exception_handler(InsufficientBaseline)
    async def insufficient_baseline(request: Request, exc: InsufficientBaseline):
        years = ", ".join(str(year) for year in exc.years)
        detail = ErrorDetail(field="baseline", message=f"Years below coverage gates: {years}")
        message = "Not enough valid 1991–2020 baseline data for this location"
        return error_response(request, 422, "INSUFFICIENT_BASELINE", message, [detail])

    @app.exception_handler(InsufficientData)
    async def insufficient_data(request: Request, exc: InsufficientData):
        message = "No requested year has enough valid daily data"
        return error_response(request, 422, "INSUFFICIENT_DATA", message)

    @app.exception_handler(SourcesFailed)
    async def sources_failed(request: Request, exc: SourcesFailed):
        details = [
            ErrorDetail(field="source", message=f"{PROVIDER_LABELS[provider]}: {kind}")
            for provider, kind in exc.failures
        ]
        if exc.timed_out:
            message = "The weather data provider did not respond in time"
            return error_response(request, 504, "UPSTREAM_TIMEOUT", message, details)
        message = "The weather data provider returned no usable data"
        return error_response(request, 502, "PROVIDER_ERROR", message, details)

    @app.exception_handler(ProviderError)
    async def provider_error(request: Request, exc: ProviderError):
        if exc.kind == "timeout":
            message = "The location search provider did not respond in time"
            return error_response(request, 504, "UPSTREAM_TIMEOUT", message)
        message = "The location search provider returned no usable data"
        return error_response(request, 502, "PROVIDER_ERROR", message)

    @app.exception_handler(SearchUnavailable)
    async def search_unavailable(request: Request, exc: SearchUnavailable):
        message = "Location search is not enabled; enter coordinates instead"
        return error_response(request, 503, "SEARCH_UNAVAILABLE", message, retryable=False)

    @app.exception_handler(RateLimited)
    async def rate_limited(request: Request, exc: RateLimited):
        response = error_response(request, 429, "RATE_LIMITED", "Too many requests; retry later")
        response.headers["Retry-After"] = str(exc.retry_after)
        return response

    @app.exception_handler(CapacityExceeded)
    async def capacity_exceeded(request: Request, exc: CapacityExceeded):
        message = "The service is busy with other analyses; retry shortly"
        return error_response(request, 503, "CAPACITY_EXCEEDED", message)

    @app.exception_handler(TimeoutError)
    async def analysis_timeout(request: Request, exc: TimeoutError):
        message = "The analysis exceeded its time budget"
        return error_response(request, 504, "ANALYSIS_TIMEOUT", message)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        code, message = HTTP_ERRORS.get(
            exc.status_code, ("HTTP_ERROR", "Request could not be completed")
        )
        response = error_response(request, exc.status_code, code, message)
        if exc.headers:
            response.headers.update(exc.headers)
        return response

    @app.get("/api/v1/health", response_model=Health)
    async def health(request: Request):
        return Health(earliest_start_year=request.app.state.earliest_start_year)

    @app.get("/api/v1/health/ready", response_model=Readiness)
    async def ready(request: Request):
        await request.app.state.database.ping()
        return Readiness()

    @app.post("/api/v1/analyses/heatwaves", response_model=AnalysisResponse)
    async def analyze(body: AnalysisRequest, request: Request):
        enforce_rate(request, "analysis")
        with app.state.capacity.slot() as acquired:
            if not acquired:
                raise CapacityExceeded()
            analysis = request.app.state.services.analysis
            return await analysis.analyze(body, request.state.request_id)

    @app.get("/api/v1/regions/search", response_model=RegionSearch)
    async def search_regions(request: Request, q: Annotated[SearchQuery, Query()]):
        enforce_rate(request, "search")
        return {"results": await request.app.state.services.regions.search(q)}

    return app
