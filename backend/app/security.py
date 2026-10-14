"""Request guards: request context, body/media limits, client identity, rate and capacity limits."""

import logging
import math
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

WINDOW_SECONDS = 60
logger = logging.getLogger("climate_hazard")


class RateLimited(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after


class CapacityExceeded(Exception):
    pass


class RateLimiter:
    """Fixed one-minute windows per client, with a bounded client map."""

    def __init__(
        self, limit: int, clock: Callable[[], float] = time.monotonic, max_clients: int = 10_000
    ):
        self.limit = limit
        self.clock = clock
        self.max_clients = max_clients
        self.windows: dict[str, tuple[float, int]] = {}

    def check(self, client: str) -> int | None:
        now = self.clock()
        start, count = self.windows.get(client, (now, 0))
        if now - start >= WINDOW_SECONDS:
            start, count = now, 0
        if count >= self.limit:
            return max(1, math.ceil(WINDOW_SECONDS - (now - start)))
        self.windows[client] = (start, count + 1)
        if len(self.windows) > self.max_clients:
            self.windows = {
                key: value for key, value in self.windows.items() if now - value[0] < WINDOW_SECONDS
            }
            while len(self.windows) > self.max_clients:
                del self.windows[next(iter(self.windows))]
        return None


class CapacityGuard:
    def __init__(self, size: int):
        self.available = size

    @contextmanager
    def slot(self) -> Iterator[bool]:
        if self.available <= 0:
            yield False
            return
        self.available -= 1
        try:
            yield True
        finally:
            self.available += 1


def client_identity(peer: str, forwarded_for: str | None, trusted_hops: int) -> str:
    # Forwarded addresses are spoofable unless a known number of proxies appended them.
    if trusted_hops and forwarded_for:
        hops = [part.strip() for part in forwarded_for.split(",") if part.strip()]
        if len(hops) >= trusted_hops:
            return hops[-trusted_hops]
    return peer


class RequestContextMiddleware:
    """Assigns request IDs, enforces JSON bodies and size, and contains unexpected errors."""

    def __init__(self, app: ASGIApp, max_body_bytes: int, envelope: Callable[..., dict]):
        self.app = app
        self.max_body_bytes = max_body_bytes
        self.envelope = envelope

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        started = False

        async def send_with_headers(message: Message) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id
                headers["Cache-Control"] = "no-store"
            await send(message)

        async def reject(status: int, code: str, message: str) -> None:
            body = self.envelope(request_id, status, code, message)
            await JSONResponse(body, status_code=status)(scope, receive, send_with_headers)

        headers = Headers(scope=scope)
        declared = headers.get("content-length")
        has_body = "transfer-encoding" in headers or declared not in (None, "0")
        if scope["method"] == "POST" and has_body:
            media_type = headers.get("content-type", "").split(";")[0].strip().lower()
            if media_type != "application/json":
                await reject(415, "UNSUPPORTED_MEDIA_TYPE", "Send the request body as JSON")
                return
            if declared is not None and (
                not declared.isdigit() or int(declared) > self.max_body_bytes
            ):
                await reject(413, "PAYLOAD_TOO_LARGE", "Request body is too large")
                return

        received = 0

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_body_bytes:
                    # FastAPI turns other body-read errors into 400s but passes HTTPException.
                    raise HTTPException(status_code=413)
            return message

        try:
            await self.app(scope, limited_receive, send_with_headers)
        except Exception:
            # Full detail stays in server logs; the client only sees the safe envelope.
            logger.exception(
                "Unhandled error request_id=%s method=%s path=%s",
                request_id, scope["method"], scope["path"],
            )
            if started:
                raise
            await reject(500, "INTERNAL_ERROR", "An unexpected error occurred")
