# Frontend implementation sequence

[Tasks](tasks.md) owns completion. FE-001 to FE-005 are DONE; FE-006 (fast start) and FE-007 (heatwave calendar) are planned below. Before significant implementation, follow [the shared workflow](../../docs/ai-development-workflow.md): add a concrete slice plan here with package-version research, files/interfaces, edge cases, tests and approval status. Existing milestones specify order, not approval to build every feature. Apply UI review before extensive markup and review/simplification/final verification after the slice.

| Milestone | Tasks / prerequisites | Verification gate / risk |
|---|---|---|
| Minimal shell | FE-001 after DOC-001, independent of unfinished backend | Verified scripts, token use, semantic shell; do not imply working analysis |
| User input | FE-002 after shell; lookup/contract are final integration gates | Accessible controls and stale-response/error tests; narrow form usability |
| Complete point dashboard | FE-003 after real analysis/hardening | Real source results, null/zero states, accessible charts, no duplicate calculations |
| Responsive acceptance | FE-005 after result view | Nine sizes and actual keyboard/zoom/reduced-motion/automated audit evidence |
| Regional extension | FE-004 after bounded backend sampler | Honest geographic approximation and invalid-box behavior |
| Fast start | FE-006 after FE-005 | Real server/progress states, browser result reuse within backend expiry; no fake progress |
| Time-series storytelling | FE-007 after FE-006 | Event calendar from backend events, linked year state, keyboard path; no derived science |

Choose the smallest adequate chart dependency during implementation and pin it; no chart/UI/state package has been installed (FE-001 added only React, Vite and test/lint tooling). Inspect an actual reference image if later supplied. Complete frontend/backend point integration before bonus map/export features. Shared-wire changes update both sides before release.

## Supplied monochrome implementation brief

The 2026-10-14 design/UI brief is reconciled into [design](design.md), screens, state and existing tasks; user confirmed document alignment only. Its implementation phases are future work, not executed commands.

| Brief phase | Existing task / authority | Implementation gate |
|---|---|---|
| Inspect | DOC-005; instructions/state | No frontend code/dependencies to reuse yet; keep Git boundaries |
| Centralize tokens | FE-001; design.md | Grayscale tokens, white action/focus, accessible borders; no new font/image dependency required |
| Compose dashboard | FE-001 shell, FE-003 results; screens/system.frontend | Header/form/metrics/frequency/supporting charts/insights; spatial intensity only with valid data |
| Interactions | FE-002, FE-003; state/contract | Real requests, safe errors, stale-response rejection; zero events distinct from insufficient data; no stale-result API extension |
| Responsive review | FE-005; responsiveness/testing | Nine sizes, long/missing/error states, keyboard, contrast and reduced motion actually checked |
| Test/review | Owning FE task | Inspect real scripts, execute checks, review affected callers/diff |
| Evidence | Owning FE task / verification | Record actual results and honest task/state/memory |

Primary series is white/solid/marked; comparison is gray/dashed/labeled. Render backend arrays without interpolation or scientific recalculation. Begin with opaque panels and pure black; no licensed local storm asset exists. Imagery/translucency requires later rendered contrast evidence. No FE task is completed by this document update.

## Fast start and heatwave calendar slice (FE-006, FE-007), 2026-10-14

Approval: the user accepted the review-feedback plan ("lean into clean time-series visualization… keep the UI snappy") and asked to start with items 1 (perceived speed) and 2 (heatwave calendar), with a plan, document updates and commits. Work happens on branch `feature/fast-start-and-heatwave-calendar`; pushing or merging to `main` deploys to Vercel/Render and is confirmed separately. No new dependency, backend or contract change.

Measured starting point: production first request after idle took 34 s (Render free plan sleeping); warm analyses 10 ms with a 23.6 kB response; responses are already Brotli-compressed; JS bundle 78.5 kB gzip. Event data (`events`) is returned but only shown in a hidden table.

### FE-006 Fast start

