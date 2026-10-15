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

## Supported start year slice (BE-012, FE-009), 2026-10-15

Approval: the user asked to "fix the 1940 year gap" (2026-10-15) after the proposal to have the backend report the earliest supported year. Branch `feature/supported-years`; merging to `main` deploys and is confirmed separately.

Problem: the form hard-codes 1940 as the earliest start year. Production runs with the ERA5 fallback off, so only NASA POWER (from 1981) is eligible, and the server rejects earlier start years with `UNSUPPORTED_PERIOD`. Users are invited to choose years the server will refuse.

| Part | Design | Files |
|---|---|---|
| One authority | `earliest_start_year(settings)` = the earliest first year among the enabled providers (1981 with NASA only, 1940 with the ERA5 fallback on). The existing `UNSUPPORTED_PERIOD` message uses the same function. | `app/selector.py`, `app/services/analysis.py` |
| Health field | `GET /api/v1/health` adds `earliest_start_year`, computed once at startup from settings. Still liveness only: no database or provider I/O, `no-store`. Readiness keeps its exact contracted shape. | `app/schemas.py`, `app/main.py`, root contract |
| Contract | Additive field within 0.2. The client treats a missing or invalid value as unknown, because Vercel and Render deploy independently and an older backend lacks it. No analysis, cache or method version change. | `INTEGRATION_CONTRACT.md` |
| Frontend | `checkHealth` returns the value; `useServerStatus` exposes it; the page uses it for start-year validation (the message names the year and says the server's data begins then), the period hint, the inputs' `min` and the year presets. Unknown keeps the 1940 outer bound, and the server stays authoritative. | `frontend/src/api/client.ts`, `hooks/useServerStatus.ts`, `form.ts`, `components/AnalysisControls.tsx`, `DashboardPage.tsx` |

Edge cases: older backend without the field; health unreachable or still waking when the user submits (the server rejects early years with its clear message); fallback enabled (1940); presets clamped to the reported year; a reported year that is not an integer between 1940 and the latest complete year (ignored).

Tests (written first): backend health reports 1981 by default and 1940 with the fallback enabled, readiness unchanged, the period error names the same year; frontend client parsing (present, missing, invalid), hook exposure, and page behaviour (hint, validation message, presets, no request sent for an early year).

Verification: backend pytest and ruff, frontend tests/typecheck/lint/build, docs checker, and a browser run against a local API with the fallback off. Rollback: revert the branch; the field is additive.
