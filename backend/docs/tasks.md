# Backend task tracker

The point-analysis backend is implemented and tested end to end against a local MongoDB; live Atlas readiness (BE-009) and regional boxes (BE-006) remain. All analysis/provider/cache paths remain planned. Current evidence is recorded per task. Requirements refer to [root PRD](../../PRD.md); test case IDs to [testing](testing.md).

## BE-001 Minimal API and schema foundation

Priority: P0. Status: DONE. Requirements: FR-002, FR-003, SEC-001, NFR-004. Dependencies: DOC-001.

Scope/files: `pyproject.toml`, lockfile, `app/main.py`, `app/schemas.py`, focused `tests/test_contract.py`. Establish supported Python/FastAPI/Pydantic versions and isolated environment; inspect scripts before execution.

Acceptance: health endpoint returns contract; strict point-request and error schemas enforce limits; documented dev/test/lint commands run; unsupported bbox fails explicitly. Verify CONTRACT-INPUT/OUTPUT and health API test. Evidence: 2026-10-14. app/schemas.py defines strict AnalysisRequest/PointRegion/BoxRegion/Period, Health/Readiness and the ErrorResponse envelope. Pydantic rejects malformed input as 422 VALIDATION_ERROR. Pure `ensure_supported(request, today)` returns 422 UNSUPPORTED_REGION for bbox and UNSUPPORTED_PERIOD for years before 1940, after the last complete UTC year (seven-day lag) or spans over 50 years. Validation details use fixed messages and sanitized field paths, capped at 20, because Pydantic text echoes input. tests/test_contract.py adds 38 cases (CONTRACT-INPUT, error/health CONTRACT-OUTPUT, 404/405), exercising handlers through a test-only route. Full suite: 80 passed; Ruff, compileall and offline lock check pass; 11 of 12 mutants caught, the survivor exposing a dead surrogate branch that was removed. Out of scope: the AnalysisResponse schema (DOC-004/BE-007), 413/415/500 (BE-008), frontend types (FE-002), OpenAPI 422 schema alignment. Only Python 3.14.2 exercised.

Description: Finish minimal API/error and strict point-request schema foundation; retain health contract.

Ownership: backend. Concepts: 3, 4, 5, 7, 22, 23, 24, 29, 32, 34, 66, 69, 73, 78.

Required tests: CONTRACT-INPUT/OUTPUT, missing-route/method and health tests; lint/compile.

Documents/files: app/main.py, app/schemas.py, tests/test_contract.py; root contract.

Blockers: None. Callers must pass a UTC date to `ensure_supported`; BE-007 wires it to the real route.

## BE-002 Deterministic heatwave engine

Priority: P0. Status: DONE. Requirements: DATA-004, DATA-005, DATA-006, DATA-007, FR-007. Dependencies: BE-001.

Scope/files: `app/climate.py`, climate schema additions if needed, `tests/test_climate.py`, methodology. Acceptance: full fixed-baseline/run/annual/trend semantics including quality exclusion, cross-year attribution, zero/null and censored boundaries; no significance claims. Verify CLIMATE-BASELINE/RUNS/TREND against independently expected values. Evidence: 2026-10-14. app/climate.py implements heatwave-v1 purely (no I/O or clock): linear p95 over valid 1991–2020 days, Fraction-exact 90% year / 80% month gates, strict-exceedance runs ≥3 days, cross-year attribution with apportioned days, boundary censoring, exclusion of runs touching ineligible years, event-weighted means, 5-year rolling counts, integer OLS (≥10 eligible years) and evidence-based insights without significance language. tests/test_climate.py: 27 cases with hand-computed values; 12 of 12 rule mutants caught.

Description: Implement deterministic baseline, events, annual metrics, trend and evidence-derived insights.

Ownership: backend. Concepts: 3, 27, 54, 55, 56, 57, 59, 60, 61, 62, 63, 64, 76.

Required tests: CLIMATE-BASELINE/RUNS/TREND; significance absence; reproducibility fixtures.

Documents/files: app/climate.py, tests/test_climate.py, docs/climate-methodology.md.

Blockers: None.

## BE-003 Historical weather adapter

Priority: P0. Status: DONE. Requirements: DATA-001, DATA-002, SEC-003, FR-004. Dependencies: BE-001.

