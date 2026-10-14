# Frontend durable context

- Workspace began empty; no existing stack or user modifications were replaced.
- User confirmed foundation here. The 85-concept alignment is complete. The monochrome design update is complete; the subsequent user request adds shared AI-development workflow guidance; backend drafts exist but frontend remains documentation-only.
- FE-001 stack: React 19.3, Vite 8.3.1, TypeScript 6.0.3 (typescript-eslint caps TypeScript <6.1), Vitest 5 + jsdom 29 (jsdom 30 needs Node ≥24.15). Install with `--ignore-scripts`; source-map-js is overridden to 1.2.2 for GHSA-68fv-2mgg-jv7q. Vitest needs `css: true` or `?raw` CSS imports come back empty. Recharts still provisional.
- frontend/docs/design.md now owns the monochrome tokens and interaction/visual rules; root DESIGN links to it. Latest supplied files supersede prior colored accents. No reference image/local cloud asset was supplied.
- Root analysis contract 0.2 owns all result meanings, including the NASA/ERA5 source object (DOC-004, approved 2026-10-14). Backend owns science.
- One page, local state, explicit request cancellation/token checks; no global store/calendar library.
- All concepts map to docs/tasks/tests in the shared coverage matrix; deferred infrastructure is not a required installation.
- FE-001 checks and a nine-size idle-shell overflow pass ran 2026-10-14; FE-005 viewport acceptance remains open. See [state](state.md) and [tasks](tasks.md).

- Design-phase user clarification: align design/project documents only; do not start a scaffold for this update. Preserve explicit no-events versus insufficient-data semantics; current API does not allow stale-result fallback. Chart series/status must be distinguished through patterns, markers and labels, not hues. Use #737373 essential control boundaries; #454545 remains decorative.

- [The shared AI workflow](../../docs/ai-development-workflow.md) owns all six role passes and approval/completion gates. Use official version-specific research when Context7 is absent; no team plugin is installed. Keep one visual authority and one viewport evidence log. Significant implementation needs an approved concrete plan; routine edits within existing approval do not need repeated confirmation.
- Charts are hand-built SVG drawn in a viewBox sized to the last measured width; CSS scales it to 100%, so stale ResizeObserver measurements (hidden tabs pause them) never clip. No chart dependency.
- Dev proxy: Vite forwards /api to 127.0.0.1:8000; production builds set VITE_API_BASE_URL for the separate API domain (ADR-023).
- A hidden Claude browser pane pauses rendering, timers and ResizeObserver; layout measurement still works, screenshots and timing do not.
- Review feedback (2026-10-14) asked for clean time-series visuals, a snappy UI and a README of decisions/trade-offs. Accepted order: FE-006 fast start, FE-007 heatwave calendar (both DONE), then a Leaflet map (not Mapbox: needs a key), then the README rewrite. Calendar excess bins are display groupings of backend values only.
- Saved results use exact input keys, never rounded ones: JavaScript and Python round half-way cases differently, so rounding could reuse a result for a point the backend treats as different.
- `ResultsView` owns hovered and selected year; charts take them as optional controlled props and keep their own hover when used alone. Pointer positions must be mapped through the viewBox scale.
- Development StrictMode mounts the page twice, so the browser shows one aborted and one completed health request; production sends one.
