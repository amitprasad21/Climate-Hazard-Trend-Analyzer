# Frontend verification plan

**Checks pass (2026-10-14):** `npm test` (86 Vitest/jsdom cases: tokens, page lifecycle and errors, search, charts, heatwave calendar and linked years, server status, saved results, loading view, nine-size responsiveness, axe accessibility), `npm run typecheck`, `npm run lint`, `npm run build` (84.02 kB gzip JS, 3.32 kB CSS). Mutation checks: 9 of 9 saved-result mutants and 16 of 16 calendar/linking mutants caught. Interaction tests use a mocked fetch and synthetic fixtures (tests/fixtures.ts). The live browser run against the real API is recorded under FE-002/FE-003/FE-005 in [tasks](tasks.md). Current documentation checks do not count as frontend tests.

| Case | Required evidence |
|---|---|
| UI-DESIGN | Black/white/grayscale only, white Analyze trends action, consistent surfaces, patterns/markers/labels for series/status, no reference-image claim without source |
| UI-METRICS | Backend values rendered with units, large/null/zero cases, no local climate calculation |
| UI-CHARTS | All three backend series, gap semantics, readable ticks/legend, table or focus details |
| UI-LIFECYCLE | Idle/loading/success/partial/error/no-events, duplicate submit, abort, stale success/error, timeout and retry |
| UI-GEOGRAPHY | Returned coordinates/sample points; missing spatial intensity explicitly disclosed |
| UI-RESPONSIVE | All [nine viewports](responsiveness.md), no page overflow, visual clipping/long-label/control checks |
| UI-A11Y | Keyboard-only workflow, visible focus/order, labels/live regions, contrast, reduced motion and 200% zoom; automated accessibility tool plus manual review |
| CONTRACT-INPUT/OUTPUT | Client request/response types match root contract; safe invalid/non-JSON errors, zero/null distinctions |
| E2E-LOCATION | Search/disambiguation, no result, timeout, keyboard selection |
| E2E-ANALYSIS | Real backend result and cache metadata; no production fixture substitution |

Proposed test stack: Vitest/Testing Library for behavior, Playwright plus axe for browser checks, subject to package/runtime compatibility at scaffold time. These are recommendations, not installed tools or verified commands. Use existing bundled browser tooling for manual review where supported. Test controls and outcomes, not implementation trivia.

For responsive fixtures test long city names, high event counts, missing durations, null years and long provider errors. Label synthetic fixtures in development-only views. Record which browsers, dimensions, states and screenshots were actually inspected. A build pass alone never completes FE-005. Root [verification](../../docs/verification.md) collects release-level evidence.

## Workflow evidence

Apply [the shared workflow](../../docs/ai-development-workflow.md) to each meaningful UI change. Record plan/approval and package research references in the owning task, then actual checks, broader review findings, simplification and final verification. Use native Codex review/browser capabilities when applicable; document manual alternatives and unavailable prerequisites. No external skill command is assumed. Existing case/viewport records remain the evidence authority.

## Layered evidence and regression policy

Unit/interaction tests exercise components and the request hook with deterministic fixtures. Contract tests exercise the client decoder and request serializer against the approved shared version; they must not invent a second source schema. Integration tests connect page, hook and client through a controlled HTTP boundary, explicitly labeled mocked. End-to-end tests use the actual browser/backend/Atlas/provider path and cannot substitute fixtures silently. Backend meanings are never re-derived by frontend assertions from the same duplicated formula.

Add regression cases for changed user behavior, stale-response races, security/validation, chart null handling and responsive overflow. Test user outcomes rather than component private state. A CSS change affecting charts requires narrow/wide visual evidence; a request-state change requires late success and late failure tests. Small prose changes need documentation verification only.

FE-005 also records production compressed JS size and a reproducible cold/warm interaction profile (browser/version, device or CPU throttling, network/cache state and sample count). Initial <250 KiB target excludes optional map chunks; measured 84.02 kB gzip (268 kB raw) after FE-007. Check expensive chart rerenders before memoizing; annual data is at most 50 rows. REL-002 puts type/lint/unit/build/contract and browser checks into clean independent CI; no workflow exists today.

Required evidence for DONE: actual commands pass, declared states and acceptance covered, failures fixed, screenshots reviewed where applicable, current docs/tasks updated, affected callers reviewed. Skipped browser prerequisites keep FE-005 open, even if static overflow checks pass.

Monochrome acceptance: inspect every production UI/chart/map/status color; use patterns/markers/labels; verify white action, focus and essential input boundaries. Decorative #454545 must not be the sole essential control boundary. #707070 is for non-text chart marks, not small axis text. Opaque token calculations are available now; rendered contrast over imagery/translucency remains a browser check. Pure black and opaque panels are the no-asset default.
