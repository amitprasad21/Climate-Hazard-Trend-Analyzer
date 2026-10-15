# Frontend task tracker

All source paths are proposed. [Root PRD](../../PRD.md) owns requirements; [testing](testing.md) owns case definitions.

## FE-001 Runnable monochrome foundation

Priority: P0. Status: DONE. Requirements: NFR-001, NFR-004. Dependencies: DOC-001.

Scope/files: package/lock/config, minimal page, tokens/styles, smoke test. Acceptance: supported React/TypeScript/Vite scaffold, semantic heading/form shell, canonical grayscale tokens and white Analyze trends action, safe API-boundary placeholder without fabricated results, exact verified run/type/lint/test/build commands. No fabricated metrics. Verify UI-DESIGN and initial keyboard/narrow layout smoke. Evidence: 2026-10-14. User approved Vite + React + TypeScript via npm. Exact pins, each published before 2026-09-30, installed with `npm install --before=… --ignore-scripts`: React 19.3.0, Vite 8.3.1, plugin-react 6.1.1, TypeScript 6.0.3 (typescript-eslint supports <6.1), Vitest 5.0.2, jsdom 29.1.1 (30.x needs Node ≥24.15; local is 24.12), Testing Library 16.3.3, ESLint 10.11.0. `npm audit` flagged source-map-js 1.2.1 (GHSA-68fv-2mgg-jv7q); an override to 1.2.2 changed one lock entry and audit now reports 0 vulnerabilities. src/ has the token sheet, global styles, semantic DashboardPage and an honest not-connected submit notice; no fetch and no figures. 7 Vitest cases include tokens identical to design.md, grayscale only and no colour literals outside tokens.css; 6 of 6 mutants caught. `npm test`, `npm run typecheck`, `npm run lint` and `npm run build` pass (JS 69.6 kB gzip). Browser pane on the Vite dev server: no console errors; idle shell has no page overflow and no element outside the viewport at all nine design sizes; controls ≥44 px; content capped at 1600 px at 1920. Real Tab presses follow reading order with a 2 px white focus-visible outline, and Enter shows the notice with zero /api requests.

Description: Establish the runnable semantic monochrome shell using one supported frontend stack.

Ownership: frontend. Concepts: 4, 9, 10, 16, 21, 73.

Required tests: UI-DESIGN, keyboard/narrow smoke, exact type/lint/unit/build commands.

Documents/files: package.json, package-lock.json, vite.config.ts, tsconfig.json, eslint.config.js, index.html, src/, tests/; docs/design.md and system.frontend.md.

Blockers: None. Not covered: a visual reference image was never supplied, and the 320 px screenshot was cropped by the capture (DPR 2 against a 480 px frame), although measured layout fit. Full state/zoom/contrast checks belong to FE-005.

## FE-002 Accessible controls and request lifecycle

Priority: P0. Status: DONE. Requirements: FR-001, FR-002, FR-003, FR-008, NFR-006. Dependencies: FE-001, BE-004.

Scope/files: controls, request hook, API client/types, interaction tests. Acceptance: Heatwave default, usable location/year selection, clear validation, actual progress/error/idle states and duplicate protection; parameter edits ignore stale results and errors. Verify UI-LIFECYCLE/CONTRACT-INPUT and E2E-LOCATION. Synthetic responses are test-only. Evidence: 2026-10-14. src/api/client.ts (contract 0.2 types, safe decoding of error envelopes and non-JSON gateway errors, Retry-After, 100 s analysis / 20 s search timeouts), src/hooks/useAnalysis.ts and useRegionSearch.ts (AbortController plus monotonic tokens: late successes and errors after edits are dropped, duplicate submits ignored, unmount aborts), src/form.ts (client guidance mirroring server limits) and src/components/AnalysisControls.tsx (place search with a radio result list, manual coordinates, Heatwave default, native year inputs, field errors with aria-invalid and focus on the first problem, Cancel while pending, live status). 15 interaction tests; 9 of 9 lifecycle mutants caught after adding a race test (a success arriving despite abort). Real browser: search "New Delhi" → choose → 1995–2024 → Analyze reached the live API.

Description: Build accessible selection and a stale-safe request lifecycle with one API boundary.

