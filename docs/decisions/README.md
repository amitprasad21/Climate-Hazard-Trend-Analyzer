# Architecture and methodology decisions

Accepted means chosen for this specification, not implemented/tested. Provisional choices require implementation evidence. Record changes here with rationale/date and update the contract/method version when semantics change. Checked 2026-10-13.

| ID | Status | Decision and trade-off |
|---|---|---|
| ADR-001 | ACCEPTED | React/TypeScript frontend, Vite build proposed. Fits user direction and one-page app; exact versions await compatibility checks. No SSR/router/global store requirement. |
| ADR-002 | PROVISIONAL | Recharts for three responsive plots: React composition and modest annual datasets. Verify current API, keyboard/table fallback and package footprint before adding. Chart.js remains an alternative if evidence favors it. |
| ADR-003 | ACCEPTED | FastAPI modular monolith with pure climate functions and explicit I/O adapters. Smaller deployment/debug burden than microservices; resource limits remain essential. |
| ADR-004 | ACCEPTED | MongoDB is primary NoSQL persistence with two initial collections and unique/TTL indexes. More setup than memory/SQLite, but fulfills persistence and reusable source data requirements. |
| ADR-005 | SUPERSEDED source preference; contract unchanged | Initial ERA5-only preference is superseded by the user's no-key NASA-first direction. Both raw endpoints passed 1990–2020 probes; adapters remain pending. Source consistency remains mandatory. ADR-017 owns the necessary response/eligibility proposal. |
| ADR-006 | ACCEPTED assumption | Fixed 1991-2020 annual p95, linear interpolation, strict exceedance and 3-day minimum. Comparable across selected windows but does not model seasonal percentile variation. |
| ADR-007 | ACCEPTED assumption | Missing dates break runs; baseline/analysis coverage gates apply. No interpolation; honest exclusions may reduce apparent event frequency. |
| ADR-008 | ACCEPTED staged scope | Point/city first, then bounded 3x3 cell-center box sampling with cosine weights. No unsupported statewide polygon claim or intensity heatmap. |
| ADR-009 | ACCEPTED | Versioned cache-aside in MongoDB, expiry predicates, idempotent upserts, one-worker single-flight. Distributed coordination deferred until measured need. |
| ADR-010 | SUPERSEDED in part by ADR-025 (2026-10-15) | Descriptive OLS slope with at least 10 eligible annual counts plus trailing-five-year mean; no formal significance or causality. Avoid unnecessary statistics dependencies initially. |
| ADR-011 | ACCEPTED | v1 synchronous REST, structured errors and method metadata, no public analysis ID/jobs. Bounded 90s request deadline requires cold-path measurement. |
| ADR-012 | ACCEPTED | Deterministic unit tests + contract/adapter/real-DB integration + browser workflow evidence. Mocked tests do not prove live integration. |
| ADR-013 | PROVISIONAL | Static frontend host, one API instance, managed MongoDB. Accounts, resource cost, quotas and actual deployment target remain undecided; no deployment claim. |
| ADR-014 | ACCEPTED | Apply needed external guidance manually now. No global plugin/hook installation, OpenDesign workspace or OmniRoute service is needed for foundation work. |
| ADR-015 | SUPERSEDED by ADR-021 | Initial colored-accent direction was replaced by the supplied monochrome design on 2026-10-14. Retained as history, not current guidance. |
| ADR-016 | SUPERSEDED 2026-10-14 | The user's instruction establishes one root repository containing frontend, backend and shared documents; no nested repositories, submodules or exported document bundle. The earlier independent-repository proposal is retained only as history. |
| ADR-017 | ACCEPTED 2026-10-14 by the user | NASA POWER preferred for eligible full intervals; fixed ERA5 fallback only when free-service usage is permitted. Full-source replacement, never blended gaps. Implemented as analysis contract 0.2 (DOC-004). |
| ADR-018 | DEFERRED with trigger | Background jobs and circuit breakers are not necessary now. BE-011 measures cold deadline failures and repeated provider-outage cost; reconsider jobs after caching/chunking still cannot meet the supported request budget, and a breaker when repeat failures materially consume quota/capacity. Any job API needs a separate durable-state/contract decision. |
| ADR-019 | ACCEPTED initial constraint; scaling deferred | One backend worker initially. BE-011 identifies measured bottlenecks before replicas; REL-001 must add shared/edge rate/quota enforcement and duplicate-work coordination before scaling. No user-count promise. |
| ADR-020 | ACCEPTED local setup, verification partial | PyMongo supported async client, environment/external-file URI, one lifespan pool, no schema writes in connectivity scope. uv manages isolated backend dependencies and lock. Existing private file is never copied. BE-009 owns missing lifecycle/timeout tests and failed live ping diagnosis. |
| ADR-025 | ACCEPTED 2026-10-15 by the user; supersedes ADR-010's no-significance rule | Trend direction comes from a two-sided Mann-Kendall test (tie-corrected variance, normal approximation with continuity correction, α = 0.05) on eligible annual event counts, with Sen's slope; at least 10 eligible years. The OLS slope stays as a descriptive reference. The test assumes independent years, so a lag-1 autocorrelation check warns when significance may be overstated; a Hamed-Rao variance correction is deferred. Implemented with the standard library (no statistics dependency). Contract 0.3, method heatwave-v2. |
| ADR-024 | ACCEPTED 2026-10-15 by the user | Leaflet 1.9.4 without a React wrapper for a result map and a map picker, loaded lazily in its own chunk. Basemap: standard OpenStreetMap tiles, shown grayscale and inverted to dark with CSS, with the OpenStreetMap credit. The user first chose CARTO Dark Matter on the mistaken premise that it needed no key; on 2026-10-15 every keyless CARTO tile, including from the production domain, was an "API KEY REQUIRED" watermark, so the user chose OpenStreetMap instead. OSM's tile usage policy allows light use with the credit and a valid referrer, which fits this demo; heavier or commercial use needs another tile source. Rejected: Mapbox and Stadia (keys required), Esri Dark Gray Canvas (keyless use less clearly permitted) and a hand-built SVG locator (no place context). The map shows requested and provider-reported locations only; no intensity shading (ADR-008). |
| ADR-023 | ACCEPTED 2026-10-14 by the user | Frontend and backend deploy on separate domains. Backend CORS uses an exact origin allowlist (dev `http://127.0.0.1:5173`; production origin to be supplied before release, BE-008/REL-001). Credentials stay false; `X-Request-ID` and `Retry-After` are exposed. |

