# Security, configuration and error handling

Implemented settings are limited to database/weather configuration in app/settings.py; controls below remain planned unless explicitly identified. Local .env points to an existing private credential file without copying secrets. There is no public listener or deployment. Use [contract](../../INTEGRATION_CONTRACT.md) for input/status/error semantics and [pipeline](data-pipeline.md) for retry/cache behavior.

## Trust boundaries and resource control

- Reject unknown fields, nonfinite/numeric-string coordinates, overlong/control-character labels, malformed/reversed dates, unsupported hazards, excessive ranges and boxes. Max JSON body 8 KiB.
- Only fixed NASA POWER, Open-Meteo archive and approved geocoding hosts may be fetched. Construct query parameters with the HTTP client. No user-provided URL, redirect-to-private-host, raw Mongo filter or operator is accepted. Disable redirects; cap streamed/decompressed response bytes as well as declared Content-Length.
- Use 5 analyses/minute/client and 30 searches/minute/client initially, a bounded process-wide upstream semaphore and a provider call budget. HTTP 429 includes Retry-After. Client identity comes from the socket unless a trusted deployment proxy is configured; do not trust arbitrary X-Forwarded-For.
- Run one worker until shared quota/duplicate-work protection is designed. An IP limit is approximate behind NAT and not an identity system. CORS alone is not abuse prevention.
- Expose sanitized errors with request IDs. Exception traces stay in controlled server logs; never log keys, connection strings, raw payloads or full credential-bearing URLs. Normalize FastAPI/Pydantic validation errors without echoing input.
- Escape provider/user text through React; do not render raw HTML. Source links must use configured HTTPS addresses. Review dependency advisories after lockfiles exist, without unrelated upgrades or disabling checks.

## Settings inventory

| Variable | Required/default | Purpose / current status |
|---|---|---|
| `APP_ENV` | development | development/test/production validation |
| `MONGODB_URI` | required for runtime; no checked-in value | Server-side database connection |
| `MONGODB_DATABASE` | climate_hazard_analyzer | Restricted application database; setting exists |
| `MONGODB_ENV_FILE` | optional existing private file path | Only reads MONGODB_URI when not otherwise supplied; no secret copying |
| `MONGODB_TIMEOUT_MS` | 5000; range 100–30000 | Driver selection/connect/socket/wait-queue/operation timeout; elapsed DNS behavior still requires tests |
| `ALLOWED_ORIGINS` | explicit local frontend origin in development | Exact origins; production requires explicit list |
| `LOG_LEVEL` | INFO | No sensitive debug dumps |
| `WEATHER_PRIMARY_PROVIDER` | nasa_power | Existing selection setting; selector implementation pending |
| `WEATHER_FALLBACK_PROVIDERS` | open_meteo | Comma-separated known provider names; no arbitrary endpoint |
| `WEATHER_FALLBACK_ENABLED` | false by default/example; true in local assessment .env | Enable only after access/usage verification |
| `OPEN_METEO_NONCOMMERCIAL_USE` | false by default; true for local assessment | Required when selecting the free Open-Meteo service; not proof of deployment entitlement |
| `NASA_POWER_BASE_URL` / `NASA_POWER_TIME_STANDARD` | fixed daily point endpoint / UTC | Literal allowlist settings |
| `OPEN_METEO_BASE_URL` / `OPEN_METEO_MODEL` | fixed archive endpoint / era5 | Literal allowlist settings |
| `WEATHER_PROVIDER_TIMEOUT_SECONDS` | 10; bounded 0.1–30 | Proposed adapter attempt deadline; setting exists |
| `WEATHER_PROVIDER_MAX_RETRIES` | 1; bounded 0–2 | Transient retries only; setting exists |
| `WEATHER_TOTAL_TIMEOUT_SECONDS` | 60; bounded 1–90 | Entire selection budget, capped by remaining service deadline |
| `WEATHER_MIN_COVERAGE_PERCENT` | 95; bounded 95–100 | Additional adapter gate, not a substitute for baseline/month/year quality |
| `ANALYSIS_TIMEOUT_SECONDS` | 90, bounded | Total request deadline |
| `UPSTREAM_CONCURRENCY` | 2, bounded | Shared source-request cap |
| `ANALYSIS_RATE_PER_MINUTE` | 5, bounded | Per-client request limit |
| `SEARCH_RATE_PER_MINUTE` | 30, bounded | Geocoding protection |
| `PROVIDER_DAILY_CALL_BUDGET` | 500, conservative provisional | Stop new outbound work before operator budget |