Ownership: frontend. Concepts: 7, 12, 13, 14, 15, 17, 20, 21, 66, 76, 78, 80.

Required tests: UI-LIFECYCLE, CONTRACT-INPUT/OUTPUT, E2E-LOCATION; late success/error and unmount.

Documents/files: src/api/, src/hooks/, src/form.ts, src/components/AnalysisControls.tsx, tests/DashboardPage.test.tsx.

Blockers: None.

## FE-003 Backend-driven result presentation

Priority: P0. Status: DONE. Requirements: FR-005, FR-006, FR-007, FR-008, FR-009, DATA-007. Dependencies: FE-002, BE-007, BE-008.

Scope/files: metric/charts/insights/region-context presentation, result tests. Acceptance: all four metrics and three plots use backend data; source/method/period/coverage are explicit; null/zero/partial/no-event states differ; keyboard/table chart details and valid geography alternative work. Verify UI-METRICS/CHARTS/GEOGRAPHY and real E2E-ANALYSIS. Evidence: 2026-10-14. src/components/ResultsView.tsx renders backend values only: four metrics (null duration and insufficient trend explained), annual frequency (solid white with markers) with the backend 5-year rolling mean (dashed grey), duration and anomaly charts (hand-built SVG, gaps at null years, data tables), region/source context (requested point, reported grid cell or "not reported", grid size, elevation, no heatmap), data quality, insights, warnings, events table, method and provenance with attribution link. ErrorPanel maps every contract error code. Live browser run against NASA POWER plus local MongoDB showed 64 events, 44.7 °C threshold, decreasing descriptive trend, 3 charts and provenance notes. 4 chart tests plus result assertions in the page tests.

Description: Render one returned analysis consistently as metrics, charts, insights and valid geography.

Ownership: frontend. Concepts: 9, 10, 11, 17, 18, 20, 21, 51, 54, 64, 79.

Required tests: UI-METRICS/CHARTS/GEOGRAPHY, partial/error/no-events and real E2E-ANALYSIS.

Documents/files: src/components/ResultsView.tsx, LineChart.tsx, ErrorPanel.tsx, src/format.ts, tests/LineChart.test.tsx; docs/screens.md.

Blockers: None.

## FE-004 Bounded-area selection

Priority: P2. Status: DONE. Requirements: FR-010, FR-009. Dependencies: FE-003, BE-006.

Scope/files: region controls/context, request types only if changed, interaction tests. Acceptance: explicit coordinate-box limits, clear unsupported error, actual sample points and resolution disclosure; no fake heatmap. Reuse numeric/native inputs; add map library only with a justified task. Verify CLIMATE-SPATIAL contract cases and UI-GEOGRAPHY. Evidence: 2026-10-14. Added region type toggle ("Single point" vs "Bounding box (area)") and North, South, East, West numeric inputs with validation in src/form.ts (enforcing max 2.0° span, -85° to 85° limits, south < north, west < east). Updated src/components/AnalysisControls.tsx with accessible radio group and numeric inputs. Updated src/components/ResultsView.tsx (RegionContext) to disclose bounding box coordinates, 3x3 spatial sampling (9 cell centers), sample points, and explicit note that no station heatmap is implied. Added unit and interaction tests in tests/DashboardPage.test.tsx verifying wire payload and validation. All 55 frontend tests pass, typecheck, lint, and build pass cleanly.

Description: Add constrained area controls and disclose sampled spatial approximation.

Ownership: frontend. Concepts: 58.

Required tests: CLIMATE-SPATIAL contract cases, UI-GEOGRAPHY and keyboard/narrow controls.

Documents/files: src/form.ts, src/components/AnalysisControls.tsx, src/components/ResultsView.tsx, src/DashboardPage.tsx, tests/DashboardPage.test.tsx; docs/screens.md and root contract.

Blockers: None. Bounded-area selection and spatial disclosure verified.

## FE-005 Responsive and accessible completion

Priority: P0. Status: DONE. Requirements: NFR-002, NFR-003, FR-008. Dependencies: FE-003.

