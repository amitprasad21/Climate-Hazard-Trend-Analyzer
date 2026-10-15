# Backend API implementation guide

**Implemented routes: GET /api/v1/health, GET /api/v1/health/ready, GET /api/v1/regions/search, POST /api/v1/analyses/heatwaves.** Schemas live in app/schemas.py and guards in app/security.py. Local-MongoDB runs are verified; live readiness against Atlas is pending BE-009. [Shared contract](../../INTEGRATION_CONTRACT.md) is the sole schema authority, including example requests, status codes, nullable fields, units, CORS, caching, limits and error envelope.

Planned: GET `/api/v1/health` (liveness), GET `/api/v1/regions/search` (bounded location lookup), POST `/api/v1/analyses/heatwaves` (synchronous analysis). No retrieval/job endpoint is needed. Point requests precede bbox support; unsupported bbox must return a typed 422 until implemented.

Generate FastAPI OpenAPI only after schemas/routes exist; verify it against the root contract. Do not hand-maintain a second divergent schema here. API fixtures must be labeled synthetic and never loaded by the production dashboard. Test both valid response invariants and safe errors, including errors from outside the application that are not JSON.

Route code translates domain failures; services orchestrate; provider/repository adapters own I/O. Full scientific rules belong in [methodology](climate-methodology.md), not route handlers or frontend chart functions.

Liveness returns the Health shape without DB/provider I/O, including `earliest_start_year`, computed once at startup from the enabled providers by the same function that words the `UNSUPPORTED_PERIOD` error (BE-012). The additive readiness draft performs a DB ping and returns status/api_version/database=available on success, or 503 STORAGE_UNAVAILABLE in the existing safe error envelope. It returns no host, database name, URI or trace. Startup itself requires a successful ping; after startup, readiness distinguishes a subsequent DB outage. No liveness pass proves storage is usable. BE-009 must test both paths and graceful closure.

Error architecture: request/schema failures become 422 with safe field paths; insufficient baseline/data remain domain 422; exhausted provider protocol/data failures become 502; storage/capacity become 503; elapsed deadline becomes 504; unexpected failures become safe 500. Details must not include Pydantic input objects, driver/provider messages or network settings. Preserve request ID and no-store on errors; CORS coverage is still planned. A failed DB write never returns successful climate data. BE-001/BE-008 test all envelopes, including 404/405 and gateway non-JSON handling at the client.

Contract 0.2 (DOC-004) defines truthful NASA POWER/ERA5 source metadata, enforced by `Source` in app/schemas.py; no analysis endpoint exists yet. The internal adapter result is not a second public API schema.
