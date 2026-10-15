# Backend durable context

- User confirmed the initially empty workspace and later supplied private Atlas configuration plus a no-key NASA-first provider task. Never copy the URI; ignored local .env stores a pointer to the original file.
- The 85-concept documentation phase is complete. The latest request integrates the shared AI-development workflow after monochrome document alignment. Preserve draft connectivity code; this phase adds no business implementation.
- Python/FastAPI/PyMongo async/HTTPX dependencies are locally installed and uv-locked on Python 3.14.2. Deterministic tests must allow loopback sockets: Windows asyncio builds its self-pipe from a loopback pair, so a blanket socket.connect guard errors every async test.
- PyMongo 4.18.3 defers SRV/TXT lookup to the first operation and accepts `;` as a URI option separator. Keep the total deadline around awaited I/O only; the synchronous client constructor cannot be interrupted. The Atlas password was exposed earlier and must be rotated before any live attempt; no successful DB connection or schema write is verified.
- Both public NASA POWER and fixed ERA5 endpoints passed basic 1990–2020 no-key probes at one point. Adapters/fallback are absent; local non-commercial eligibility does not authorize unknown deployment use.
- One source/model/UTC convention must cover baseline and selected period. No mixing alternate values into gaps. Preserve provenance and source-specific cache identity.
- Contract 0.2 (user-approved ADR-017) replaced the ERA5-only source object; `SOURCE_PROFILES` in app/schemas.py is the backend copy of its provider table. NASA POWER v2.10.0 reports `sources` MERRA2/POWER, UTC, °C, fill −999 and echoes the requested point, so NASA `resolved` stays null.
- Pydantic 2.14 error text echoes input (union tags) and loc carries user-chosen keys even with hide_input_in_errors; API 422 details must stay fixed-message and path-sanitized. Its strip-whitespace string path already rejects lone surrogates.
- Provider transport is `ProviderHttp` (injected client, sleep, jitter). On Windows, pytest puts the test id in an env var capped at 32,767 chars, so huge parameters need explicit ids. httpx rejects non-ASCII header values.
- Fixed 1991–2020 all-season linear p95, strict exceedance, three-day runs, explicit year/month gates, cross-year/censoring rules remain unchanged; since heatwave-v2 the trend direction comes from a Mann-Kendall test with Sen's slope (ADR-025), with OLS kept for reference; methodology owns science.
- MongoDB persistence/readback remains mandatory for eventual analysis; no memory production substitute. No repositories/collections/indexes or climate engine exist.
- One worker initially; no Redis/queue/AI service. Deferred infrastructure has evidence-based review triggers in the decision register.
- The shared concept matrix and local task tracker own traceability; current state/evidence must be updated after each meaningful change. Independent Git and CI remain unconfigured.

- [The shared AI workflow](../../docs/ai-development-workflow.md) owns planning/research/architecture approval, verification/review/simplification and final evidence. Use focused TDD for science/validation/fallback/cache; separate live from mocked tests. No team plugin was installed. Installation needs explicit approval and an individual smoke test; existing task approvals persist for unchanged scope.
- FastAPI turns any non-HTTPException raised while reading a body into a 400, so the streaming size guard raises HTTPException(413). FastAPI's 500 handler sits outside CORS, so RequestContextMiddleware (inside CORS) contains unexpected errors.
- Serve with `uvicorn app.main:create_app --factory --no-proxy-headers`; importing the module performs no settings or network work.
- The local MongoDB 8.3.4 on 127.0.0.1:27017 holds the user's own databases (mydatabase, shop): never touch them. Tests use climate_hazard_test_* and drop them; local runs use climate_hazard_analyzer_dev.
