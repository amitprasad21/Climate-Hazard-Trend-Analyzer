# Backend task tracker

Only settings, database lifecycle and health routes have code; their deterministic tests pass, while live Atlas readiness is unverified. All analysis/provider/cache paths remain planned. Current evidence is recorded per task. Requirements refer to [root PRD](../../PRD.md); test case IDs to [testing](testing.md).

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

Priority: P0. Status: TODO. Requirements: DATA-004, DATA-005, DATA-006, DATA-007, FR-007. Dependencies: BE-001.

Scope/files: `app/climate.py`, climate schema additions if needed, `tests/test_climate.py`, methodology. Acceptance: full fixed-baseline/run/annual/trend semantics including quality exclusion, cross-year attribution, zero/null and censored boundaries; no significance claims. Verify CLIMATE-BASELINE/RUNS/TREND against independently expected values. Evidence: none.

Description: Implement deterministic baseline, events, annual metrics, trend and evidence-derived insights.

Ownership: backend. Concepts: 3, 27, 54, 55, 56, 57, 59, 60, 61, 62, 63, 64, 76.

Required tests: CLIMATE-BASELINE/RUNS/TREND; significance absence; reproducibility fixtures.

Documents/files: app/climate.py, docs/climate-methodology.md, planned tests/test_climate.py.

Blockers: Depends on validated schemas; no numerical code exists.

## BE-003 Historical weather adapter

Priority: P0. Status: DONE. Requirements: DATA-001, DATA-002, SEC-003, FR-004. Dependencies: BE-001.

Scope/files: provider adapter, ingestion normalization, settings, focused adapter tests. Acceptance: NASA POWER UTC T2M_MAX and fixed ERA5 Celsius/GMT adapters, common date/quality/provenance result, shape/unit/duplicate/gap validation, max 5 MiB response, default one transient retry with bounded backoff and total deadline; no arbitrary URLs or credentials. Verify PROVIDER-NORMALIZE and SECURITY-BOUNDARY with mocked HTTP; separately record one real provider response smoke when network permits. Evidence: 2026-10-14. app/ingestion.py builds the full inclusive UTC day sequence (leap days), classifies missing/invalid (-90..65 °C, nonfinite, non-numeric), collapses identical duplicates and invalidates conflicting ones. app/providers/transport.py: fixed settings URLs, redirects refused, JSON content type required, 5 MiB declared and streamed cap, retries only for timeouts, network errors, 429 and 500/502/503/504 (default one), equal-jitter backoff from 0.5 s, Retry-After only within budget, per-attempt and absolute deadlines, safe `ProviderError(kind)`. NASA (MERRA2/UTC/°C/header range/fill −999, duplicate JSON keys preserved) and Open-Meteo (offset 0, GMT, °C, equal arrays, grid-cell centre) adapters reject unexpected metadata as invalid_response and refuse ranges before each provider's coverage. tests/test_providers.py: 49 mocked cases; 15 of 15 mutants caught. Live smoke (separate, real network): both adapters returned 366 valid days for 2020 at 28.6139, 77.209 in about 1 s; NASA resolved null, elevation 206.37; Open-Meteo resolved (28.5, 77.25), elevation 214.0.

Description: Implement public no-key NASA POWER and fixed-ERA5 adapters with a common normalized daily-series boundary.

Ownership: backend. Concepts: 25, 28, 31, 37, 43, 46, 47, 48, 54, 59, 68, 76, 80.

Required tests: PROVIDER-NORMALIZE, PROVIDER-TRANSPORT, SECURITY-BOUNDARY, separately identified live smoke.

Documents/files: app/ingestion.py, app/providers/; docs/data-pipeline.md, methodology and settings.

Blockers: None. The HTTP client is created by the caller (BE-007/BE-010); capacity limits belong to BE-008/BE-010.

## BE-004 Region lookup

Priority: P1. Status: TODO. Requirements: FR-001. Dependencies: BE-001, BE-003.