Package versions/runtime: backend lock now resolves FastAPI 0.136.3, PyMongo 4.18.3, Pydantic 2.14.1, HTTPX 0.28.1, Uvicorn 0.54.0 and local dev tools on Python 3.14.2. Lock/lint/compile checks passed; application tests and other declared Python versions remain unverified. Frontend versions are still unselected. Numerical dependencies are chosen only when the climate implementation demonstrates need; no scientific package was added for this documentation phase.

Deployment/provider entitlement, repo remotes, document-bundle workflow and exact reference-image fidelity remain open. They do not prevent this documentation phase. Scientific assumptions can be revised before implementation; after implementation they require tests and cache invalidation/versioning.

## ADR-021 Monochrome visual authority

Accepted 2026-10-14 from the supplied design/UI brief; implementation pending. frontend/docs/design.md is visual authority; root DESIGN links to it. Pure black/white/grayscale only, white Analyze trends action and non-color series/status cues. Retain the readable local system font and pure-black/opaque background until suitable local imagery exists. Use #737373 for essential input boundaries because supplied #454545 reaches only 1.97:1 on #111111. DOC-005 owns document alignment; FE-001/FE-003/FE-005 own implementation and visual acceptance. No science, API or backend change follows from this decision.

## ADR-017 reviewable contract proposal

Problem: contract 0.1 fixes source.provider=Open-Meteo, model=ERA5 and a scalar 0.25-degree resolution. NASA data cannot satisfy those meanings. NASA response geometry can echo requested coordinates and does not establish a resolved cell center. Silently accepting NASA under the old shape would falsify provenance and cache identity.

Coordinated **analysis contract 0.2**, accepted 2026-10-14 and now canonical in INTEGRATION_CONTRACT.md:

- Retain all analysis, metric, event, quality, error and method semantics. Fixed baseline/strict p95/three days/OLS remain unchanged.
- Expand the existing source object with a bounded provider identifier and truthful model/dataset identifier, plus grid latitude/longitude dimensions (NASA MERRA-2 approximately 0.5/0.625; ERA5 0.25/0.25), UTC day convention and normalization version. Validate returned NASA source metadata rather than assuming every future period has the same product.
- Permit an unknown resolved point as null with an explicit limitation; never substitute an echoed requested point as a known source-cell center. Retain requested coordinates, valid elevation metadata, retrieval timestamp and approved attribution link.
- Keep 1940 as the outer product history bound when ERA5 is eligible. Source selection must cover the full selected interval and baseline. NASA before 1981 is ineligible; no eligible source yields a controlled unsupported-period/provider-availability response. Do not misclassify an otherwise valid period as malformed user input.
- Source switching changes cache identity and recomputes the baseline from the alternate source. Same algorithm version does not imply inter-source scientific equivalence. UI shows the actual source and limitations; no additional authoritative calculation moves to the client.
- Update canonical schema, backend validation/fixtures, frontend types/shape checks and source-display tests together. Version-bump tests reject mismatched source/model/grid combinations. No running analysis consumer currently exists, so a coordinated pre-release revision is feasible.

Alternative: retain ERA5-only contract and use only ERA5 for publicly returned analysis until a later revision; NASA can remain a separately tested internal adapter. This preserves 0.1 but does not deliver NASA-first analysis. The user chose the NASA-first revision over this alternative.

## Decision ownership and maintenance

DOC-003 owns documentation consistency; DOC-004 owns source-contract resolution; DOC-002 owns the single-root repository structure; BE-002 owns scientific implementation assumptions; BE-011 owns measured operational triggers; REL-001 owns deployment eligibility. Review affected ADRs before an implementation task is DONE. Record rationale, evidence, alternatives and a successor when superseding a choice; never rewrite history to suggest an earlier probe or benchmark happened.

## ADR-022 Shared AI development roles (2026-10-14)

ACCEPTED for documentation and future task process under DOC-007; no tool installation is approved. docs/ai-development-workflow.md owns the six roles and ten stages, AI_WORKFLOW is the entry point/CI plan, and skills-and-tools owns capability/setup evidence. Select roles by risk; one session can execute sequential passes. Keep existing plans/tasks/authority documents, preserve all 85 concept IDs and link their checkpoints. Significant implementation needs a concrete approved plan; unchanged authorized work does not need repeated approval. Tool/environment changes need explicit approval and individual discovery/smoke evidence. Superpowers/Context7 remain uninstalled, gstack is experimental and lacks Bun, and manual review/design/simplification remains sufficient. Optional development tools add no production runtime dependencies.