Scope/files: focused layout/chart fixes, browser tests and evidence docs. Acceptance: all nine widths without page overflow, long/missing/large data and every UI state tested, focus/keyboard/reduced motion/zoom and automated accessibility checks plus manual review. Verify UI-RESPONSIVE/A11Y; fix findings and record browser/screenshots actually reviewed; report production compressed bundle size and measured cold/warm interaction cost, optimizing only demonstrated bottlenecks. Evidence: 2026-10-14. All nine design viewports verified via automated responsiveness suite (tests/responsiveness.test.tsx) across idle, populated and error states: 320x568, 360x800, 390x844, 430x932, 768x1024, 1024x768, 1280x800, 1440x900, 1920x1080. In Chromium desktop browser pane: no page overflow, controls ≥44 px, metric cards wrap 4 → 2 → 1 rows. Chart clipping fixed with SVG viewBox scaling; panel overflow fixed with overflow-wrap: anywhere. Keyboard Tab order and white focus-visible outline verified. axe-core 4.13 reports 0 violations across idle, validation, search, populated and error states. Bundle: 77.4 kB gzip JS, 2.4 kB CSS. Measured warm analysis request 10 ms (23.6 kB); cold server path 2.74 s.

Description: Verify responsive/accessibility/performance acceptance across actual browser states.

Ownership: frontend. Concepts: 16, 17, 19, 21, 71, 81.

Required tests: UI-RESPONSIVE/A11Y at all nine sizes; bundle report and interaction profiling.

Documents/files: src/styles/global.css, src/components/LineChart.tsx, tests/a11y.test.tsx, tests/responsiveness.test.tsx; docs/responsiveness.md, docs/testing.md.

Blockers: None. Responsive viewports, accessibility audits and bundle performance verified.


## FE-006 Fast start and honest loading

Priority: P1. Status: DONE. Requirements: NFR-006, FR-008. Dependencies: FE-005.

Scope/files: health wake-up and server status, in-browser result reuse, loading stages and placeholders; src/api/client.ts, src/hooks/useServerStatus.ts, src/resultCache.ts, src/hooks/useAnalysis.ts, src/components/LoadingView.tsx, styles and tests. Acceptance: one health request per page load with waking/ready/unreachable messages; repeated identical analyses served from the browser only while the backend's expiry allows, relabelled and marked as saved, never caching errors; loading view shows only real stages and elapsed time, never simulated progress; no backend or contract change. Verify UI-LIFECYCLE plus cache, timer and accessibility tests. Evidence: 2026-10-14, commits 28d8488, 343fca2 and 8a5682c. `checkHealth` and `useServerStatus` send one health request per page load (90 s timeout, aborted on unmount), show a waking message after 1.5 s, "Analysis server ready." after a slow wake and an unreachable message on failure (tests/serverStatus.test.tsx, fake timers). `ResultCache` is an in-memory LRU of 20 keyed by the exact inputs with the label excluded; `useAnalysis` serves a hit only while the backend's `cache.expires_at` is in the future, relabels it and marks it saved, and never stores failures or superseded responses (tests/resultCache.test.ts, tests/browserCache.test.tsx). 9 of 9 cache mutants were caught after adding longitude and per-edge key tests. `LoadingView` shows only known stages, real elapsed seconds, static placeholders and a 45 s slow-wait note with Cancel still available (tests/loadingView.test.tsx); axe reports 0 violations while loading. Browser (Claude pane, Chromium, local API): resubmitting New Delhi 1995–2024 sent no analysis request and showed "(saved result, no new request)"; one health request completed per load (development StrictMode aborts a duplicate first ping; production mounts once). Typecheck, lint and build pass. Not measured: a real Render cold start through the waking message, which needs the deployment.

Description: Make the first and repeated analyses feel fast without hiding the free-hosting cold start or inventing progress.

Ownership: frontend. Concepts: 12, 15, 19.

Required tests: UI-LIFECYCLE (server status, cache hit/expiry/no error caching, loading stages), axe, nine-size overflow check.

Documents/files: [plan](implementation-plan.md), docs/state.md, docs/screens.md, docs/testing.md.

Blockers: None.

## FE-007 Heatwave calendar and linked year views

Priority: P1. Status: DONE. Requirements: FR-006, FR-007, NFR-003. Dependencies: FE-003, FE-006.

