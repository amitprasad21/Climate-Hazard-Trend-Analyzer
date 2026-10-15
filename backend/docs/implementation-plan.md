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

## Mann-Kendall trend slice (BE-013, FE-010), 2026-10-15

Approval: the user asked to "add Mann-Kendall trend detection" (2026-10-15), the case study's named trend technique and the README's first planned improvement. Branch `feature/mann-kendall`; merging to `main` deploys and is confirmed separately. Recorded as ADR-025, which supersedes ADR-010's no-significance rule.

| Part | Design | Files |
|---|---|---|
| Test | Classical two-sided Mann-Kendall on eligible annual event counts in year order: S = Σ sign(yⱼ − yᵢ) for i < j; variance with the tie correction [n(n−1)(2n+5) − Σ t(t−1)(2t+5)] / 18; Z with continuity correction (S ∓ 1)/√Var, 0 when S = 0 or the variance is 0; p = erfc(|Z|/√2); Kendall's τ = S / (n(n−1)/2). Significant when p < 0.05. Still at least 10 eligible years. No new dependency. | `app/trend.py` |
| Slope | Sen's slope: the median of (yⱼ − yᵢ)/(xⱼ − xᵢ) over all pairs, using actual years so excluded years are gaps. The OLS slope stays as `frequency_slope_per_year` for reference. | `app/trend.py` |
| Serial correlation | The test assumes independent years. Lag-1 autocorrelation of the Sen-detrended counts (eligible years in order); when it is positive and above Anderson's 95% bound (−1 + 1.96√(n−2))/(n−1), add a `SERIAL_CORRELATION` warning that significance may be overstated. A Hamed-Rao variance correction is left for later. | `app/trend.py`, `app/climate.py` |
| Direction | `increasing` / `decreasing` only when significant (sign of S); otherwise `no_significant_trend`; `insufficient_data` below 10 years. `flat` is retired. | `app/climate.py` |
| Contract 0.3, method heatwave-v2 | `summary.mann_kendall` = {s, tau, z, p_value, sens_slope_per_year, significant} or null; methodology `trend_method: "mann_kendall_sens_slope"`, `significance_tested: true`, `significance_level: 0.05`. The version bump changes the cache key, so old cached results are never served with the new shape. | `app/schemas.py`, `app/services/analysis.py`, root contract |
| Insight | States the test result, p-value, eligible years and Sen's slope, and says a trend test describes this record only, not its cause. | `app/climate.py` |
| Frontend | Accepts 0.2 and 0.3 (Vercel and Render deploy separately; a 0.2 response has no test result and keeps the old wording). The trend card shows the test outcome with p and Sen's slope; the method text explains the test and its assumption. | `frontend/src/api/*`, `components/ResultsView.tsx` |

Edge cases: all counts equal (variance 0: p = 1, slope 0), heavy ties, excluded years inside the series, exactly 10 years, p below 0.001, strictly monotonic series, a significant decrease, serial correlation with no trend.

Tests (written first): independent hand-computed S, variance, Z, p, τ and Sen's slope for monotonic, tied, constant and gapped series; the serial-correlation bound; direction and insight wording from `analyze_heatwaves`; contract 0.3 and method fields; frontend decoding of 0.2 and 0.3 and the trend card and method text.

Verification: backend pytest and ruff, frontend tests/typecheck/lint/build, docs checker, mutation checks on the statistics, and a live run (local API) comparing New Delhi before and after. Rollback: revert the branch; the cache key changes with the method version, so no data migration.