Startup code validates database/weather settings and attempts a ping. Origin/rate/log/analysis-limit settings in the table remain planned for BE-008/BE-011; do not claim they are enforced yet. [.env.example](../.env.example) exists and contains placeholders only. Root/backend ignore rules exclude .env variants, credential files, keys, virtual environments and caches. No Git repository exists, so repository-specific ignore/secret checks remain a future gate. Process environment overrides local .env; private-file URI is a fallback only. Dotenv interpolation is disabled and only the URI is taken from the external file. Do not enable debug dumps or echo configuration errors with input values. Test settings must use isolated resources, never automatic writes through supplied production credentials.

No weather API-key setting or paid provider is supported. Do not add one as a workaround for unavailable free fallback. Never print connection strings in troubleshooting; safe failure categories and private checks are in [database](database.md).

Free-provider limits and permitted use must be checked before deployment. The [official terms](https://open-meteo.com/en/terms) currently describe non-commercial use and call limits; historical/multi-location work can incur weighted usage. Our conservative call counter is not proof of provider-billing equivalence. Obtain actual deployment entitlement/budget before opening a public service.

## Failure handling and deployment

Input/data-quality errors are user-correctable 422 responses; provider/protocol failure is 502; storage/capacity failure is 503; deadline failure is 504; unexpected errors return safe 500. No result is returned after a failed required persistence write. No silent fallback to synthetic data.

Local development binds loopback. Public deployment requires TLS, origin restrictions, protected MongoDB networking/least-privilege user, request limits and tested host timeouts. Do not provision accounts, expose listeners or run gateways automatically. Authentication is outside current product scope; add it only if actual deployment requirements change.

## Observability and performance policy

BE-011 owns implementation. Emit structured events with server-generated request ID, route template, elapsed milliseconds, outcome code, cache hit/miss, fixed provider name, retry count and valid/missing/invalid totals. Source retrieval timestamps/fingerprints support reproducibility. Never log URI, credentials, request bodies, raw provider errors or private paths. Do not put region labels, coordinates, request IDs or arbitrary error strings into metric labels; bounded dimensions are route/provider/status class.

Observe p50/p95 latency, active/waiting work, cache hit ratio, source failures/timeouts/429s, DB failures, invalid-day counts and storage size. Begin with process logs/counters; no telemetry vendor or background monitoring service is required. Observe provider health from actual requests and occasional explicit smoke checks. No periodic probe schedule is authorized by this plan.

Initial targets from PRD are hypotheses: hot p95 under 1s at five concurrent clients, cold completion within 90s, frontend compressed JS under 250 KiB excluding optional map chunks. Measure first/repeated point requests across representative 1/30/50-year periods with known baseline cache state, hardware/runtime, network context and at least a stated sample count. Report failures and source-call spend alongside latency; do not exclude failures to improve percentiles. Later box tests must disclose number of unique source series. Benchmarks must stay within provider quotas; use deterministic fixtures for stress and a small real smoke for integration.

Circuit breaker, queues and replicas are deferred under ADR-018/ADR-019. Revisit only after repeated measured outage cost/deadline failures or a demonstrated capacity bottleneck. Multiple workers require shared/edge limits and duplicate-work coordination first. No traffic capacity or production readiness is currently verified.

## Deployment and recovery plan

REL-001 selects hosting and rechecks free-service terms, quotas, cold starts and timeouts; BE-011 supplies a runbook. Build a static frontend and one FastAPI worker, inject server secrets, terminate verified TLS, set exact origins and trust proxy headers only from the configured ingress. Host/proxy timeout must accommodate the bounded API response without multiplying retries. Restrict Atlas access to intended clients and least-privilege database roles.

Separate liveness from DB readiness; startup failure prevents serving. Test graceful cancellation/closure under shutdown; a health response is not an end-to-end analysis check. Keep previous deployable artifacts and configuration revision for rollback. Before schema implementation, agree isolated test DB, backup/restore ownership and migration/rollback procedure; test restore in isolation before claiming recoverability. No production schema, account, network rule or deployment is changed during this documentation phase.
