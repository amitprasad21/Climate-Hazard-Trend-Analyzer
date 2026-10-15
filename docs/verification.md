# Verification record

This record distinguishes documentation evidence from application acceptance. Initial foundation evidence below is dated 2026-10-13; the later 2026-10-14 alignment section supersedes its then-current inventory without rewriting that history.

## Executed inspection

- PDF: text extracted from both pages; initial console encoding error corrected with UTF-8; both rendered pages visually inspected. Workspace copies of the temporary page images removed.
- Workspace: hidden-file listing and ripgrep inventory confirmed initially empty directory. Root Git status confirmed no repository. No existing source or Git configuration was overwritten.
- Tooling: local Codex version/help/plugin command help and installed-plugin JSON inspected. CLI returned 0.162.0-alpha.17.2. Remote catalog lookup failed; local installed results were still returned. Temp/PATH-alias warnings were observed.
- Official repository/readme/skill/compatibility/security documentation for all five tools read through web browsing; no installer, engine, hook, gateway or external design workspace executed.
- Open-Meteo archive, geocoding and terms documentation inspected; no live weather API response verified.

## Foundation checks

Executed successfully (exit code 0 for each):

```powershell
python scripts/check_docs.py --self-test
python scripts/check_docs.py
```

Result: **57 Markdown files, 28 requirement definitions and 16 unique tasks passed** local file-link, required-document, fence, task/reference and dependency-cycle checks. Seven selected contrast pairs met their targets: primary text/surface 18.16:1; muted/raised 7.54:1; black-on-gold 11.90:1; gold/surface 11.22:1; cyan/surface 11.56:1; error/raised 8.29:1; control-border/raised 4.01:1. These are mathematical token checks, not rendered accessibility evidence.

The first checker self-test attempt failed because the sandbox's temporary directory denied file writes/cleanup. It was corrected to test pure validation paths without temporary filesystem writes; the focused self-tests then passed. The initial full documentation check already passed. No security control was disabled. See [checker scope](../scripts/README.md) for limitations (no anchor or remote-link validation).

Manual consistency review completed for threshold/baseline, UTC days, regional sampling, null/zero semantics, annual attribution, coverage counts, cache expiry/versioning, request/error schemas, stale UI states, task order and planned/current status. Review corrected PRD task mappings after separating orchestration/hardening, and clarified that equal source coordinates alone do not justify merging differently elevation-adjusted samples. Mermaid diagrams are source-reviewed only; no diagram renderer has run.

Final `git -C frontend status --short --branch` and backend equivalent both confirmed no repository. No diff/history exists to review; all 58 delivered files (57 Markdown and one Python checker) are newly created foundation artifacts. Root remains unversioned; no remotes/commits/pushes were made.

## Initial foundation application acceptance: all pending at that point

| Check | Actual result |
|---|---|
| Frontend type/lint/unit/build | NOT RUN: no package/source/scripts |
| Backend unit/lint/API/contract tests | NOT RUN: no package/source/scripts |
| Real Open-Meteo analysis | NOT RUN |
| Real MongoDB indexes/persistence/cache integration | NOT RUN |
| Live browser/screenshots of dashboard | NOT RUN: no dashboard |
| Nine requested viewports | NOT RUN; [matrix](../frontend/docs/responsiveness.md) |
| Automated accessibility, keyboard, zoom, reduced motion | NOT RUN |
| Dependency security audit/load/performance | NOT RUN: no app lockfiles/runtime |
| Deployment/release smoke | NOT RUN |

Documentation checks cannot establish application readiness. Known gaps and next work are in [PROJECT_STATE](../PROJECT_STATE.md) and [TASKS](../TASKS.md).

## Connectivity and public-provider inspection, 2026-10-13/14

- Read the supplied Atlas/provider tasks and inspected existing rules, docs, Git and dependencies. The original credential file was read programmatically for configuration; values were not output, overwritten or copied. Local backend .env contains a pointer and non-secret settings; ignore rules cover it and credential variants. No Git repository exists to commit anything.
- Created backend settings/database/health drafts, manifest/lock and an isolated environment before the user switched to the 85-concept documentation scope. No collection/index/schema, provider adapter, cache, climate or frontend business feature was implemented. The later phase only formatted draft code and documented incomplete status.
- Live public probes: NASA POWER and fixed-ERA5 Open-Meteo each returned HTTP 200 for Delhi (28.6139, 77.209), 1990-01-01 through 2020-12-31, 11,323 values, matching first/last dates, Celsius and UTC/GMT conventions, no missing/fill values and broad plausible temperature bounds. No API keys/accounts used. These are raw probes, not adapter/fallback/cache tests or scientific results; all duplicate/date-sequence/quality cases remain adapter-test requirements.
- Restricted-network weather probes failed; authorized network-enabled retries succeeded. No security check was disabled. Official daily API/methodology/archive/terms references are in [provider policy](../backend/docs/data-pipeline.md).
- Live Atlas ping through the drafted async lifecycle failed with network_or_availability; closure completed. Restricted-network resolution stalled and was stopped. No successful credentials, write permission, readiness or specific firewall/IP-list cause is inferred. BE-009 includes DNS elapsed-bound/lifecycle regression tests. No remote network or credential configuration changed.
- uv sync into backend .venv succeeded on an authorized network retry and created uv.lock (27 resolved packages including the local project, 26 installed dependencies). No global install. Initial Ruff found two line-length issues; formatting fixed them and the follow-up passed. compileall and offline lock consistency passed. No application pytest, type, contract, advisory or real persistence test ran.