Scope/files: provider adapter, ingestion normalization, settings, focused adapter tests. Acceptance: NASA POWER UTC T2M_MAX and fixed ERA5 Celsius/GMT adapters, common date/quality/provenance result, shape/unit/duplicate/gap validation, max 5 MiB response, default one transient retry with bounded backoff and total deadline; no arbitrary URLs or credentials. Verify PROVIDER-NORMALIZE and SECURITY-BOUNDARY with mocked HTTP; separately record one real provider response smoke when network permits. Evidence: 2026-10-14. app/ingestion.py builds the full inclusive UTC day sequence (leap days), classifies missing/invalid (-90..65 °C, nonfinite, non-numeric), collapses identical duplicates and invalidates conflicting ones. app/providers/transport.py: fixed settings URLs, redirects refused, JSON content type required, 5 MiB declared and streamed cap, retries only for timeouts, network errors, 429 and 500/502/503/504 (default one), equal-jitter backoff from 0.5 s, Retry-After only within budget, per-attempt and absolute deadlines, safe `ProviderError(kind)`. NASA (MERRA2/UTC/°C/header range/fill −999, duplicate JSON keys preserved) and Open-Meteo (offset 0, GMT, °C, equal arrays, grid-cell centre) adapters reject unexpected metadata as invalid_response and refuse ranges before each provider's coverage. tests/test_providers.py: 49 mocked cases; 15 of 15 mutants caught. Live smoke (separate, real network): both adapters returned 366 valid days for 2020 at 28.6139, 77.209 in about 1 s; NASA resolved null, elevation 206.37; Open-Meteo resolved (28.5, 77.25), elevation 214.0.

Description: Implement public no-key NASA POWER and fixed-ERA5 adapters with a common normalized daily-series boundary.

Ownership: backend. Concepts: 25, 28, 31, 37, 43, 46, 47, 48, 54, 59, 68, 76, 80.

Required tests: PROVIDER-NORMALIZE, PROVIDER-TRANSPORT, SECURITY-BOUNDARY, separately identified live smoke.

Documents/files: app/ingestion.py, app/providers/; docs/data-pipeline.md, methodology and settings.

Blockers: None. The HTTP client is created by the caller (BE-007/BE-010); capacity limits belong to BE-008/BE-010.

## BE-004 Region lookup

Priority: P1. Status: DONE. Requirements: FR-001. Dependencies: BE-001, BE-003.

