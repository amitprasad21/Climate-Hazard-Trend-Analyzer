# Project state

Last reviewed: 2026-10-14 (Asia/Calcutta). **The point-analysis and bounding box regional sampling applications work end to end (live NASA POWER, live MongoDB Atlas and local MongoDB). CI is configured, 9-viewport responsive tests pass, telemetry/benchmarks are complete, and CSV export is implemented. Deployment & release (REL-001) remain.**

## Verified facts

- Initial documentation foundation DOC-001 was checked; private PDF/master prompts and all five requested upstream tools were inspected. No optional plugin, design workspace or gateway was installed.
- Backend now contains settings, PyMongo async lifecycle, health routes, manifest/lock, an isolated virtual environment and ignored local environment. Secrets and credentials are not tracked in Git.
- 2026-10-14: 271 backend tests pass (265 deterministic + 6 on real local MongoDB). Live E2E (NASA POWER → MongoDB → engine → cache, New Delhi 1995–2024): cold 7.0 s, cached 7.7 ms. OSV finds no Python advisories; npm audit 0 vulnerabilities.
- Direct no-key NASA POWER and Open-Meteo probes for 1990–2020 returned all 11,323 daily values at the test point with expected Celsius/UTC conventions.
- 2026-10-14: The Atlas password was rotated by the user and live connectivity was verified. TLS-verified ping succeeded, readiness endpoint returned 200 available, and end-to-end analysis (New Delhi 2020) succeeded cold in 2.74 s (persisted into Atlas) and warm in 57.5 ms (cached from Atlas).
- One root Git repository (branch `main`, clean working tree) contains frontend, backend and docs; no nested repositories. Secrets/caches are ignored. Granular conventional commits track each verified milestone.
- OmniRoute and Superpowers are not installed; both were re-audited for Claude Code 2.1.241 in the [tool registry](docs/skills-and-tools.md). Installation awaits explicit approval.
- Continuous integration is configured in `.github/workflows/ci.yml` running docs, backend (Python 3.12/3.14), and frontend (Node 24) checks on GitHub pushes/PRs.
- Operational telemetry and benchmarks are implemented via `scripts/benchmark.py` and documented in `backend/docs/runbook.md`.
- 9-viewport automated responsive test suite (`frontend/tests/responsiveness.test.tsx`) verifies all canonical breakpoints (320px to 1920px) without page overflow; axe-core 4.13.0 automated accessibility audit confirmed 0 violations across all UI states.
- Enhanced UX suite verified and committed: quick year presets (`Last 10y`, `Last 20y`, `Last 30y`, `Baseline 1991–2020`, `Full record`), rapid city location chips, high-contrast trend direction badges, subtle monochrome area fill gradients, and interactive SVG crosshair line with floating tooltip cards.
- Bounding box regional sampling (`BE-006` and `FE-004`) implements 3x3 cell-center grid sampling with cosine weighting, cell deduplication, and spatial disclosure.
- Client-side RFC 4180 CSV export for heatwave events is implemented in `frontend/src/components/ResultsView.tsx` with zero server overhead.

## Current phase and task state

DOC-003 is DONE for the prior architecture documentation pass: [audit](docs/system-design-audit.md), [all 85 concepts](docs/system-design-coverage.md), expanded local designs, aligned rules and complete task metadata. Final evidence is in [verification](docs/verification.md); [TASKS](TASKS.md) is the status authority.

DOC-005 is DONE for the supplied monochrome design/UI-brief alignment. frontend/docs/design.md is the visual authority; root DESIGN links to it. 13 opaque grayscale contrast pairs pass.

DOC-006 is DONE for the refreshed tool audit. DOC-007 is DONE for [the canonical AI workflow](docs/ai-development-workflow.md), rule/plan/testing checkpoints and concept traceability. Documentation checker/self-tests pass for all Markdown files, requirements, tasks, concepts and contrast pairs. DOC-008 remains conditional TODO: no tool installation is selected or approved.

DOC-002, DOC-004, BE-001 through BE-012, FE-001 through FE-009, and REL-002 are DONE. Only REL-001 (Deployment and Release) remains TODO.

## Gaps and next work

Backend BE-001 through BE-011, FE-001 through FE-005 and REL-002 are DONE. Bounded regional sampling (3x3 grid with cosine-latitude weighting) is verified in backend and frontend. CSV export bonus slice is verified and committed. Next: REL-001 deployment and release.

Deployment target accounts/hosting, remote repository synchronization, and final production smoke test are the remaining release prerequisites.

Current work (2026-10-14): review feedback on visualization and responsiveness. FE-006 (wake-up, saved results, honest loading) and FE-007 (heatwave calendar with linked year views) were merged to `main` and deployed on 2026-10-15 (CI passed). FE-008 (Leaflet result map and map picker on OpenStreetMap tiles) and the README rewrite were merged and pushed to `main` on 2026-10-15. The root README was rewritten with an architectural decisions and trade-offs section, live links and claims re-checked against the code: corrected endpoint, collections, body limit, fallback status, benchmark command and cold-latency figures. BE-012 and FE-009 close the start-year gap: the health response reports the earliest supported start year (1981 in production) and the form follows it; merged to `main` and verified in production on 2026-10-15.