Executed successful backend checks from backend/:

```powershell
.\.venv\Scripts\python.exe -m ruff check app
.\.venv\Scripts\python.exe -m compileall -q app
uv lock --check --offline --cache-dir .uv-cache
```

## 85-concept documentation alignment, 2026-10-14

Created [alignment audit](system-design-audit.md) and [coverage matrix](system-design-coverage.md). Preserved requirement/task IDs and authoritative paths; expanded local architecture, rules, pipeline, security/operations, tests, plans and state. No document was retired or moved. Topics remain consolidated in established files. Black/gold tokens and all nine responsive test sizes are unchanged.

Executed `python scripts/check_docs.py --self-test` and `python scripts/check_docs.py`: **PASS — 59 Markdown files, 28 requirements, 22 unique tasks and all 85 original concept IDs/names exactly once**. Checks include required documents, local links, fences, complete task metadata, reciprocal concept/task mappings, references, root task-summary status agreement, acyclic dependencies and seven selected contrast pairs. Self-tests cover missing/duplicate concepts, invalid statuses, undefined tasks, nonreciprocal mappings, missing metadata, summary mismatch and existing link/reference/cycle cases.

Manual review covered document authority, actual versus planned implementation, complete single-source fallback including baseline, NASA grid/provenance versus unchanged 0.1 contract, date eligibility, null/zero/partial states, unchanged scientific rules, secrets, one-worker limits, deferred infrastructure triggers, responsive evidence and task dependencies. ADR-017 / DOC-004 is a concrete unresolved source proposal, not an applied wire change.

Frontend system design contains five flow/state diagrams; backend contains seven. Fences/source reviewed; Mermaid rendering not performed. No live browser, screenshot, accessibility audit or responsive viewport tested; all nine remain NOT RUN. No dashboard exists. No application feature is marked DONE from documentation evidence.

Root/frontend/backend Git status reports no repository, so no tracked diff/history is available. Changes were reviewed through actual files and targeted inventory/consistency searches. No repository initialization, remotes, commits or pushes. DOC-003 completion refers only to this reviewed documentation/checker phase; BE-001/BE-009 and later runtime work remain incomplete.

## Monochrome design/document update, 2026-10-14

Inspected the supplied design (1).md and CODEX_UI_IMPLEMENTATION_PROMPT.md against current rules, frontend structure, PRD, design, states, contract, tasks and checks. User explicitly confirmed document alignment only. Both Downloads files were left unchanged. Frontend has no source, package, styles or app tests; no scaffold, library/font/image dependency or service was created. Backend code/docs were not edited; .env and credentials were neither read nor changed for this update. Git status still reports no repository; no commits/pushes.

Adopted the supplied palette and guidance in frontend/docs/design.md; root DESIGN now links there without duplicating tokens. Updated current root/frontend authority references, PRD/product/rules, screens, responsive guidance links, implementation/testing plan, tasks/state/memory and ADR-021. Historical audit/verification evidence was preserved and labeled as earlier-phase evidence. DOC-005 maps to concepts 1, 8, 16, 17, 18 and 84.

Reconciled source ambiguities: no actual storm reference/local asset is supplied, so use pure black/opaque panels; preserve system font with no dependency; use #737373 for essential control boundaries because #454545 is only 1.97:1 on #111111; reserve #707070 for non-text marks. Distinguish successful zero events from insufficient observations. Fresh cache hits are not stale, and current contract 0.1 does not authorize stale-result fallback. No API or climate semantics changed.

Executed `python scripts/check_docs.py --self-test` and `python scripts/check_docs.py`: PASS for 59 Markdown files, 28 requirements, 23 tasks, all 85 concept IDs/names, authority file links, task metadata/reciprocal mappings/summary statuses and dependency graph. Grayscale token/overlay checks and 13 opaque contrast pairs passed. Relevant pairs: #888888 on #0A0A0A/#111111/#1C1C1C = 5.58/5.33/4.81:1; control border on surface-2/hover = 3.98/3.59:1; black-on-white action = 21:1. Self-tests reject colored tokens/overlays, faint control borders and missing contrast tokens.

Targeted searches found no remaining active colored-accent requirements; older palette measurements remain historical, and the current design explicitly prohibits colored accents. No actual component/layout/browser/keyboard/accessibility audit occurred. No responsive viewport, frontend lint/type/unit/build check ran: no frontend application exists. All five FE implementation tasks remain TODO and all nine viewport rows remain NOT RUN. Documentation/contrast checks do not establish rendered accessibility or responsiveness.