| Part | Design | Files |
|---|---|---|
| Wake the API | One `GET /api/v1/health` on page load (90 s timeout, aborted on unmount). States: checking → waking (no answer after 1.5 s) → ready, or unreachable. A polite live message explains the free-hosting delay; nothing is shown when the server answers quickly. Health is not rate-limited. | `src/api/client.ts` (`checkHealth`), `src/hooks/useServerStatus.ts`, `src/DashboardPage.tsx` |
| Reuse results | In-memory, per-tab LRU of 20 successful responses keyed by the canonical request (hazard, region kind, coordinates rounded to 4 dp like the backend, period; the display label is excluded). A hit is used only while the backend's `cache.expires_at` is in the future, is relabelled with the current label, and is marked "saved in this browser". Errors and cancelled requests are never stored. Hits send no request, so they do not count against the 5-per-minute limit. | `src/resultCache.ts`, `src/hooks/useAnalysis.ts`, `src/components/ResultsView.tsx` |
| Honest loading | A stage list built only from facts the browser knows: server state (waking/ready) and "analysis requested" with real elapsed seconds. Static placeholder outlines (no numbers, no looping animation) for metrics and charts. After 45 s, a note that the server or data provider is slow, with Cancel still available. No percentages or simulated progress (NFR-006). | `src/components/LoadingView.tsx`, `src/styles/global.css` |

Edge cases: very fast or very slow health checks; health failure while analysis still works; coordinates differing only below 4 dp; bbox keys; label-only changes; expired saved results; LRU eviction; retry after an error; unmount mid-request.

Tests (written first): cache keying, expiry and bound; health ping once with waking/ready/unreachable states (fake timers); a repeat analysis served without fetch and relabelled; expired entry refetched; errors not cached; loading view shows stages, elapsed time and no metric digits; long-wait note after 45 s.

### FE-007 Heatwave calendar and linked charts

| Part | Design | Files |
|---|---|---|
| Calendar | SVG, one row per requested year, x = day of year scaled to that year's length (leap years end at the same edge), month gridlines and labels. Each event is drawn as bars over its days; events crossing 31 December are split into two rows with continuation marks. Bars are shaded by the backend's peak excess in three labelled display bins (< 1 °C, 1–2 °C, ≥ 2 °C) using the chart tertiary/secondary/primary tokens; boundary-censored events get a dashed outline; excluded years get a dotted row marker and an "excluded" label. Minimum bar width 3 px; row height adapts to the number of years. Hover shows dates, length and excess. | `src/components/HeatwaveCalendar.tsx`, `src/hooks/useWidth.ts`, `src/styles/global.css` |
| Linked year | `ResultsView` owns `activeYear` (hover) and `selectedYear` (click/keyboard). Line charts and the calendar draw the same year cursor; state changes only when the year changes, not on every pointer move. Derived series are memoised per result. | `src/components/ResultsView.tsx`, `src/components/LineChart.tsx` |
| Year detail | Selecting a year (chart click, calendar click, or a native "Inspect a year" select for keyboard users) opens a detail panel with that year's backend values (events started, heatwave days, durations, anomaly, coverage or exclusion reasons) and the events that touch that year; the events table filters to the same year. Escape or "Show all years" clears it. | `src/components/ResultsView.tsx` |

Honesty rules: everything comes from `annual` and `events` already returned; the excess bins only group backend numbers for display and are labelled as such; no seasonality statistics or trends are computed in the browser.

Edge cases: one-year and 50-year periods, no events, events crossing years, leap days, censored edges, excluded years, bbox results, 320 px width (single-letter month labels, minimum bar width).

Tests (written first): day-of-year and cross-year splitting incl. leap years; shading bins and censored/excluded markers; empty-period message; hover tooltip; chart hover moves the calendar cursor and vice versa; click, select and Escape drive the year detail and filtered events table; axe with a year selected.

Verification: Vitest, typecheck, lint, build size, axe; nine-size overflow measurement and a live run against the local or deployed API; mutation checks on the cache, stale-state and calendar rules. Rollback: revert the branch; no data or contract migration involved.

Commit plan: plan and traceability → wake-up → browser reuse → loading view → calendar → linked year state → evidence and state documents.
