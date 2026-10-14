"""Liveness, database readiness and the shared error envelope; analysis routes come later."""

from collections.abc import Sequence
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.database import Database, DatabaseUnavailable
from app.schemas import (
    ErrorBody,
    ErrorDetail,
    ErrorResponse,
    Health,
    Readiness,
    UnsupportedRequest,
    validation_details,
)
from app.settings import DatabaseSettings, load_database_settings, load_weather_settings


def error_response(
    request: Request,
    status: int,
    code: str,
    message: str,
    details: Sequence[ErrorDetail] = (),
) -> JSONResponse:
    error = ErrorBody(
        code=code,
        message=message,
        request_id=request.state.request_id,
        details=list(details),
        retryable=status == 503,
    )
    return JSONResponse(status_code=status, content=ErrorResponse(error=error).model_dump())


def create_app(settings: DatabaseSettings | None = None, database_factory=Database) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        config = settings if settings is not None else load_database_settings()
        if settings is None:
            load_weather_settings()  # Validate configuration, without provider calls at startup.
        database = database_factory(config)
        app.state.database = database
        try:
            await database.open()
            yield
        finally:
            await database.close()

    app = FastAPI(title="Climate Hazard Analyzer", lifespan=lifespan, debug=False)

    @app.middleware("http")
    async def response_metadata(request: Request, call_next):
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["Cache-Control"] = "no-store"
        return response

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

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        code, message = {
            404: ("NOT_FOUND", "Route not found"),
            405: ("METHOD_NOT_ALLOWED", "Method not allowed"),
        }.get(exc.status_code, ("HTTP_ERROR", "Request could not be completed"))
        response = error_response(request, exc.status_code, code, message)
        if exc.headers:
            response.headers.update(exc.headers)
        return response

    @app.get("/api/v1/health", response_model=Health)
    async def health():
        return Health()

    @app.get("/api/v1/health/ready", response_model=Readiness)
    async def ready(request: Request):
        await request.app.state.database.ping()
        return Readiness()

    return app


app = create_app()