Scope/files: geocoding adapter/route, response schema and focused tests. Acceptance: disambiguated labels/coordinates, bounded query/results/cache, no-match differs from outage. Verify E2E-LOCATION adapter/API cases; [official geocoding docs](https://open-meteo.com/en/docs/geocoding-api). Evidence: none.

Description: Provide bounded and disambiguated geographic lookup for accessible selection.

Ownership: backend. Concepts: 23.

Required tests: E2E-LOCATION adapter/API no-match/outage/limits cases.

Documents/files: Planned geocoding adapter/route; docs/API.md and official geocoding docs.

Blockers: API foundation and adapter boundary pending; live geocoding not verified.

## BE-005 MongoDB weather and result repositories

Priority: P0. Status: TODO. Requirements: DATA-003, NFR-005. Dependencies: BE-001, BE-003, BE-009.

Scope/files: two repository modules, lifespan/settings, real-DB integration tests. Acceptance: indexes/validation, idempotent upserts and readback, expiry-aware result/weather caching, version identity and partial-write recovery. Verify DB-CACHE with real isolated MongoDB, not only mocks. Evidence: no persistence tests; credentials were supplied but live connectivity failed. No collections or indexes created.

Description: Build proposed Atlas observation/result repositories only in the later authorized persistence slice.

Ownership: backend. Concepts: 30, 35, 36, 37, 38, 39, 40, 41, 43, 44, 63, 77.

Required tests: DB-CACHE with isolated real MongoDB; key mutations, expiry, uniqueness, partial writes, restart and query explain.

Documents/files: Planned app/repositories/; docs/database.md and data-pipeline.md.

Blockers: Successful Atlas connectivity and isolated test database required; supplied credentials are not permission for schema creation in this phase.

## BE-006 Bounded regional sampling

Priority: P2. Status: TODO. Requirements: FR-009, FR-010, SEC-001. Dependencies: BE-007, BE-008.

Scope/files: region schema, sampling/regional aggregation, service limits, focused tests. Acceptance: 3x3 centers, correct weights, source-cell dedup with metadata, strict box bounds and fixed sample coverage; performance budget measured before exposing selector. Verify CLIMATE-SPATIAL and cold point-versus-box budget comparison. Evidence: none.

Description: Add bounded nine-point spatial aggregation with honest approximation metadata.

Ownership: backend. Concepts: 24, 58.

Required tests: CLIMATE-SPATIAL, coordinate bounds, fixed weights, dedup and missing-sample cases; cold budget benchmark.

Documents/files: Planned region schema/sampler; docs/climate-methodology.md and root contract.

Blockers: Point flow and resource safeguards must pass first.

## BE-007 Persisted point analysis endpoint

Priority: P0. Status: TODO. Requirements: FR-004, DATA-003, DATA-007. Dependencies: BE-002, BE-005, BE-010, DOC-004.

Scope/files: analysis service, route/lifespan wiring, response tests and integration smoke. Acceptance: validated request -> cache/source -> persist/reread -> engine -> cache -> contract result; concurrent identical misses coalesce within one process; source timestamps and per-request ID/label remain correct. Verify E2E-ANALYSIS twice plus CONTRACT-OUTPUT, DB-CACHE and failure recovery. Evidence: none.

Description: Integrate cache, whole-source ingestion, persisted readback and pure engine into point analysis.

Ownership: backend. Concepts: 6, 22, 23, 26, 30, 37, 39, 42, 53, 77, 80.

Required tests: E2E-ANALYSIS twice, DB-CACHE, CONTRACT-OUTPUT, FAILURE-PIPELINE; concurrent miss and provenance cases.

Documents/files: Planned app/services/analysis.py, analysis route/repositories; docs/data-pipeline.md.

Blockers: Engine, repositories, fallback and approved source contract are prerequisites.

## BE-008 Request limits and production errors

Priority: P0. Status: TODO. Requirements: SEC-002, SEC-004, NFR-005. Dependencies: BE-007, BE-004.

Scope/files: limiter/budget middleware, settings, safe error handlers and focused tests. Acceptance: validated proxy identity, bounded maps/concurrency/deadlines, exact CORS on errors, safe logs, no persistence bypass, 429/503/504 recovery. Verify SECURITY-LOAD/BOUNDARY and dependency advisory check for the actual lockfile. Evidence: none.

Description: Implement safe errors, input/egress limits, proxy identity, exact CORS and bounded work.

Ownership: backend. Concepts: 29, 42, 46, 50, 65, 66, 67, 68, 69.

Required tests: SECURITY-BOUNDARY/LOAD; leak, SSRF/redirect, quota, cancellation and map cleanup tests.

Documents/files: Planned middleware/limiter/error handlers; docs/security.md.

Blockers: Core point and lookup paths pending; no production hardening claim.

## BE-009 Atlas connection lifecycle verification

Priority: P0. Status: BLOCKED. Requirements: SEC-004, NFR-004, NFR-005. Dependencies: DOC-001.

Scope/files: existing app/settings.py, database.py, main.py, .env.example, manifest/lock and focused configuration/lifespan/health tests. Connectivity only; no collections, indexes or document models.

Acceptance: required settings fail safely; one async client is reused; startup ping fails clearly; liveness avoids I/O; readiness returns safe 503 after outage; successful and failed startup close the client; DNS/selection/connect/read/shutdown respect bounded elapsed time; dependency handle creates no database objects; original credential file unchanged and secrets absent from output. Record real ping separately from mocked tests.

Evidence: 2026-10-14, mocked/deterministic only. 42 pytest cases pass in tests/test_settings.py, test_database.py and test_health.py; Ruff, compileall and offline lock check pass. Fixed defects: the network guard blocked the Windows event-loop loopback pair (all async tests errored); duplicate and `;`-separated TLS options bypassed validation; undecodable env files raised raw UnicodeDecodeError; open() leaked duplicate/half-open clients, lacked elapsed deadlines and skipped cleanup on cancellation. Each operation now has a total `asyncio.timeout` from MONGODB_TIMEOUT_MS; stalled DNS is proven cancellable against the real installed PyMongo 4.18.3 with mocked dnspython. Five deliberate mutants were each caught. 25 repeated runs (cold and under CPU load) passed. Earlier live Atlas ping failed with network_or_availability; no live attempt this session.

Description: Complete and verify the drafted Atlas connectivity slice without schemas or writes.

Ownership: backend. Concepts: 29, 31, 32, 46, 65, 67, 75, 76, 80.

Required tests: DB-CONNECTION, HEALTH and configuration/leak tests; bounded DNS/selection/shutdown; separate live ping.

Documents/files: app/settings.py, database.py, main.py; docs/database.md, security.md, testing.md.

Blockers: Live read-only ping only. Next action: the user rotates the previously exposed Atlas password and confirms the Atlas network access list for this machine, then run one ping and record it separately.

## BE-010 Whole-source weather fallback

Priority: P0. Status: TODO. Requirements: DATA-001, DATA-002, DATA-007, SEC-002, SEC-003. Dependencies: BE-003.

Scope/files: provider selector/settings and HTTP-boundary tests; no database schema changes.

Acceptance: validate user request before I/O; choose only source eligible for complete baseline and selected dates; NASA preferred for supported periods; Open-Meteo enabled only for permitted no-key usage; timeout/temporary HTTP/malformed or unusable primary triggers ordered fallback within total budget; fallback obtains the entire required dataset with one provenance; invalid input never triggers fallback. All-provider failures are controlled; failures cannot be represented as successful cached analyses; adapter-level tests do not claim persistence.

Evidence: both adapters exist and are tested (BE-003); no selector exists. Cache-reuse and failure-not-cached integration acceptance belongs to BE-007 after repositories/engine exist.

Description: Implement ordered whole-source fallback while preserving data meaning.

Ownership: backend. Concepts: 45, 47, 48, 51, 53, 80.

Required tests: PROVIDER-FALLBACK and QUALITY-SOURCE, no-key config tests; cache tests deferred to BE-007.

Documents/files: Planned selector and provider tests; docs/data-pipeline.md.

Blockers: None for implementation; free Open-Meteo eligibility must be rechecked for any deployment.

## BE-011 Observability, performance and operational readiness

Priority: P1. Status: TODO. Requirements: NFR-005, NFR-007, SEC-004. Dependencies: BE-007, BE-008.

Scope/files: safe structured events, bounded metrics, reproducible benchmark script, deployment/runbook documentation and tests.

Acceptance: request/source/cache/quality outcomes are observable without secrets or unbounded label cardinality; cold/hot latency, provider calls and memory measured with stated workload/environment/sample count; graceful shutdown and restore/rollback procedure exercised in isolated setup; evaluate background-job/circuit-breaker/scaling triggers using evidence; retain one worker unless shared enforcement approved. Deployment settings/host timeouts/TLS/readiness validated before release; no user-count guarantee.

Evidence: none; no telemetry, benchmark or deployment is implemented.

Description: Measure service behavior and prepare proportionate operations without new infrastructure.

Ownership: backend. Concepts: 33, 44, 49, 52, 70, 71, 72, 74.

Required tests: OBSERVABILITY, PERFORMANCE, DEPLOYMENT-RECOVERY; ADR trigger review.

Documents/files: docs/security.md/testing.md and planned telemetry/benchmark/config modules.

Blockers: No integrated application or chosen deployment host to measure.


## Shared workflow checkpoints

[The canonical workflow](../../docs/ai-development-workflow.md) owns roles and execution/approval gates. Shared DOC-006 audits tools/compatibility, DOC-007 integrates rules/traceability/checkpoints, and conditional DOC-008 owns each approved tool installation and smoke test; root TASKS defines them once.

Before each significant BE slice, expand [implementation plan](implementation-plan.md) with affected interfaces, installed-version official research, failure cases, tests, rollback and approval. Apply TDD to BE-001 validation, BE-002 science, BE-003 normalization, BE-010 fallback and BE-005/BE-007 caching/integration. BE-009 preserves connectivity-only scope and tests elapsed deadlines/closure. Review architecture before core pipeline work and security before release; review broader callers, simplify safely, rerun affected tests and record findings/evidence. Native review/manual fallback is identified honestly. DOC-004 still gates NASA public response semantics.
