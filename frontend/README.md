# Frontend

React/TypeScript single-page climate dashboard. **FE-001 shell only:** monochrome tokens, semantic header/form and an idle results state. It sends no requests and shows no climate figures.

Verified commands, run from this directory on Node 24.12 / npm 10.2.5 (2026-10-14):

```powershell
npm ci --ignore-scripts
npm test
npm run typecheck
npm run lint
npm run build
npm run dev
```

`npm run dev` serves http://127.0.0.1:5173 (loopback only). The root `.claude/launch.json` entry `frontend` starts the same server for the Claude desktop browser pane.

Read [instructions](AGENTS.md), [docs](docs/README.md), [tasks](docs/tasks.md), [design](docs/design.md) and the [contract](../INTEGRATION_CONTRACT.md). `src/` owns source and `tests/` owns tests. No global state library or router is currently needed for one page. Recharts is proposed for FE-003, not installed. Browser-native year inputs and semantic controls precede a calendar/UI dependency.

The frontend renders backend results, never scientific calculations. A production API failure must be visible rather than replaced with demo climate values. Test fixtures belong only in tests or explicitly labeled development views.

This directory belongs to the single root repository; no commits, remote or deployment exist yet. AI work so far is documentation and planning; no live dashboard audit has occurred.