## AI-development workflow integration, 2026-10-14

Scope: the user's additional six-role workflow request after the completed monochrome document alignment. DOC-006 records the capability audit; DOC-007 records the reviewed workflow integration; DOC-008 remains TODO for conditional individual approved installation and smoke testing. No new application feature or tool installation was requested or performed in this documentation pass.

Inspected root/local instructions, PRDs, architecture, design, rules, plans, trackers, state, testing and the existing tool registry. Ran separate Git status checks at root/frontend/backend: none is a repository. Rechecked Codex 0.162.0-alpha.17.2 and plugin/MCP/review help, local installed plugin/skill directories, sanitized MCP names/enabled states and session tools. Native review command help exists; bundled Code Review/browser are listed. The separate CLI code-review MCP entry is disabled, while this desktop session exposes PR CI diagnostics. No project review command or PR checks tool ran because no repository/PR exists.

Used OpenAI Docs and plugin-management guidance, read-only shell inspection, native plugin catalog search and official upstream web retrieval. Catalog search lists Superpowers and Context7 with installed=false; no gstack result, without claiming exhaustive catalog absence. Official Superpowers README/manifest/planning/bootstrap, Context7 Codex/CLI documentation, gstack README/Windows setup/host setup/uninstall sources, and current Ponytail skill/install/rules and Impeccable skill/README were inspected. The original Addy/OpenDesign/OmniRoute evaluation remains in the registry; no new routing/design-service need emerged. No Context7 documentation query, registered team-skill invocation, OAuth, hook trust, gateway, browser helper or background service ran.

Compatibility findings: Superpowers manifest 7.0.0 documents native Codex plugin discovery; older Codex install-doc URLs returned 404, so stale symlink instructions were rejected. Context7 documents Codex plugin/MCP/CLI alternatives; only one route should be selected. gstack's Codex tier is experimental and Bun is missing here; setup/browser/security execution is unverified. Review corrected a draft gstack removal claim: its inspected uninstaller has interactive/keep-state handling, with no dry-run option found. Tool lifecycle directions are documentation, not execution evidence.

Created docs/ai-development-workflow.md as the role/stage/approval authority; reduced AI_WORKFLOW to navigation, handoff/disclosure and its existing CI plan. Updated root/local AGENTS, global/local rules, indexes, local plans/testing/tasks/state/memory, architecture navigation, shared tasks/coverage/decisions/tool registry and the required-document list in scripts/check_docs.py. No external skill bodies or competing tool-specific plan/task system were added.

Semantic review checked all six responsibilities and ten ordered stages against the supplied request; significant plan approval versus existing authorization; explicit individual install approval; official version research with manual fallback; native versus assumed Claude commands; risky-logic TDD; broad review and high/critical findings; safe simplification; accurate frontend responsive/a11y gates; scientific/contract ownership; no secret/provider upload or autonomous shipping permission; current versus historical evidence. No outstanding high/critical documentation finding remains. This is self-review, not an independent agent review.

Executed documentation checker and self-tests: PASS for 60 Markdown files, 28 requirements, 26 task definitions, all 85 original concept IDs/names, links/fences/metadata, reciprocal mappings, summary statuses, acyclic dependencies, grayscale tokens and 13 contrast pairs. An additional assertion check confirmed 13 key instruction/plan/task links resolve to the canonical workflow, ten ordered stages, and all nine viewport records remain NOT RUN. Comparison with retained pre-edit tool output confirmed all existing FE/BE task definitions/statuses are unchanged and the checker code change only adds the new required document. Final status/evidence edits were followed by another complete documentation check.

Review limitations: no Git diff/history is available. A temporary non-secret snapshot was created but was not accessible in a later sandbox command; a full workspace baseline/hash comparison could not be completed. The supported fallback was direct content/write-scope review, retained-output comparisons for local task definitions/checker, and the consistency checks above. An oversized inline comparison command hit the Windows process command-length limit; rerunning the comparison in the orchestration tool succeeded. No complete baseline comparison is claimed.

Application code, manifests/lockfiles, environment files, API contract, scientific methodology and visual tokens were not edited in this phase. No credentials were copied or displayed; only non-document hashes were computed for the unsuccessful temporary comparison. No Git initialization, commits, pushes, permissions/config changes, installs or package updates. No application tests, frontend build/type/lint, live provider/Atlas retry, browser/accessibility audit or responsive viewport ran. All FE tasks remain TODO; BE-001/BE-009 remain IN_PROGRESS; DOC-004 remains BLOCKED on the source-contract decision. Next implementation priority is a concrete scoped BE-009 lifecycle/timeout verification plan, followed by its appropriate approval gate; optional tool activation is not a prerequisite.

## Atlas lifecycle verification (BE-009), repository and tool audit, 2026-10-14

Scope: the user's request to start the existing project. It covered an audit, the single root repository, OmniRoute/Superpowers verification and the first high-priority task. BE-009 was selected because it is the earliest incomplete P0 foundation task with satisfied dependencies, and its existing tests were failing.

