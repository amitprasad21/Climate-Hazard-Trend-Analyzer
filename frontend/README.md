# Frontend

React/TypeScript single-page climate dashboard: place search, validated settings, a wake-up check for the sleeping free-tier API, live analysis requests with stale-response protection, saved results reused within their backend expiry, honest loading stages, a map picker for points and boxes, and backend-driven metrics, a heatwave calendar linked to three line charts by year, a result map, provenance and insights in the monochrome design.

Verified commands, run from this directory on Node 24.12 / npm 10.2.5 (2026-10-14):

```powershell
npm ci --ignore-scripts
npm test
npm run typecheck
npm run lint
npm run build
npm run dev
```

`npm run dev` serves http://127.0.0.1:5173 (loopback only) and proxies `/api` to the backend on 127.0.0.1:8000 (see [backend README](../backend/README.md)). Production builds set `VITE_API_BASE_URL` to the API origin, which must also be in the backend's `ALLOWED_ORIGINS`. The root `.claude/launch.json` entry `frontend` starts the dev server for the Claude desktop browser pane.

Read [instructions](AGENTS.md), [docs](docs/README.md), [tasks](docs/tasks.md), [design](docs/design.md) and the [contract](../INTEGRATION_CONTRACT.md). `src/` owns source and `tests/` owns tests. Charts are hand-crafted accessible scalable SVGs with data table alternatives; zero external chart dependencies keep the initial bundle at 86.03 kB gzip. Leaflet 1.9.4 draws the maps from OpenStreetMap tiles (no key; OSM's light-use policy and credit apply) and loads in its own 44.53 kB gzip chunk. Browser-native year inputs and semantic controls precede a calendar/UI dependency.

The frontend renders backend results, never scientific calculations. A production API failure is visible with safe error envelopes rather than replaced with fake climate values.

This directory belongs to the single root repository ([DOC-002](../TASKS.md)). All 111 frontend tests, automated accessibility audit (0 axe-core violations), and 9 responsive viewports (320px–1920px) are verified.