Scope/files: src/components/HeatwaveCalendar.tsx, src/hooks/useWidth.ts, src/components/LineChart.tsx, src/components/ResultsView.tsx, styles and tests. Acceptance: calendar of backend events by year and day of year with cross-year splitting, labelled grayscale excess bins, censored and excluded markers; hover links every chart to the same year; click, a native year select or Escape drive a year detail panel and filtered events table; all values from the existing response, nothing computed scientifically in the browser. Verify UI-CHARTS, keyboard path and axe. Evidence: 2026-10-14, commit cbbb41c. `src/calendar.ts` (leap-aware day of year, cross-year splitting, events touching a year, display-only excess bins, exclusion-reason text) and `HeatwaveCalendar` (one row per year, month grid with initials when months are narrow, 3 px minimum bars, continuation marks, dashed censored outlines, dotted excluded rows, hover tooltip, empty state). `ResultsView` owns the hovered and selected year: every line chart draws the hovered crosshair and tooltip plus a solid selected-year line; a calendar row, a chart click or the native "Inspect a year" list opens a panel of that year's backend values or exclusion reasons and the events touching it, and filters the events table; Escape, "Show all years" or clicking the selected row clears it. Chart pointer positions now map through the viewBox scale, and series are memoised per result. Tests: tests/HeatwaveCalendar.test.tsx (10), a viewBox-scaling LineChart test and a reused-result selection test; 16 of 16 calendar and linking mutants caught; axe reports 0 violations with a year selected. Browser (Claude pane, Chromium, local API, New Delhi 1995–2024): 30 rows and 64 bars for 64 backend events; a real pointer over 2013 drew the 2013 crosshair and tooltip in all three charts; a bar tooltip read 18–21 May 2003, 4 days, peak 1.45 °C; selecting 2003 listed its values and 2 events and filtered the table to 2; 0 px page overflow at all nine sizes with the calendar populated, two-column timeline from 1024 px. Suite 86 tests; bundle 84.02 kB gzip JS (78.5 kB before FE-006), 3.32 kB CSS. Not covered: per-size screenshot review (the hidden pane's captures were unreliable) and a physical touch device.

Description: Turn the returned events into a clear time-series story and link the charts by year.

Ownership: frontend. Concepts: 9, 17, 18.

Required tests: UI-CHARTS (calendar geometry, bins, markers, empty state), linked hover/selection, keyboard and axe.

Documents/files: [plan](implementation-plan.md), [design](design.md), docs/screens.md, docs/system.frontend.md.

Blockers: None.

## FE-008 Leaflet result map and map picker

Priority: P1. Status: DONE. Requirements: FR-001, FR-009, FR-010, NFR-003. Dependencies: FE-004, FE-007.

Scope/files: src/map/geometry.ts, src/map/maps.tsx, src/map/lazy.ts, src/components/ResultsView.tsx, src/components/AnalysisControls.tsx, src/DashboardPage.tsx, src/main.tsx, styles, package.json/lock and tests. Acceptance: a lazily loaded Leaflet map with dark grayscale OpenStreetMap tiles and the required credit shows the analysed point, any provider-reported grid cell, or the box with its 9 sample points, never an intensity shading; a picker map sets a point by click or by "Use map centre" and a box by two corner clicks, never overwriting a typed label; typed and searched coordinates appear on the map; the initial bundle stays within budget with Leaflet in its own chunk. Verify UI-GEOGRAPHY, E2E-LOCATION, keyboard path, axe and nine sizes. Evidence: 2026-10-15, commits b6d00d3 (plan, ADR-024), 8aff674 (leaflet 1.9.4 and @types/leaflet 1.9.22, exact, scripts disabled, npm audit 0 vulnerabilities), 153e52e (geometry) and 9b066ad (maps). Tests: tests/mapGeometry.test.ts (6), tests/maps.test.tsx (5, real Leaflet in jsdom with an SVG shim) and tests/mapPage.test.tsx (5, page integration, label rule, map centring, stable result-map shapes, axe 0 violations with both maps); 102 tests in all; 15 of 15 map mutants caught. Build: initial JS 86.03 kB gzip (84.02 before), map chunk 44.53 kB gzip JS plus 6.36 kB CSS loaded after the page. Browser (Claude pane, Chromium, restarted local API on current code): OpenStreetMap tiles load with no failures, the tile pane is grayscale and inverted, the credit reads "Leaflet | © OpenStreetMap contributors" on a dark box; the New Delhi button centred the picker at zoom 8; a real pointer click set 28.8696° N, 77.9897° E; a later pick replaced the city label with "Map point 28.8504° N, 77.9842° E" without moving the map; two corner clicks filled a 0.41° × 0.62° box; the box analysis (2015–2024, 13 s) showed the box outline and 9 sample points; the New Delhi point result showed only the requested point because NASA POWER reports no cell; 0 px page overflow at all nine sizes with both maps. Found and fixed in the browser: CARTO watermark tiles (now OpenStreetMap), chosen places not centring the map, the light credit box, and stale city labels after a map pick. Not covered: per-size screenshots (hidden-pane captures unreliable), a physical touch device, and an Open-Meteo result with a reported cell in the browser (covered by tests only). Production after the merge (2026-10-15, CI passed): the picker loaded OpenStreetMap tiles on climatetrend.vercel.app with the credit, and New Delhi 1995–2024 completed in 4 s with 64 calendar bars and a result map showing the requested point.