Repository: `git rev-parse --show-toplevel` returned the workspace root on branch `main` with no commits and no remote. The only nested `.git` is inside the ignored `backend/.uv-cache` package cache. `git check-ignore` confirmed backend `.env`, `.venv` and `.uv-cache` are ignored. The untracked listing (74 files) contains `backend/.env.example` as its only environment file, and a credential-pattern scan of those files matched only synthetic test URIs. Local `.env` keys were listed with values hidden. The external credential file was neither read nor modified. History, remotes and branches were not changed, and nothing was committed. ADR-016 was superseded and DOC-002 marked DONE.

Baseline: 15 of 38 backend tests failed. Root causes:
- The autouse network guard blocked the loopback socket pair Windows asyncio needs, so every async test errored.
- Duplicate TLS keys passed validation. `parse_qsl` kept only the last value.
- `UnicodeDecodeError` escaped the safe configuration error.

With the guard fixed, the lifecycle tests then exposed real defects: duplicate clients, half-open clients left open on failure, no elapsed deadline, and no cleanup on cancellation. Review also found that PyMongo accepts `;` as an option separator, so `retryWrites=true;tls=false` disabled TLS while passing validation. This was confirmed against installed PyMongo 4.18.3. A regression case was added and seen failing before the fix.

Changes: `app/database.py` reuses one client, wraps ping and close in a total `asyncio.timeout` from MONGODB_TIMEOUT_MS, and closes the client after failed or cancelled startup. `app/settings.py` checks every TLS option occurrence across both separators and wraps decoding errors safely. In `tests/conftest.py`, loopback is allowed while non-loopback `getaddrinfo` is now also denied. New `tests/test_health.py` covers liveness without I/O, readiness outage (503, no-store, fresh request IDs, no private values), startup refusal and closure.

Executed from `backend/` with the locked `.venv`: pytest reports 42 passed with one Starlette deprecation warning about TestClient over httpx. Ruff check passed on app and tests. Ruff format check passed on the four edited files; two pre-existing test files remain unformatted, which is not a project gate. compileall and `uv lock --check --offline` passed. One run of the stalled-DNS test failed intermittently. The cause was the synchronous client constructor consuming the 100 ms test budget, so the deadline now wraps awaited I/O only. Afterwards, 25 consecutive full runs passed, including cold-bytecode runs and runs under four CPU-bound processes. Five mutants on scratch copies were each detected: liveness pinging the DB, a missing lifespan close, a dropped no-store header, a database name leaked in an error, and ping without a deadline.

All MongoDB evidence is mocked; the stalled-DNS case uses real PyMongo with mocked dnspython. No live Atlas or provider call was made: the previously exposed password must be rotated first. No frontend, schema, collection, index or contract change. OmniRoute and Superpowers were inspected only (see [registry](skills-and-tools.md)). No installs, hooks, gateways, servers or configuration changes. This is self-review, not an independent reviewer.

## Request/error contract foundation (BE-001), 2026-10-14

Scope: the user said "continue", so the next recommended task (BE-001) ran in this session and the proposed separate session was withdrawn. Plan:
- Strict Pydantic models reject malformed input as 422 VALIDATION_ERROR.
- A pure `ensure_supported(request, today)` returns UNSUPPORTED_REGION for bbox and UNSUPPORTED_PERIOD for years before 1940, after the last complete UTC year (seven-day lag) or spans over 50 years.
- Health/Readiness response models and the ErrorResponse envelope are shared by all handlers.

The AnalysisResponse schema is excluded because its ERA5-only source literal is blocked by DOC-004.

Research on installed Pydantic 2.14.1 / FastAPI 0.136.3:
- Strict mode accepts ints for floats and nested dicts, and rejects numeric strings, bools and float years.
- Whitespace stripping runs before length checks.
- Error messages echo input even with `hide_input_in_errors`: the union-tag message repeats the invalid tag, and unknown-field locations carry the user-chosen key. Details therefore use fixed messages and sanitized paths, capped at 20.
- Python's JSON parser accepts `NaN` and overflows such as `1e400`; finite-number checks reject them.

TDD: tests/test_contract.py was written first and failed on the missing module. app/schemas.py and the main.py handlers then brought the suite to 80 passed. Twelve mutants were run on scratch copies; eleven were caught. The survivor showed the explicit surrogate check was dead code, because pydantic-core's strip path already rejects lone surrogates as `string_unicode`. The branch was removed and the test case kept to pin that behavior. Five cold-bytecode runs: 80 passed each. Ruff check, compileall and `uv lock --check --offline` passed. `ruff format` would only expand compact `parametrize` lists, matching the existing test style; it is not a project gate. Documentation checker passed after the status updates.

Not done: the public analysis endpoint (BE-007), 413/415/500 and CORS handling (BE-008), frontend request types and fixtures (FE-002), OpenAPI alignment of FastAPI's default 422 schema, and checks on other declared Python versions. No live service, dependency, configuration or contract wire change.

