# Backend verification plan

**Deterministic DB-CONNECTION, HEALTH, configuration, CONTRACT-INPUT, source-schema, PROVIDER-NORMALIZE and PROVIDER-TRANSPORT tests pass (142 cases, 2026-10-14). No selector, cache, climate or end-to-end suite exists.** Provider tests use `httpx.MockTransport`; the separate live smoke is recorded in [tasks](tasks.md) BE-003. The autouse fixture in tests/conftest.py permits only loopback sockets (Windows event loops need a loopback pair) and synthetic environment files. Raw provider probes and the failed live Atlas ping are separate, older evidence. See [evidence](../../docs/verification.md) and [backend README](../README.md) for actual commands.

Use [the shared workflow](../../docs/ai-development-workflow.md) for planning/research, TDD where risk warrants it, broader review and simplification followed by affected-test reruns. Record official sources/version applicability and review findings in the owning task/evidence record. Mocked pass results cannot clear live Atlas/provider acceptance; no optional plugin is required to run the project's tests.

| Case | Required evidence |
|---|---|
| CONTRACT-INPUT | Strict schemas, date/coordinate/label limits, unknown fields, unsupported hazard/bbox, safe validation errors |
| CONTRACT-OUTPUT | Response shape/nullability/invariants, sorted years, event count sums, metadata, error envelope |
| CLIMATE-BASELINE | Independently calculated percentile/interpolation, fixed baseline, coverage gates and leap counts |
| CLIMATE-RUNS | Equality, 2/3 days, gaps, missing/invalid, cross-year, final flush, censoring, ineligible-year crossing |
| CLIMATE-TREND | Known slopes, actual year spacing, ten-year gate, five-year rolling gaps, zero denominator, no significance |
| PROVIDER-NORMALIZE | Shapes, units, dates, duplicates/conflicts, invalid/nulls, response limit and bounded retries |
| DB-CACHE | Real DB index uniqueness, expiry lookup before TTL cleanup, partial upsert recovery, method/source key changes |
| CLIMATE-SPATIAL | Bounds, nine centers, weights, dedup, missing/invalid samples, no unsupported heatmap |
| SECURITY-BOUNDARY | No arbitrary URL/query, no secret/error leakage, trusted proxy/CORS behavior |
| SECURITY-LOAD | 429/Retry-After, deadlines, bounded concurrent work/lock map, repeated misses and cancellation |
| E2E-LOCATION | Real/mocked geocoding clearly distinguished, no-match and provider failure |
| E2E-ANALYSIS | One real provider + isolated real MongoDB analysis, persistence readback, repeated cache hit, UI schema compatibility |
| DB-CONNECTION | Missing URI, invalid/URL-encoded config, secure TLS validation, successful/failed ping, DNS/selection deadline, reused handle, safe exception text, closure after success/failed startup/cancellation; no collection operations |
| HEALTH | Liveness calls no dependency; startup refuses failed DB; readiness detects subsequent outage with safe 503/no-store/request ID; closure awaited |
| PROVIDER-TRANSPORT | Exact timeout/attempt bounds, transient status allowlist, Retry-After date/seconds, bounded backoff, streamed body cap, redirect denial, cancellation releases capacity |
| PROVIDER-FALLBACK | Primary success; timeout/temporary 5xx/malformed JSON/missing-invalid data; full alternate source; both fail; units/time conflicts; no credentials; invalid input causes no I/O |
| QUALITY-SOURCE | Whole baseline plus selected interval from one source, correct provenance/eligibility, 95% guard plus year/month baseline gates, conflicting duplicates and no interpolation |
| FAILURE-PIPELINE | Provider errors never create success cache entries, concurrent duplicate requests reuse valid stored results, partial writes recover, DB loss yields no unstored success, stale results refused |
| OBSERVABILITY | Structured field allowlist, redacted failures, bounded metric labels, provider/cache/quality outcome counts |
| PERFORMANCE | Reproducible cold/hot point workloads, sample count/environment/concurrency/cache state, p50/p95 including failures, provider quota/memory budget; no fake capacity claim |
| DEPLOYMENT-RECOVERY | Graceful shutdown, host timeout/origin/TLS/readiness checks and isolated restore/rollback rehearsal |
| CI-CLEAN | Frozen lock install on clean runner, separate backend/frontend jobs in the root repository, shared-contract check, failed test blocks merge; fork jobs have no live secrets |

Use deterministic synthetic fixtures for unit cases, explicitly labeled and excluded from production. Mock HTTP only at provider boundaries. Do not let tests depend on today's weather or live clock; pass time into freshness/period checks. Separate live tests from deterministic CI and document skipped prerequisite-dependent checks.

Cache/load results must include request size, period, region, cache state, hardware, concurrency and sample count. Safety checks cannot be disabled just to pass installation or tests. Cross-repository release evidence belongs in [shared verification](../../docs/verification.md).

## Test levels and completion gates (76–85)

Unit tests isolate a pure function/state transition using independently expected values; an in-memory fake proves only behavior at its boundary. Integration tests connect modules or a real dependency and must identify which is real: mocked HTTP adapter tests do not prove upstream access, while an isolated real MongoDB test can prove unique indexes/readback. Contract tests compare actual serialized requests/responses/errors and consumer fixtures to the canonical version, including null/zero and source semantics. End-to-end tests exercise the browser through the real backend, persistence and source into visible results, including a repeated cache hit.

Behavior changes to climate rules, normalization, caching, security, retry/timeout or request state need regression cases covering the changed failure mode. Low-impact prose/format edits need relevant checks, not tests that mirror implementation. Failed/skipped prerequisite checks keep the affected task open; record exact command, date, result and limitation. A build or lint pass cannot substitute for feature behavior.

BE-009's deterministic tests are complete; retry a minimal live Atlas ping only after password rotation and confirmed network access. BE-001 contract tests are complete; analysis-response contract tests follow DOC-004/BE-007. BE-003 / BE-010 test both public adapters/selector; BE-005 / BE-007 later own real cache and failure-not-cached evidence. Current user scope prohibits implementing schemas/collections/business features during this documentation phase.