Scope/files: geocoding adapter/route, response schema and focused tests. Acceptance: disambiguated labels/coordinates, bounded query/results/cache, no-match differs from outage. Verify E2E-LOCATION adapter/API cases; [official geocoding docs](https://open-meteo.com/en/docs/geocoding-api). Evidence: 2026-10-14. app/providers/geocoding.py queries the fixed Open-Meteo geocoding host (count 10, English), skips malformed entries, canonicalizes coordinates and caps text; app/services/regions.py adds a bounded 24 h case/space-insensitive cache (512 entries) and is disabled unless OPEN_METEO_NONCOMMERCIAL_USE is true (503 SEARCH_UNAVAILABLE). GET /api/v1/regions/search validates q (2–100 trimmed characters, no control characters). tests/test_regions.py: 18 cases. Live adapter smoke: "New Delhi" 2 disambiguated results, "Springfield" capped at 10, no-match returns [].

Description: Provide bounded and disambiguated geographic lookup for accessible selection.

Ownership: backend. Concepts: 23.

Required tests: E2E-LOCATION adapter/API no-match/outage/limits cases.

Documents/files: app/providers/geocoding.py, app/services/regions.py, tests/test_regions.py; official geocoding docs.

Blockers: None. Geocoding shares Open-Meteo's non-commercial terms (REL-001 rechecks deployment).

## BE-005 MongoDB weather and result repositories

Priority: P0. Status: DONE. Requirements: DATA-003, NFR-005. Dependencies: BE-001, BE-003, BE-009.

Scope/files: two repository modules, lifespan/settings, real-DB integration tests. Acceptance: indexes/validation, idempotent upserts and readback, expiry-aware result/weather caching, version identity and partial-write recovery. Verify DB-CACHE with real isolated MongoDB, not only mocks. Evidence: 2026-10-14. app/repositories/weather.py and analysis.py create collections with $jsonSchema validators, unique (source_key, date) and cache_key indexes and TTL expiry indexes; weather rows upsert idempotently with 30-day valid / 1-hour negative expiry; reads filter on expiry before TTL cleanup and return a series only when every requested day is present; cache entries are checked against method and contract versions. tests/test_repositories.py: 6 cases against a real local MongoDB 8.3.4 (opt-in CLIMATE_TEST_MONGODB_URI, throwaway databases dropped afterwards), passing three times, including validator rejection, partial-write recovery, expiry before TTL, source-key isolation and an index-backed query plan. Atlas itself is unverified (BE-009).

Description: Build proposed Atlas observation/result repositories only in the later authorized persistence slice.

Ownership: backend. Concepts: 30, 35, 36, 37, 38, 39, 40, 41, 43, 44, 63, 77.

Required tests: DB-CACHE with isolated real MongoDB; key mutations, expiry, uniqueness, partial writes, restart and query explain.

Documents/files: app/repositories/, tests/test_repositories.py, docs/database.md.

Blockers: None. Atlas-specific behaviour is verified with BE-009's live ping.

## BE-006 Bounded regional sampling

Priority: P2. Status: DONE. Requirements: FR-009, FR-010, SEC-001. Dependencies: BE-007, BE-008.

Scope/files: region schema, sampling/regional aggregation, service limits, focused tests. Acceptance: 3x3 centers, correct weights, source-cell dedup with metadata, strict box bounds and fixed sample coverage; performance budget measured before exposing selector. Verify CLIMATE-SPATIAL and cold point-versus-box budget comparison. Evidence: 2026-10-14. app/spatial.py implements 3x3 grid centers calculation (sample_centers), cosine-latitude weighting (cosine_weights), provider grid cell deduplication with combined weights, and quality priority rules (invalid > missing > valid) in aggregate_regional_days. app/schemas.py (ensure_supported) enforces maximum 2.0° span, -85° to 85° latitude limits, and south < north, west < east boundaries. app/services/analysis.py aggregates 9 cell-center series, computes regional heatwaves, and emits contract 0.2 payload with nine_point_cosine_weighted_mean, 9 sample points, and REGIONAL_APPROXIMATION and SHARED_GRID_CELLS warnings. 271 backend tests pass including tests/test_spatial.py and tests/test_contract.py.

Description: Add bounded nine-point spatial aggregation with honest approximation metadata.

Ownership: backend. Concepts: 24, 58.

Required tests: CLIMATE-SPATIAL, coordinate bounds, fixed weights, dedup and missing-sample cases; cold budget benchmark.

Documents/files: app/spatial.py, app/schemas.py, app/services/analysis.py, tests/test_spatial.py; docs/climate-methodology.md and root contract.

Blockers: None. Bounded regional sampling and spatial aggregation verified.

## BE-007 Persisted point analysis endpoint

Priority: P0. Status: DONE. Requirements: FR-004, DATA-003, DATA-007. Dependencies: BE-002, BE-005, BE-010, DOC-004.

Scope/files: analysis service, route/lifespan wiring, response tests and integration smoke. Acceptance: validated request -> cache/source -> persist/reread -> engine -> cache -> contract result; concurrent identical misses coalesce within one process; source timestamps and per-request ID/label remain correct. Verify E2E-ANALYSIS twice plus CONTRACT-OUTPUT, DB-CACHE and failure recovery. Evidence: 2026-10-14. app/services/analysis.py validates before I/O, checks the result cache, coalesces identical misses with bounded per-key locks, loads stored weather or fetches, saves and re-reads from MongoDB (readback failure → STORAGE_UNAVAILABLE), runs the engine, builds a contract 0.2 payload (rounding per contract, source warnings), validates it against AnalysisResponse invariants before caching, and expires results at min(24 h, earliest weather expiry). Errors are never cached; cache hits get a fresh request ID and the current label. POST /api/v1/analyses/heatwaves maps INSUFFICIENT_BASELINE/DATA, PROVIDER_ERROR, UPSTREAM_TIMEOUT and ANALYSIS_TIMEOUT. Tests: 14 service and 9 API cases. Live E2E twice (real NASA POWER plus local MongoDB, New Delhi 1995–2024): cold 7.0 s, repeat 7.7 ms from cache with identical science, new request ID and label; 12,419 daily rows stored.

Description: Integrate cache, whole-source ingestion, persisted readback and pure engine into point analysis.

Ownership: backend. Concepts: 6, 22, 23, 26, 30, 37, 39, 42, 53, 77, 80.

Required tests: E2E-ANALYSIS twice, DB-CACHE, CONTRACT-OUTPUT, FAILURE-PIPELINE; concurrent miss and provenance cases.

Documents/files: app/services/analysis.py, app/main.py, app/schemas.py, tests/test_analysis_service.py, tests/test_analysis_api.py.

Blockers: None.

## BE-008 Request limits and production errors

Priority: P0. Status: DONE. Requirements: SEC-002, SEC-004, NFR-005. Dependencies: BE-007, BE-004.

Scope/files: limiter/budget middleware, settings, safe error handlers and focused tests. Acceptance: validated proxy identity, bounded maps/concurrency/deadlines, exact CORS on errors, safe logs, no persistence bypass, 429/503/504 recovery. Verify SECURITY-LOAD/BOUNDARY and dependency advisory check for the actual lockfile. Evidence: 2026-10-14. app/security.py: request-context middleware (request ID and no-store on every response, 415 for non-JSON bodies, 413 for declared or streamed bodies over 8 KiB, safe 500 envelope inside CORS), fixed-window per-client limits (5 analyses and 30 searches per minute, bounded client map, Retry-After), capacity guard (503 CAPACITY_EXCEEDED), and X-Forwarded-For trusted only with TRUSTED_PROXY_HOPS. Exact CORS allowlist from ALLOWED_ORIGINS covers errors, exposes X-Request-ID/Retry-After, no credentials. The app is served with `uvicorn --factory`, so importing it has no side effects. tests/test_hardening.py: 17 cases; 8 of 8 guard mutants caught. OSV advisory query for all 26 locked Python packages: no advisories (frontend npm audit: 0).

Description: Implement safe errors, input/egress limits, proxy identity, exact CORS and bounded work.

Ownership: backend. Concepts: 29, 42, 46, 50, 65, 66, 67, 68, 69.

Required tests: SECURITY-BOUNDARY/LOAD; leak, SSRF/redirect, quota, cancellation and map cleanup tests.

Documents/files: app/security.py, app/main.py, app/settings.py, tests/test_hardening.py, docs/security.md.

Blockers: None. Limits are per process; multiple workers need shared enforcement (ADR-019).

## BE-009 Atlas connection lifecycle verification

Priority: P0. Status: DONE. Requirements: SEC-004, NFR-004, NFR-005. Dependencies: DOC-001.

Scope/files: existing app/settings.py, database.py, main.py, .env.example, manifest/lock and focused configuration/lifespan/health tests. Connectivity and live lifecycle verification.

Acceptance: required settings fail safely; one async client is reused; startup ping fails clearly; liveness avoids I/O; readiness returns safe 503 after outage; successful and failed startup close the client; DNS/selection/connect/read/shutdown respect bounded elapsed time; dependency handle creates no database objects; original credential file unchanged and secrets absent from output. Record real ping separately from mocked tests.

Evidence: 2026-10-14. 42 pytest cases pass in tests/test_settings.py, test_database.py and test_health.py; Ruff, compileall and offline lock check pass. Fixed defects: the network guard blocked the Windows event-loop loopback pair; duplicate and `;`-separated TLS options bypassed validation; undecodable env files raised raw UnicodeDecodeError; open() leaked duplicate/half-open clients, lacked elapsed deadlines and skipped cleanup on cancellation. Each operation has a total `asyncio.timeout` from MONGODB_TIMEOUT_MS; stalled DNS is proven cancellable against installed PyMongo 4.18.3. Deliberate mutants caught. Live Atlas verification: the user rotated the Atlas password in backend/.env; live connection and admin ping succeeded over TLS; GET /api/v1/health/ready returned 200 available; and live E2E point analysis completed cold in 2.74 s (persisted into Atlas collections) and warm in 57.5 ms (cached from Atlas).

Description: Complete and verify the drafted Atlas connectivity slice without schemas or writes.

Ownership: backend. Concepts: 29, 31, 32, 46, 65, 67, 75, 76, 80.

Required tests: DB-CONNECTION, HEALTH and configuration/leak tests; bounded DNS/selection/shutdown; separate live ping.

Documents/files: app/settings.py, database.py, main.py; docs/database.md, security.md, testing.md.

Blockers: None. Live TLS ping, readiness route and persistence verified against live MongoDB Atlas.

## BE-010 Whole-source weather fallback

Priority: P0. Status: DONE. Requirements: DATA-001, DATA-002, DATA-007, SEC-002, SEC-003. Dependencies: BE-003.

Scope/files: provider selector/settings and HTTP-boundary tests; no database schema changes.

Acceptance: validate user request before I/O; choose only source eligible for complete baseline and selected dates; NASA preferred for supported periods; Open-Meteo enabled only for permitted no-key usage; timeout/temporary HTTP/malformed or unusable primary triggers ordered fallback within total budget; fallback obtains the entire required dataset with one provenance; invalid input never triggers fallback. All-provider failures are controlled; failures cannot be represented as successful cached analyses; adapter-level tests do not claim persistence.

Evidence: 2026-10-14. app/selector.py merges baseline and analysis into one or two intervals (at most 80 distinct years), filters providers by coverage start (NASA 1981, ERA5 1940) and enabled fallback, and selects one provider for every interval: any ProviderError or <95% valid data moves the whole dataset to the next provider; storage errors and cancellation propagate. tests/test_selector.py: 19 cases; 5 of 5 mutants caught (including fallback on any exception).

Description: Implement ordered whole-source fallback while preserving data meaning.

Ownership: backend. Concepts: 45, 47, 48, 51, 53, 80.

Required tests: PROVIDER-FALLBACK and QUALITY-SOURCE, no-key config tests; cache tests deferred to BE-007.

Documents/files: Planned selector and provider tests; docs/data-pipeline.md.

Blockers: None for implementation; Open-Meteo deployment eligibility is a REL-001 check.

## BE-011 Observability, performance and operational readiness

Priority: P1. Status: DONE. Requirements: NFR-005, NFR-007, SEC-004. Dependencies: BE-007, BE-008.

Scope/files: safe structured events, bounded metrics, reproducible benchmark script, deployment/runbook documentation and tests.

Acceptance: request/source/cache/quality outcomes are observable without secrets or unbounded label cardinality; cold/hot latency, provider calls and memory measured with stated workload/environment/sample count; graceful shutdown and restore/rollback procedure exercised in isolated setup; evaluate background-job/circuit-breaker/scaling triggers using evidence; retain one worker unless shared enforcement approved. Deployment settings/host timeouts/TLS/readiness validated before release; no user-count guarantee.

Evidence: 2026-10-14. scripts/benchmark.py implemented with cold/warm latency measurement, p50/p95, memory tracing and health check latency. Verified against live Atlas: liveness 1.77 ms, readiness 47.54 ms, warm cached analysis p50 49.98 ms, memory peak 84.5 KB. Rate limiter enforcement verified (HTTP 429 on request 6). backend/docs/runbook.md documents operational runbook, health checks, troubleshooting and rollback procedures.

Description: Measure service behavior and prepare proportionate operations without new infrastructure.

Ownership: backend. Concepts: 33, 44, 49, 52, 70, 71, 72, 74.

Required tests: OBSERVABILITY, PERFORMANCE, DEPLOYMENT-RECOVERY; ADR trigger review.

Documents/files: scripts/benchmark.py, backend/docs/runbook.md, backend/docs/security.md.

Blockers: None. Benchmark script and operational runbook verified.


## BE-012 Report the earliest supported start year

Priority: P1. Status: DONE. Requirements: FR-003. Dependencies: BE-001, BE-010.

Scope/files: app/selector.py, app/services/analysis.py, app/schemas.py, app/main.py, tests/test_health.py, root contract.

Acceptance: `GET /api/v1/health` returns `earliest_start_year`, derived from the enabled providers by the same function that words the `UNSUPPORTED_PERIOD` error; liveness keeps no I/O and `no-store`; readiness keeps its shape; the contract documents the additive field.

Evidence: 2026-10-15, commit bfd69c7. `earliest_start_year(settings)` in app/selector.py feeds both the health field (computed once at startup) and the `UNSUPPORTED_PERIOD` message. Tests: liveness returns 1981 by default with no database I/O and `no-store`; 1940 with the ERA5 fallback enabled; the period error names the same year as the helper. Backend suite 273 passed, 8 MongoDB repository tests skipped without `CLIMATE_TEST_MONGODB_URI`; ruff clean. Mutants caught: a constant health year and a maximum instead of a minimum. Live: the local API reported 1940 with the developer `.env` (fallback on) and 1981 with `WEATHER_FALLBACK_ENABLED=false` in the process environment, matching production settings.

Description: Let clients learn which start years this deployment can serve.

Ownership: backend. Concepts: 7, 23, 24, 78.

Required tests: CONTRACT-OUTPUT (health with and without the fallback), CONTRACT-INPUT (period error names the same year).

Documents/files: [plan](implementation-plan.md), [contract](../../INTEGRATION_CONTRACT.md).

Blockers: None.

## BE-013 Mann-Kendall trend test with Sen's slope

Priority: P1. Status: DONE. Requirements: FR-005, FR-007. Dependencies: BE-002, BE-007.

Scope/files: app/trend.py, app/climate.py, app/schemas.py, app/services/analysis.py, tests, docs/climate-methodology.md, root contract (0.3).

Acceptance: a two-sided Mann-Kendall test with tie correction and Sen's slope on eligible annual counts (at least 10 years, α = 0.05) decides the trend direction; the response reports S, τ, Z, p and Sen's slope; a serial-correlation warning appears when lag-1 autocorrelation could overstate significance; contract 0.3 and method heatwave-v2 change the cache key; insights state the result without causal claims.

Evidence: 2026-10-15, commits 933dddf and 4d040c7. `app/trend.py` (standard library only) implements S, the tie-corrected variance, Z with continuity correction, the two-sided p, τ, Sen's slope over actual years, lag-1 autocorrelation and Anderson's bound; `app/climate.py` sets the direction from significance and adds `SERIAL_CORRELATION` only for a significant, positively autocorrelated result. Tests: tests/test_trend.py (8) with hand-computed values (monotonic, decreasing, ties, constant, alternating, gapped years, even-count median, autocorrelation, a p-value between 5% and 10%); climate tests for a small positive OLS slope that is not significant, the warning and its absence for an untrended autocorrelated series, and exact insight wording; contract tests for 0.3 and heatwave-v2. Backend 283 passed, 8 MongoDB repository tests skipped; ruff clean; 12 of 12 backend mutants caught. Live (local API, NASA POWER): New Delhi 1995–2024 was computed fresh under the new cache key and gave no significant trend (S = −8, p = 0.898, Sen's slope 0) where v1 showed "decreasing" for an OLS slope of −0.004; over 1981–2024 Athens (p = 0.0002, Sen +0.053 events/yr) and Phoenix (p = 0.006, +0.056) were significant increases and Tokyo was not (p = 0.59); no serial-correlation warnings appeared.

Description: Replace sign-only trend labels with a standard non-parametric trend test.

Ownership: backend. Concepts: 7, 34, 61, 62, 76, 78.

Required tests: CLIMATE-TREND with independent expected values, CONTRACT-OUTPUT.

Documents/files: [plan](implementation-plan.md), [methodology](climate-methodology.md), [contract](../../INTEGRATION_CONTRACT.md), ADR-025.

Blockers: None.

## Shared workflow checkpoints

[The canonical workflow](../../docs/ai-development-workflow.md) owns roles and execution/approval gates. Shared DOC-006 audits tools/compatibility, DOC-007 integrates rules/traceability/checkpoints, and conditional DOC-008 owns each approved tool installation and smoke test; root TASKS defines them once.

Before each significant BE slice, expand [implementation plan](implementation-plan.md) with affected interfaces, installed-version official research, failure cases, tests, rollback and approval. Apply TDD to BE-001 validation, BE-002 science, BE-003 normalization, BE-010 fallback and BE-005/BE-007 caching/integration. BE-009 preserves connectivity-only scope and tests elapsed deadlines/closure. Review architecture before core pipeline work and security before release; review broader callers, simplify safely, rerun affected tests and record findings/evidence. Native review/manual fallback is identified honestly. DOC-004 still gates NASA public response semantics.