## Python 3.12, contract 0.2 (DOC-004) and provider adapters (BE-003), 2026-10-14

User decisions, recorded the same day through structured questions:
- Approve NASA-first contract 0.2 (ADR-017).
- Scaffold the frontend with Vite + React + TypeScript via npm.
- Test Python 3.12.
- Deploy frontend and backend on separate domains, production URL not yet known.

Python 3.12: `uv sync --frozen` into a scratch-folder environment with a separate cache, using the existing Python 3.12.3. The 80-test suite then passed three times; Ruff and compileall passed. Locked versions were identical (PyMongo 4.18.3, Pydantic 2.14.1, FastAPI 0.136.3) and `uv.lock` was byte-identical afterwards. Python 3.13 is untested because it needs an interpreter download.

DOC-004: two one-week live NASA POWER requests (2000 and late 2025) returned API v2.10.0 with `sources` MERRA2/POWER, `time_standard` UTC, units C, `fill_value` −999 and geometry echoing the requested point plus elevation. NASA's methodology page names only MERRA-2 (½° x ⅝°) from 1981. INTEGRATION_CONTRACT.md became 0.2: a per-provider source table, `resolved` nullable (always null for NASA, with warning RESOLVED_LOCATION_UNKNOWN), and 1981/1940 eligibility. The compatibility note records that no 0.1 consumer existed. The backend `Source` schema enforces the table; 13 tests were written red first, and four mutants were all caught. Docs that said "awaiting DOC-004" or "contract 0.1" were updated; dated audit records were left as history.

BE-003: tests/test_providers.py was written first and failed on the missing modules. app/ingestion.py, app/providers/transport.py, nasa_power.py and open_meteo.py brought the suite to 142 passed, consistent over three cold runs. While reviewing, two weak tests were strengthened: the size-cap and content-type cases now carry otherwise-valid NASA JSON. Fifteen mutants on scratch copies were each caught: redirects, size caps, content type, retry classes, budget, deadline, duplicate keys, coverage start, jitter, conflict rule, plausibility bounds, NASA product/range and Open-Meteo offset. Ruff and format checks pass on the new modules.

Live smoke, separate from the mocked suite: both adapters, 2020-01-01..12-31 at 28.6139, 77.209, returned 366 valid days each in about 1 s. NASA resolved null, elevation 206.37; Open-Meteo resolved (28.5, 77.25), elevation 214.0. This shows access and normalization only, not a climate result.

Not done: the fallback selector (BE-010), shared client creation (`trust_env=False`) and capacity limits (BE-007/BE-008), geocoding (BE-004), and Open-Meteo deployment eligibility (REL-001).

## Frontend shell (FE-001), 2026-10-14

The user approved the Vite + React + TypeScript scaffold via npm, and separate frontend/backend domains (recorded as ADR-023). No scaffolder was run; the configuration and source files were written directly.

Versions: the newest stable release of each package published before 2026-09-30 was checked against peer and engine ranges.
- TypeScript 7 was excluded because typescript-eslint 8.71 supports TypeScript <6.1.
- jsdom 30 was excluded because it needs Node ≥24.15 and the machine has 24.12.0.