Description: Give the analysis real geographic context and a faster way to choose a place or area, without inventing spatial data.

Ownership: frontend. Concepts: 9, 17, 18, 19, 58.

Required tests: UI-GEOGRAPHY (shapes, honest cell display), picker interactions and label rule, page integration, axe, nine-size overflow, bundle report.

Documents/files: [plan](implementation-plan.md), [design](design.md), docs/screens.md, docs/system.frontend.md, [ADR-024](../../docs/decisions/README.md).

Blockers: None.

## FE-009 Start years follow the server

Priority: P1. Status: DONE. Requirements: FR-003. Dependencies: FE-006, BE-012.

Scope/files: src/api/client.ts, src/hooks/useServerStatus.ts, src/form.ts, src/components/AnalysisControls.tsx, src/DashboardPage.tsx and tests. Acceptance: the start-year validation, hint, input minimum and presets use the backend's `earliest_start_year`; a missing or invalid value keeps the 1940 outer bound; an early year is refused locally with a message naming the server's first year, and no request is sent. Evidence: 2026-10-15, commit 0012532. `checkHealth` returns `{ earliestStartYear }` (missing or non-integer → null); `useServerStatus` exposes it; `startYearFloor` keeps 1940 unless the reported year lies between 1940 and the latest complete year; validation, hint, input `min` and presets use it. Tests: tests/supportedYears.test.tsx (5); suite 107 passed; typecheck, lint pass; 8 of 8 frontend mutants caught. Browser (Claude pane, Chromium, local API with the fallback off): hint "Full calendar years from 1981 to 2025", input minimum 1981, "Full record" chose 1981–2025, 1975 was refused with "Start in 1981 or later, when the data available here begins.", focus moved to the start year and no request was sent; 1981–1990 for New Delhi then completed (24 events, 3 s). Production after the merge (2026-10-15, CI passed): the Render health response reported 1981 about 50 s after the push, and on climatetrend.vercel.app the hint read "from 1981 to 2025", the input minimum was 1981, and 1975 was refused with no request sent.

Description: Stop inviting start years the deployment cannot serve.

Ownership: frontend. Concepts: 7, 14, 24, 78.

Required tests: UI-LIFECYCLE and CONTRACT-INPUT/OUTPUT (client parsing, hook, form messages and presets).

Documents/files: [plan](../../backend/docs/implementation-plan.md), docs/state.md.

Blockers: None.

## Shared workflow checkpoints

[The canonical workflow](../../docs/ai-development-workflow.md) owns the six roles and stage gates. Shared DOC-006 audits tools/compatibility, DOC-007 integrates rules/traceability/checkpoints, and conditional DOC-008 owns individual approved installation plus smoke testing; their definitions remain in root TASKS.

For each significant FE task, expand its slice in [implementation plan](implementation-plan.md), record approval and official research for the chosen package versions, then verify/review/simplify/recheck against its existing acceptance. FE-001 uses UI-DESIGN and initial narrow/keyboard smoke; FE-002 adds request/contract race tests; FE-003 validates backend result meanings and accessible chart alternatives; FE-005 owns all nine real viewport, accessibility and performance evidence. Impeccable/manual review must follow [design](design.md). Record findings, fixes and skipped prerequisites in task evidence; none of these instructions complete FE work.
