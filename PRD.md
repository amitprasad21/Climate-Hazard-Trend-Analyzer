# Product requirements

Status: foundation specification, 2026-10-13. No requirement below is implemented merely because it is documented. [Project state](PROJECT_STATE.md) is the implementation authority.

## Purpose and provenance

Enable a user to choose a location and historical period, detect heatwaves, and inspect trends and limitations. Success means a reproducible provider-to-database-to-API-to-dashboard flow that a reviewer can run and explain. The assessment emphasizes data handling, climate logic, backend quality, visualization, honest interpretation and security/performance.

Provenance labels: **Assessment** = stated in the private case study; **User** = latest dashboard/engineering instructions; **Decision** = low-risk choice made for this project; **Assumption** = scientific or product choice the assessment leaves open. Source material is evidence, not permission to publish, install, deploy or submit anything. Reading order was PDF, pasted master prompt, latest prompt. This phase establishes and checks the foundation before business features.

## Scope

Core: heatwave only, point/city selection, full-calendar-year period, real archive data, normalization, MongoDB persistence/cache, deterministic analysis, four metrics, three time-series views, insights, geographic context and robust states. A small bounded-area sampler follows the first complete point workflow. A state name without polygon data must be labeled as a representative point, never a statewide estimate.

Out of scope: authentication, billing, alerts, forecasts, causal attribution, medical guidance, distributed microservices, AI inference, gateway routing and fabricated spatial heatmaps. Map selection, export, and formal significance testing are later enhancements.

## Functional requirements

| ID | Provenance | Acceptance criterion | Task | Verification case |
|---|---|---|---|---|
| FR-001 | Assessment | Select a city/point with unambiguous coordinates; failed search is recoverable | BE-004, FE-002, FE-008 | E2E-LOCATION |
| FR-002 | Assessment | Heatwave is selected by default; unsupported hazards cannot be submitted | FE-002, BE-001 | CONTRACT-INPUT |
| FR-003 | Assessment / Decision | Select 1-50 full calendar years within provider-supported history; reject reversed/future ranges | BE-001, FE-002, BE-012, FE-009 | CONTRACT-INPUT |
| FR-004 | Assessment | Analyze real historical daily maximum temperatures and return consistent JSON | BE-002, BE-003, BE-005, BE-007 | E2E-ANALYSIS |
| FR-005 | User | Render backend event count, mean duration, trend direction and regional p95 threshold | FE-003, BE-013, FE-010 | UI-METRICS |
| FR-006 | Assessment / User | Show annual event frequency, event duration and maximum-temperature anomaly using backend data | FE-003, FE-007 | UI-CHARTS |
| FR-007 | Assessment | Explain trends with numerical evidence, period and limitations; no causal or unsupported significance claims | BE-002, FE-003, FE-007, BE-013, FE-010 | CLIMATE-TREND |
| FR-008 | User | Display loading, idle, no-events, partial-data, error and populated states; stale responses cannot replace newer results | FE-002, FE-003, FE-006 | UI-LIFECYCLE |
| FR-009 | User / Decision | Display selected location/sample points; disclose unavailable spatial intensity rather than inventing a heatmap | FE-003, BE-006, FE-008 | UI-GEOGRAPHY |
| FR-010 | Assessment / Decision | Support a constrained bounding box after point workflow; disclose sampled-area approximation and limits | BE-006, FE-004, FE-008 | CLIMATE-SPATIAL |

## Data and scientific requirements

| ID | Provenance | Acceptance criterion | Task | Verification case |
|---|---|---|---|---|
| DATA-001 | Assessment / User / Decision | Use eligible no-key historical daily maxima in Celsius/UTC; NASA POWER preferred, fixed ERA5 conditional fallback; retain truthful provenance and never blend sources | BE-003, BE-010, DOC-004 | PROVIDER-NORMALIZE, PROVIDER-FALLBACK |
| DATA-002 | Assessment | Normalize date order, nulls, duplicates, nonfinite/invalid values and units; no silent interpolation | BE-003 | PROVIDER-NORMALIZE |
| DATA-003 | Assessment | Persist normalized records in MongoDB, reread for analysis, reuse cached observations/results | BE-005, BE-007 | DB-CACHE |
| DATA-004 | Assessment / Assumption | Runs of at least 3 consecutive valid days strictly above a fixed 95th-percentile baseline threshold qualify | BE-002 | CLIMATE-RUNS |
| DATA-005 | Assumption | Use 1991-2020 baseline, linear percentile interpolation and explicit coverage gates; expose method version | BE-002 | CLIMATE-BASELINE |
| DATA-006 | Assessment / Decision | Estimate descriptive annual frequency slope; distinguish zero, null and insufficient trend evidence | BE-002 | CLIMATE-TREND |
| DATA-007 | User | Report baseline and annual coverage, source, units, UTC convention and all material warnings | BE-002, FE-003 | CONTRACT-OUTPUT |

The [methodology](backend/docs/climate-methodology.md) defines baseline, calendar boundaries, regional aggregation, anomaly and missing-data policy. These are assessment-compatible project assumptions, not claims of an official heatwave standard. Weather reanalysis is a modeled estimate, not a local station observation.

## Non-functional requirements