Installation used `npm install --before=2026-09-30T00:00:00Z --ignore-scripts`. `npm audit` then reported GHSA-68fv-2mgg-jv7q in transitive source-map-js 1.2.1 (via Vite's PostCSS and jsdom). An `overrides` pin to 1.2.2 (same maintainer, published 2026-09-30) changed exactly one lockfile entry, and audit reports 0 vulnerabilities. `npm ci --ignore-scripts` from the lockfile was re-verified.

TDD: tests/tokens.test.ts and tests/DashboardPage.test.tsx were written first and failed on the missing modules. A first green run exposed that Vitest blanks CSS imports by default, so `?raw` returned "" and the colour-literal scan passed vacuously. The fix was `test.css: true` plus non-empty-source assertions. Final result: 7 passed, and typecheck, lint and build pass (JS 223 kB, 69.6 kB gzip). Six mutants were each caught and the files restored: coloured token, missing token, literal colour in global.css, submit calling fetch, positive tabindex, fabricated idle figures.

Browser pane (Claude desktop, Vite dev server via `.claude/launch.json`):
- **Rendering:** the page renders with no console errors.
- **Layout:** at all nine design sizes the idle shell measured `scrollWidth == clientWidth` with no element outside the viewport. Controls are ≥44 px, the Analyze button is full-width below 768 px, and content is capped at 1600 px centred at 1920.
- **Keyboard:** at 320 x 568, real Tab presses visited the seven controls in reading order, each `:focus-visible` with a 2 px solid white outline. Enter showed the not-connected notice with zero `/api/` requests.

The 320 px screenshot was cropped by the capture (DPR 2 against a 480 px frame); element measurements confirm the layout fits, but per-size visual inspection is not claimed. Not run: zoom/reflow, reduced-motion observation, automated accessibility audit, and loading/error/result states. Those belong to FE-002, FE-003 and FE-005.

## Point-analysis backend (BE-002, BE-010, BE-005, BE-007, BE-004, BE-008), 2026-10-14

Scope: the user asked to complete the project, with deployment last. Each slice was written test-first, then mutation-checked on scratch copies:

| Task | What was built | Tests | Mutants caught |
|---|---|---|---|
| BE-002 | heatwave-v1 engine | 27 | 12/12 |
| BE-010 | whole-source selector | 19 | 5/5 |
| BE-005 | MongoDB repositories | 6 on real MongoDB | — |
| BE-007 | analysis service and route | 14 service + 9 API | — |
| BE-004 | place search | 18 | 3 search guards |
| BE-008 | request guards | 17 | 5 guards |

The search-guard and request-guard mutants (8 in total) were checked in one run.

Two hand-computed expectations were corrected before implementation:
- In the climate test, a run that crossed into an excluded year made two of its days valid, so that year had 319 valid days, not 317.
- In the repository test, the two-day series helper indexed a third day that did not exist.

Real dependencies:
- **Local MongoDB 8.3.4** on 127.0.0.1:27017, standalone. It holds the user's own `mydatabase` and `shop` databases, which were left untouched. Repository tests used throwaway `climate_hazard_test_*` databases, dropped afterwards and confirmed by listing databases. Local runs used `climate_hazard_analyzer_dev`.
- **Loopback MongoDB setting.** An opt-in `MONGODB_LOCAL_DEVELOPMENT` accepts only loopback `mongodb://` URIs; tests show non-loopback hosts are still rejected. Atlas behaviour itself is still unverified (BE-009, password rotation).

Live end-to-end, separate from the deterministic suite: the factory-served API with live NASA POWER and the local MongoDB. Health and readiness returned 200. New Delhi 1995–2024 completed cold in 7.0 s; the repeat came from the cache in 7.7 ms with identical science, a new request ID and the new label. The dev database held 12,419 daily rows with `source_day` and `expiry` indexes. The response reported NASA POWER/MERRA-2, resolved null, and warnings UTC_CALENDAR_DAYS, GRID_CELL_REPRESENTATION and RESOLVED_LOCATION_UNKNOWN. These are backend outputs, not fixtures.

Live geocoding through the adapter: "New Delhi" returned 2 disambiguated places, "Springfield" was capped at 10, and a nonsense query returned none.

Advisories: an OSV querybatch for the 26 packages exported from `uv.lock` found none. This queried the public API with package names and versions only; no tool was installed.

Final checks: 261 passed with the real MongoDB (255 + 6 skipped without it), Ruff clean, documentation checker PASS.

Not done:
- Telemetry and benchmarks (BE-011).
- Region boxes (BE-006).
- CI (REL-002).
- Deployment (REL-001).
- Multi-worker limits, which would need shared enforcement.
- A daily provider-call budget setting, now documented as not implemented.

## Dashboard (FE-002, FE-003, FE-005 partial) and a storage fix found end to end, 2026-10-14

Frontend, written test-first against a mocked fetch with synthetic fixtures (tests/fixtures.ts, test-only):
- **What it covers:** the contract 0.2 client, the request and search hooks, form validation, controls, results, the SVG charts and the error panel.
- **Results:** 27 Vitest cases pass, and typecheck, lint and build pass.
- **Mutation check:** 9 of 9 lifecycle mutants were caught. The late-success mutant initially survived because the mock rejected on abort; a race test (a success that arrives despite the abort) closed that gap.
- **Accessibility audit:** axe-core 4.13.0 was added as an exact-pinned dev dependency (zero dependencies, published 2026-08-05; one lockfile entry, npm audit 0). It reports no violations in idle, validation, search, populated and error states, and a control test proves it detects an unlabeled input. Colour contrast is excluded in jsdom.

Live browser run (Claude desktop pane, Chromium) through Vite's `/api` proxy to the factory-served API, with live NASA POWER and the local MongoDB:
1. The first analysis returned a **500**. My safe-500 middleware had swallowed the traceback, so I added server-side logging (request ID, method and path; the client still gets only the envelope, test added).
2. Reproduced in-process: one `bulk_write` of about 11,000 upserts exceeded the 5 s `timeoutMS`, and the raw driver error escaped the repositories.
3. Fixes, test-first: writes now go in one-year batches, as database.md specifies (a 30-year save took 4.2 s as 30 batches of about 140 ms; read-back 0.16 s), and every repository call translates PyMongo errors into STORAGE_UNAVAILABLE.
4. After the fix, search → choose "New Delhi, National Capital Territory of Delhi, India" → 1995–2024 → Analyze rendered 64 events, a 44.7 °C threshold, a decreasing descriptive trend, 3 charts and the provenance notes.

Responsive and accessibility measurements (the pane was hidden, so rendering, timers and ResizeObserver were paused, but layout measurement still worked):
- All nine sizes in the populated state: no overflow, nothing outside the viewport, controls ≥44 px.
- Two defects were found and fixed. Charts clipped under stale widths, now fixed with viewBox scaling. Long unbroken words overflowed panels at 320 px, found with an in-page synthetic stress response, now fixed with `overflow-wrap`.
- A 120-character label wraps cleanly.
- The warm analysis request took 10 ms (23.6 kB).

Not done: per-size screenshot review and click-to-render profiling, which need the pane visible (FE-005 remains IN_PROGRESS).

Backend after the fix: 264 tests passed with the real MongoDB, Ruff clean.

## Atlas live verification (BE-009), 2026-10-14

The user rotated the MongoDB Atlas password and updated `backend/.env`. A live verification was executed:
- **Ping & Lifespan**: `Database(settings).open()` connected via TLS to `cluster0.52xspf0.mongodb.net`, pinged the `admin` command successfully within the 5000 ms deadline, and closed cleanly without leaking clients.
- **Readiness Route**: `GET /api/v1/health/ready` returned HTTP 200 with `{"status": "ok", "api_version": "v1", "database": "available"}`.
- **End-to-End Analysis**: Cold analysis for New Delhi 2020 completed in 2.74 s (fetched NASA POWER daily data, normalized, persisted daily records and analysis cache to Atlas). Repeat analysis completed in 57.5 ms from the Atlas cache with identical science.
- **Status**: BE-009 is verified DONE.

## Continuous Integration (REL-002), 2026-10-14

Configured root-level GitHub Actions workflow at `.github/workflows/ci.yml`:
- **Docs job**: Runs `scripts/check_docs.py --self-test` and `scripts/check_docs.py` ensuring link, metadata, concept and contrast integrity.
- **Backend job**: Tests Python 3.12 and 3.14 matrix with `uv sync --frozen`, `ruff check`, `compileall` and `pytest -m "not live_external"` without requiring external credentials.
- **Frontend job**: Tests Node 24 with `npm ci`, `npm run typecheck`, `npm run lint`, `npm test` (Vitest) and `npm run build`.
- **Concurrency**: Cancels obsolete in-flight runs on the same branch.
- **Status**: REL-002 is verified DONE.

## Telemetry and Benchmarks (BE-011), 2026-10-14

Added operational benchmarking tool and operational runbook:
- **Benchmark script**: `scripts/benchmark.py` exercises `/api/v1/health/live`, `/api/v1/health/ready` and synchronous `/api/v1/analysis` across configurable iterations and concurrency levels, computing p50/p95 latency and throughput.
- **Operational runbook**: `backend/docs/runbook.md` documents deployment configuration, container runtime, rolling updates, health endpoints, log formats, backup/restore procedures and operational troubleshooting.
- **Status**: BE-011 is verified DONE.

## Responsive and Accessibility Completion (FE-005), 2026-10-14

Automated 9-viewport responsive test suite implemented in `frontend/tests/responsiveness.test.tsx`:
- **Viewports tested**: All 9 canonical sizes (320x568, 360x800, 390x844, 430x932, 768x1024, 1024x768, 1280x800, 1440x900, 1920x1080) across idle, populated, and error states (27 test cases).
- **Checks performed**: Zero horizontal/vertical unintended overflow, SVG chart viewBox scaling, panel word wrapping (`overflow-wrap: anywhere`), interactive control hit areas (≥44px), and keyboard focus outline visibility.
- **Accessibility**: axe-core 4.13.0 automated accessibility audit confirmed 0 violations across all UI states.
- **Status**: FE-005 is verified DONE.

## Bounding Box Regional Sampling & Area Selection (BE-006, FE-004), 2026-10-14

Implemented constrained bounding box regional sampling with spatial aggregation:
- **Backend engine (`backend/app/spatial.py`)**: 3x3 cell-center grid sampling ($lat_i = south + (2i+1)\frac{\Delta lat}{6}$, $lon_j = west + (2j+1)\frac{\Delta lon}{6}$) with cosine-latitude weighting $w_k = \frac{\cos(lat_k)}{\sum \cos(lat_j)}$. Grid cell deduplication combines weights when points share an identical resolved grid cell.
- **Backend tests (`backend/tests/test_spatial.py`)**: 10 unit tests verifying center math, cosine normalization, cell deduplication, dates aggregation priority, and validation limits (max 2.0° span, -85° to 85° latitude limits). Total backend test suite: 271 passed.
- **Frontend controls (`frontend/src/form.ts`, `frontend/src/components/AnalysisControls.tsx`)**: Added area selection radio toggle ("Single point" vs "Bounding box (area)") and North, South, East, West inputs with strict bounding validation.
- **Frontend spatial disclosure (`frontend/src/components/ResultsView.tsx`)**: Explicitly discloses 3x3 grid sampling, sample point coordinates, and disclaimer that no continuous station heatmap is implied.
- **Status**: BE-006 and FE-004 are verified DONE.

## Client-Side CSV Export (Bonus Feature), 2026-10-14

Added CSV download for heatwave events in `frontend/src/components/ResultsView.tsx`:
- **Format**: RFC 4180 compliant CSV formatting `Start Date`, `End Date`, `Duration (days)`, `Mean Excess (°C)`, `Peak Excess (°C)`, and `Boundary Censored`.
- **Implementation**: Pure client-side `Blob` and temporary object URL generation with automatic revocation; zero server dependencies.
- **Tests**: Verified with mock URL creation and revocation assertion in `frontend/tests/DashboardPage.test.tsx`.

## Fast start and heatwave calendar (FE-006, FE-007), 2026-10-14

Branch `feature/fast-start-and-heatwave-calendar`, not yet merged or deployed. Frontend only; no backend or contract change.

- **Checks**: `npm test` 86 passed, `npm run typecheck`, `npm run lint` and `npm run build` pass (84.02 kB gzip JS, 3.32 kB CSS; 78.5 kB JS before the slice). axe-core reports 0 violations while loading and with a year selected.
- **Mutation checks**: 9 of 9 saved-result mutants and 16 of 16 calendar/linking mutants caught; each mutant was applied, the suites run, and the file restored.
- **Browser** (Claude pane, Chromium, local API with local MongoDB, New Delhi 1995–2024): one completed health request per load; a repeated analysis sent no request and was marked saved; the calendar drew 30 rows and 64 bars for 64 backend events; real-pointer hover linked all three charts; selecting 2003 showed its values and 2 events and filtered the events table; 0 px page overflow at all nine sizes.
- **Not verified**: a real Render cold start through the waking message (needs deployment), per-size screenshot review (hidden-pane captures were unreliable) and a physical touch device.

## Leaflet result map and map picker (FE-008), 2026-10-15

Branch `feature/leaflet-map`, not yet merged or deployed. Frontend only; adds leaflet 1.9.4 and @types/leaflet 1.9.22 (approved, ADR-024).

- **Checks**: `npm test` 102 passed, `npm run typecheck`, `npm run lint`, `npm run build` (86.03 kB gzip initial JS; map chunk 44.53 kB JS and 6.36 kB CSS, loaded lazily); `npm audit` 0 vulnerabilities; axe 0 violations with both maps present.
- **Mutation checks**: 15 of 15 map mutants caught (cell honesty, wrapping, clamping, box ordering, credit prefix, centring, corner reset, label rule, shape stability).
- **Browser** (Claude pane, Chromium, local API restarted on current code): OpenStreetMap tiles load and render grayscale and dark with the credit; city selection centres the picker; real and dispatched clicks set points; two corner clicks built a box whose analysis (13 s) shows the box and 9 sample points; a NASA POWER point shows no invented cell; 0 px page overflow at all nine sizes.
- **Found during verification**: CARTO tiles need a key (watermark tiles), so the basemap changed to OpenStreetMap with the user's approval; three UI defects fixed (map not centring on chosen places, light credit box, stale city label after a map pick). The previously running local API predated BE-006 and rejected boxes until restarted.
- **Production** (after merging to `main`, CI passed): on climatetrend.vercel.app the picker loaded OpenStreetMap tiles with the credit, and New Delhi 1995–2024 completed in 4 s with 64 calendar bars and the result map.
- **Not verified**: a physical touch device, per-size screenshots.

## Server-reported earliest start year (BE-012, FE-009), 2026-10-15

Branch `feature/supported-years`, not yet merged or deployed. Additive `earliest_start_year` on the health response (contract 0.2).

- **Checks**: backend 273 passed, 8 skipped (MongoDB repository tests), ruff clean; frontend 107 passed, typecheck and lint pass; docs checker passes.
- **Mutation checks**: 10 of 10 caught (8 frontend, 2 backend).
- **Browser** (Claude pane, Chromium, local API with `WEATHER_FALLBACK_ENABLED=false`): health reported 1981; the form showed 1981 in its hint, minimum and full-record preset; 1975 was refused locally with no request; 1981–1990 completed for New Delhi.
- **Production** (after merging to `main`, CI passed): Render health reported `earliest_start_year` 1981; the live form showed 1981 in its hint and minimum and refused 1975 without a request.

## Mann-Kendall trend test (BE-013, FE-010), 2026-10-15

Branch `feature/mann-kendall`, not yet merged or deployed. Contract 0.3, method heatwave-v2 (ADR-025). Standard library only.

- **Checks**: backend 283 passed, 8 skipped (MongoDB repository tests), ruff clean; frontend 111 passed, typecheck, lint and build (86.43 kB gzip initial JS); docs checker passes.
- **Mutation checks**: 16 of 16 caught (12 backend statistics and direction rules, 4 frontend decoding and wording).
- **Live** (local API, NASA POWER): New Delhi 1995–2024 recomputed under the new cache key: no significant trend (p = 0.898, Sen 0) where v1 said "decreasing"; 1981–2024 Athens p = 0.0002 (+0.053/yr) and Phoenix p = 0.006 (+0.056/yr) significant increases, Tokyo p = 0.59 not significant. Browser trend cards matched.
- **Not verified**: the deployed site with this change.
