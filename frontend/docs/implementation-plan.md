# Frontend implementation sequence

[Tasks](tasks.md) owns completion. FE-001 to FE-007 are DONE; the slices below record how FE-006 (fast start) and FE-007 (heatwave calendar) were built and plan FE-008 (Leaflet map and map picker). Before significant implementation, follow [the shared workflow](../../docs/ai-development-workflow.md): add a concrete slice plan here with package-version research, files/interfaces, edge cases, tests and approval status. Existing milestones specify order, not approval to build every feature. Apply UI review before extensive markup and review/simplification/final verification after the slice.

| Milestone | Tasks / prerequisites | Verification gate / risk |
|---|---|---|
| Minimal shell | FE-001 after DOC-001, independent of unfinished backend | Verified scripts, token use, semantic shell; do not imply working analysis |
| User input | FE-002 after shell; lookup/contract are final integration gates | Accessible controls and stale-response/error tests; narrow form usability |
| Complete point dashboard | FE-003 after real analysis/hardening | Real source results, null/zero states, accessible charts, no duplicate calculations |
| Responsive acceptance | FE-005 after result view | Nine sizes and actual keyboard/zoom/reduced-motion/automated audit evidence |
| Regional extension | FE-004 after bounded backend sampler | Honest geographic approximation and invalid-box behavior |
| Fast start | FE-006 after FE-005 | Real server/progress states, browser result reuse within backend expiry; no fake progress |
| Time-series storytelling | FE-007 after FE-006 | Event calendar from backend events, linked year state, keyboard path; no derived science |
| Map context and picking | FE-008 after FE-004 and FE-007 | Lazily loaded Leaflet chunk, grayscale tiles, honest grid-cell display, typed inputs stay the keyboard path |

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
| Reuse results | In-memory, per-tab LRU of 20 successful responses keyed by the exact request inputs (hazard, region kind and coordinates, period; the display label is excluded). Exact rather than rounded keys: JavaScript and Python round half-way cases differently, so rounding could reuse a result for a point the backend treats as different, while an exact key can only cause a harmless miss. A hit is used only while the backend's `cache.expires_at` is in the future, is relabelled with the current label, and is marked "saved in this browser". Errors and cancelled requests are never stored. Hits send no request, so they do not count against the 5-per-minute limit. | `src/resultCache.ts`, `src/hooks/useAnalysis.ts`, `src/components/ResultsView.tsx` |
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

Result (2026-10-14): built as planned; evidence is in [tasks](tasks.md). Deviations: the calendar and linked year state landed in one commit because their tests share fixtures; the year panel sits beside the calendar from 1024 px (below it on narrower screens) so selecting a year never moves the calendar; excluded years are named in the legend, the chart description and the year list ("2004 (excluded)") instead of an in-row label, which would collide with 8 px rows.

## Leaflet result map and map picker slice (FE-008), 2026-10-15

Approval: after FE-006/FE-007 were merged and deployed, the user approved adding `leaflet@1.9.4` (current stable; 2.0 is alpha) with `@types/leaflet@1.9.22`, a basemap (first CARTO Dark Matter, then OpenStreetMap once CARTO proved to need a key) and scope "result map + map picker" (2026-10-15). No React wrapper (react-leaflet 5 would be a third package for two small components). Mapbox is out because it needs a key. Recorded as [ADR-024](../../docs/decisions/README.md). Branch `feature/leaflet-map`; merging to `main` deploys and is confirmed separately. No backend or contract change.

