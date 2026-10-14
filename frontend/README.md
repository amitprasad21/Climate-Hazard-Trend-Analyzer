# Frontend

React/TypeScript single-page climate dashboard: place search, validated settings, live analysis requests with stale-response protection, and backend-driven metrics, charts, provenance and insights in the monochrome design.

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

Read [instructions](AGENTS.md), [docs](docs/README.md), [tasks](docs/tasks.md), [design](docs/design.md) and the [contract](../INTEGRATION_CONTRACT.md). `src/` owns source and `tests/` owns tests. No global state library or router is currently needed for one page. Recharts is proposed for FE-003, not installed. Browser-native year inputs and semantic controls precede a calendar/UI dependency.

The frontend renders backend results, never scientific calculations. A production API failure must be visible rather than replaced with demo climate values. Test fixtures belong only in tests or explicitly labeled development views.

This directory belongs to the single root repository; no commits, remote or deployment exist yet. AI work so far is documentation and planning; no live dashboard audit has occurred.