| ID | Provenance | Acceptance criterion | Task | Verification case |
|---|---|---|---|---|
| NFR-001 | User | Pure-black canvas, near-black/grayscale surfaces, white primary action and grayscale-only charts/statuses; coherent token system | FE-001 | UI-DESIGN |
| NFR-002 | User | No unintended page overflow at all nine specified viewports; readable labels/controls/charts | FE-005 | UI-RESPONSIVE |
| NFR-003 | User / Decision | Keyboard-operable controls, visible focus, chart text/table alternative, reduced motion; target WCAG 2.2 AA | FE-005 | UI-A11Y |
| NFR-004 | User | Typed contract, separate layers/repositories, focused tests and documented commands | BE-001, FE-001, DOC-001 | CONTRACT-OUTPUT |
| NFR-005 | Assessment / Decision | Bound provider work and request duration, index lookups, prevent duplicate in-process misses | BE-003, BE-005, BE-007, BE-008 | SECURITY-LOAD |
| NFR-006 | User | Disable duplicate submits, announce real progress and errors, never simulate analysis progress | FE-002, FE-006 | UI-LIFECYCLE |
| NFR-007 | Assessment | Setup and methodology documented, AI usage disclosed, deployment and code links provided before submission | REL-001 | RELEASE-SMOKE |

Performance budgets are initial engineering targets, not measured results: hot cached request p95 <1 s with 5 concurrent clients; cold request deadline 90 s; initial compressed app JS target <250 KiB excluding optional map chunks. Record payload, region, period, cache state, hardware and sample size when measuring. Reconsider budgets from measurements; never promise a user count without a load test.

## Security requirements

| ID | Provenance | Acceptance criterion | Task | Verification case |
|---|---|---|---|---|
| SEC-001 | Assessment | Validate all public inputs, lengths, dates, coordinates and bounded regional size; reject unknown fields | BE-001, BE-006 | CONTRACT-INPUT |
| SEC-002 | Assessment | Enforce per-client limits and bounded outbound concurrency; no unbounded retries | BE-003, BE-008 | SECURITY-LOAD |
| SEC-003 | User | Fetch only configured provider URLs; no request-controlled host or database operators | BE-003 | SECURITY-BOUNDARY |
| SEC-004 | User | Keep secrets server-side; exact CORS allowlist, sanitized errors and logs, no keys in Git | BE-008, REL-001 | SECURITY-BOUNDARY |

## API and UI behavior

The [contract](INTEGRATION_CONTRACT.md) owns endpoint/schema details. Requests are synchronous and bounded; no job queue, polling ID or fabricated progress percentage. Empty geocoding results differ from provider failure. No detected events is a successful result with zero count; insufficient data is a structured error. Partial years remain visible as null chart values and coverage warnings. Changing controls hides old results until an analysis for the new parameters succeeds.

The [dashboard brief](frontend/docs/screens.md) specifies composition and [frontend design](frontend/docs/design.md) owns visual tokens. All charts and insights derive from the same returned analysis. A geographic diagram can show sample locations without claiming spatial intensity.

## Acceptance and release

Application completion requires deterministic methodology tests, schema parity, provider-adapter and MongoDB integration tests, a real point analysis twice demonstrating cache reuse, all required UI states, nine responsive viewports, keyboard/reduced-motion/accessibility checks, dependency review, and a deployed smoke test. Each is currently pending. [Verification plan](docs/verification.md) records evidence rather than inferred passes.

Deployment recommendation: static frontend host plus one FastAPI instance and managed MongoDB; actual providers/accounts remain undecided. Validate timeouts, cold-start behavior, TLS, origin allowlists and provider usage terms before release. No deployment has been authorized or performed here.

## Risks, assumptions and dependencies

- No visual reference image was supplied; the latest written monochrome direction is binding, pixel fidelity cannot yet be evaluated.
- Baseline and UTC-day policy affect interpretation. Fixed annual thresholds emphasize absolute seasonal heat and differ from day-of-year methods.
- Sparse spatial sampling cannot establish a true heat-risk surface or administrative-area average.
- Long historical requests can exceed free-host timeouts or provider budgets; cache and chunk before considering background work.
- MongoDB credentials are supplied in an external private file; live ping failed. Deployment accounts, repository remotes and root-document versioning ownership remain unset.
- Backend dependencies are locked and lint/compile checks passed on Python 3.14.2; lifecycle/application tests remain absent. Frontend dependencies are not selected.
- The Open-Meteo free service has non-commercial use constraints. Deployment eligibility must be checked against actual use; no entitlement is assumed.
- Contract 0.2 (DOC-004, approved 2026-10-14) represents NASA POWER and ERA5 provenance truthfully; source adapters still cannot silently change frontend meanings.

## Bonus priority and submission checklist

After core acceptance: geographic map selection, CSV export, then optional PDF export or suitable significance analysis. Do not delay the core for these.

- [x] CSV export of heatwave events (implemented client-side in frontend/src/components/ResultsView.tsx).
- [ ] Public frontend/backend repository links and setup instructions (REL-001 release gate).
- [ ] Deployed app URL and a successful live analysis (REL-001 release gate).
- [x] Data source attribution, methodology, assumptions, limitations and future improvements documented.
- [x] Accurate AI-tool disclosure (documented in docs/skills-and-tools.md and docs/ai-development-workflow.md).
- [ ] Confirm submission deadline/link outside this workspace; user submits or explicitly authorizes submission.
- [ ] Optional short demo video. Never upload the private assessment brief.