| Part | Design | Files |
|---|---|---|
| Geometry | Pure helpers: the shapes to draw for a result (requested point; for a provider-reported grid point, that cell as resolved ± half the grid size; for a box, its outline and the 9 sample points), a clicked map position converted to a valid point (longitude wrapped, rounded to 4 dp), two clicked corners converted to an ordered box, and the label for a map-picked point. A cell is never drawn when the provider did not report it (NASA POWER), because its position would be a guess. | `src/map/geometry.ts` |
| Leaflet layer | Imperative Leaflet in `useEffect`, one map per component, removed on unmount. Vector circle markers and rectangles only (the default marker images are colored PNGs). OpenStreetMap tiles with the OpenStreetMap credit, tile pane turned grayscale and inverted to dark with CSS, `noWrap` world bounds, wheel zoom off so page scrolling is never captured. The attribution prefix drops Leaflet's colored flag. | `src/map/maps.tsx`, `src/styles/global.css` |
| Lazy loading | `React.lazy` splits Leaflet and its CSS into a separate chunk; a same-size outline holds the space while it loads. The page receives the map components like the existing health check, so page tests stay isolated and dedicated map tests load the real module. | `src/map/lazy.ts`, `src/main.tsx`, `src/DashboardPage.tsx` |
| Result map | In the region section: requested point (filled), reported grid point and its cell (hollow, dashed), or the box outline and 9 sample points; fitted to the shapes. Text beside it keeps the coordinates, and states when the provider did not report the cell. No intensity shading. | `src/components/ResultsView.tsx` |
| Map picker | In the Location fieldset. Point mode: a click sets latitude and longitude (and a "Map point …" label when the label is empty or was set by the map); a "Use map centre" button gives keyboard users the same action after panning with arrow keys. Box mode: first click sets one corner, second click the opposite corner and fills south/west/north/east; spans over 2° are left to the existing validation message. Typed or searched coordinates are drawn on the map, which pans to them when they are outside the view. | `src/components/AnalysisControls.tsx`, `src/DashboardPage.tsx` |

Honesty rules: the map shows only requested coordinates, provider-reported grid points and the box's sample points; the grayscale map tokens stay reserved because there is still no spatial intensity data.

Edge cases: NASA (resolved null) versus Open-Meteo (resolved point), box sample points, longitude wrap and world edges, a box dragged in either direction, spans over 2°, a label typed by the user (never overwritten), search or quick-city selection moving the map, unmount mid-load, tiles failing to load (coordinates and text remain), touch dragging inside a 220–260 px map, 320 px width.

Tests (written first): geometry (cells only when reported, cell bounds, box ordering and rounding, longitude wrap, labels); Leaflet components in jsdom with an SVG shim (shapes drawn, picker click and corner clicks call back with the right values, "Use map centre"); page integration through injected map components (fields filled, label rule, map follows typed coordinates); axe with maps present.

Verification: Vitest, typecheck, lint, build with the initial and map chunk sizes reported separately, axe, nine-size overflow with both maps, and a real browser run (tiles load, click to pick, analysis, result map) locally and after deployment. Rollback: revert the branch and the dependency.

Commit plan: plan, ADR and traceability → dependency → geometry → result map → map picker → evidence and state documents.

Result (2026-10-15): built with these changes from the plan. CARTO served only "API KEY REQUIRED" watermark tiles, so the basemap is OpenStreetMap (user decision, ADR-024 corrected). Browser review found three issues that tests had not: a chosen city did not move the map (external places now centre and zoom it, map picks never move it), the credit box kept Leaflet's light background (Leaflet's stylesheet loads later with equal specificity, so overrides use `.leaflet-map.leaflet-container`), and a city-button label survived a map pick far away (the label is now kept only if the user typed it). The result map and picker landed in one commit because they share `src/map/maps.tsx`; the per-test timeout was raised to 15 s after a cold run timed out.

## Supported start year slice (FE-009 with BE-012), 2026-10-15

The form's earliest start year comes from the backend's health response instead of a hard-coded 1940. The plan, edge cases and tests are in the [backend implementation plan](../../backend/docs/implementation-plan.md#supported-start-year-slice-be-012-fe-009-2026-10-15).

## Mann-Kendall trend slice (FE-010 with BE-013), 2026-10-15

The trend card and method text show the backend's Mann-Kendall result (contract 0.3) and still accept 0.2 responses during deployment. The plan, edge cases and tests are in the [backend implementation plan](../../backend/docs/implementation-plan.md#mann-kendall-trend-slice-be-013-fe-010-2026-10-15).
