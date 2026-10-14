# Backend implementation sequence

The [task tracker](tasks.md) owns statuses and acceptance. The latest user prompt authorizes incremental implementation in one root repository. Start with BE-001/BE-009, then provider integration, science, persistence/API, frontend, end-to-end checks and final review. No analysis business feature is implemented yet.

## Authorized milestone 1 slice (2026-10-14)

Scope: DOC-002 root Git/ignore protection; BE-009 configuration, bounded async Atlas lifecycle and live read-only ping after password rotation; BE-001 strict point/period/error/health schemas and API tests. Reuse installed dependencies and the existing three modules. Add only schemas and focused tests, with no collections or indexes in this slice.

Acceptance: process/local/private-file precedence and safe configuration failures; TLS validation; one lifespan-owned client; elapsed deadlines covering async DNS, ping and close; cancellation cleanup; liveness without I/O; readiness outage with sanitized errors and fresh request IDs; strict input bounds and explicit unsupported bbox. Deterministic tests use synthetic secrets and block network/real credential reads. Live ping is recorded separately.

Research/review: installed PyMongo 4.18.3 performs SRV/TXT resolution through async dnspython; verify cancellation at that actual driver boundary. Use Python asyncio.timeout, no worker-thread DNS workaround. FastAPI TestClient context exercises lifespan. Rollback is a file diff against the ignored pre-edit baseline; do not reset Git or overwrite unrelated work. The user's current master prompt authorizes this slice; password rotation was confirmed separately before live access.

| Milestone | Tasks and prerequisites | Gate / principal risk |
|---|---|---|
| Connectivity verification | BE-009 after DOC-001 | Safe configuration/lifecycle tests, bounded DNS and failed live Atlas diagnosis; no collections |
| Contract foundation | BE-001 after DOC-001; DOC-004 before NASA response integration | Strict schemas and health test; supported Python dependency versions |
| Scientific core | BE-002 after schemas | Independent expected numerical values; calendar and coverage errors |
| Source boundary | BE-003 then BE-010; BE-004 lookup can follow adapter boundary | HTTP normalization/retry/size tests and live smoke distinguished |
| Persistence | BE-005 after adapter and BE-009 | Real MongoDB indexes, expiry and idempotent readback; credentials/setup |
| Point vertical slice | BE-007 after engine/source/storage and approved DOC-004 | Real analysis + repeat cache hit; method/response invariants |
| Public service safeguards | BE-008 after point/lookup | Rate/deadline/CORS/error tests; one-worker limitation stated |
| Operations | BE-011 after core/hardening; REL-002 after repository/scaffold setup | Safe telemetry, measured performance, clean CI and deployment gates |
| Regional extension | BE-006 after hardened point path | Correct sampled-series semantics and measured cold budget |

Before significant implementation, follow [the shared workflow](../../docs/ai-development-workflow.md): record the slice plan, installed-version research, boundaries, failure cases, tests, rollback and approval status here. Review the core pipeline architecture before integration; use TDD for science, validation, fallback and caching. Review affected callers/security and preserve safeguards during simplification, then re-run affected checks.

Work in small complete changes. Update tests/documents before advancing. Shared contract changes are coordinated with frontend types/fixtures. If a source/hosting limit disproves this plan, record evidence and revise the affected boundary before introducing more infrastructure.
