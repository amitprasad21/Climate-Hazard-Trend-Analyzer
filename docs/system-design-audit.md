# System-design alignment audit

Reviewed 2026-10-14 after the connectivity/provider request and before the 85-concept documentation pass. This is that phase's audit; the subsequent monochrome update is recorded in DOC-005 / ADR-021 and the current frontend design. Earlier palette/authority findings below are historical. The checklist is the 85 numbered concepts in the user's supplied master prompt; no separate checklist file was supplied. This pass changes documentation, rules, task traceability and its checker, not business features.

## Inventory and authority

All 57 existing project Markdown files, root checker, backend manifest/lock and four Python modules were inventoried. Relevant content was reviewed across root, `.agent/`, frontend and backend; dependency caches and the virtual environment are generated artifacts, not project documentation. Secret files were inspected only through presence/configuration checks, never dumped. The existing private file remains outside the workspace; local `.env` holds its path and non-secret flags only.

| Area | Finding | Disposition and authority |
|---|---|---|
| Root PRD / PRODUCT | Useful scope, 28 requirement IDs and provenance; old provider and setup assumptions | Preserve IDs; update DATA-001 and factual gaps; PRD owns requirements, PRODUCT owns user/product context |
| Root ARCHITECTURE | Sound modular boundaries and flow; source choice and completion state outdated | Link to local designs; distinguish runtime drafts from planned analysis; architecture remains canonical |
| INTEGRATION_CONTRACT / backend API | Single schema authority already present; all-endpoints-planned claim stale; provider literal conflicts with NASA preference | Record drafted health/readiness; leave analysis 0.1 unchanged; DOC-004 prepares a coordinated proposal before implementation |
| Frontend system/state/screens | Useful component tree, request cancellation and screen states | Keep paths; deepen concepts 9–21 and test gates; system.frontend owns components/state consumption, state owns lifecycle transitions |
| DESIGN / frontend design/responsiveness | Black/gold tokens and nine viewport plan remain accurate | Preserve tokens and visual direction; no UI or visual evidence exists |
| Backend system/pipeline/security | Good separation/cache intent; lacks complete fallback, monitoring, operational policies; old API-key option contradicts no-key requirement | Revise in place; system.backend owns boundaries, pipeline owns providers/cache orchestration, security owns settings/operations |
| Database / methodology | Proposed collections/indexes and detailed science are useful; no schema is deployed | Preserve proposed model and scientific rules; add connectivity facts and provenance/fallback impact, without migrations |
| Agent rules | Concise but no 85-concept traceability requirement | Add links and completion gates, not copied definitions |
| Tasks/plans | 16 meaningful task IDs; lack explicit ownership/concept IDs/blockers and operations/CI scope | Preserve IDs, add six cohesive tasks; keep statuses tied to evidence |
| README/state/memory | Documentation-only statements now inaccurate for backend | Replace current snapshots; preserve dated historical evidence separately |
| Decisions | Compact decision register; several runtime/provider choices need revision | Keep register rather than invent 85 ADR files; add decision owners/triggers and review evidence |
| Tool registry | Five upstream repositories already classified; no new tool installation needed | Retain registry; distinguish installed app dependencies from optional skills |
| Git/deployment | Root/frontend/backend `git status` report no repository; no CI or deployment files | No histories/remotes modified; DOC-002 / REL-002 / REL-001 own missing work |

New documents needed: this audit and [system-design coverage](system-design-coverage.md). All other content belongs in established documents. No project documents were retired or moved. No duplicate lowercase architecture file was found on this Windows workspace.

## Current facts versus proposals

Existing code: `backend/app/settings.py`, `database.py`, `main.py`, package marker; manifest, `uv.lock`, isolated `.venv`, ignored local environment and placeholder template. The code drafts validated settings, one PyMongo async client per lifespan, startup ping/close, DB dependency, liveness and readiness. It has no automated application tests. Import/format/lint checks cannot establish lifecycle or security acceptance. BE-001 and BE-009 remain IN_PROGRESS.

Real, credential-free public probes for a Delhi point returned 11,323 daily maxima for 1990-01-01 through 2020-12-31 from each candidate. These checks inspected units, timezone, date bounds, count, missing values and plausibility. They were exploratory HTTP probes, not tests of an implemented adapter or complete climate methodology. BE-003 / BE-010 remain TODO. No provider module, persistence repository, cache, climate engine or dashboard exists.

The Atlas ping using the provided file failed with the safe category `network_or_availability`; client closure completed. The restricted-network attempt stalled in resolution and was stopped. No successful live connectivity, permission-to-write, collection or index check is claimed. Timeout behavior including DNS is a specific BE-009 regression requirement. No broad Atlas allowlist change was made.

## Conflicts and unresolved decisions

1. **Source metadata:** analysis contract 0.1 hardcodes ERA5/0.25 degrees; NASA uses a different source and grid. DOC-004 is BLOCKED on approval of a concrete compatible source-metadata/period policy. Document the proposal now; do not emit NASA data labeled ERA5.
2. **Historical eligibility:** NASA daily UTC begins in 1981, while ERA5 supports 1940. Validate user inputs once, then select a source covering the complete baseline and requested interval. Periods before 1981 need an eligible ERA5 source or a controlled unsupported-period result.
3. **Fallback/persistence gap:** there is no existing storage/cache/engine implementation to wire. BE-003 / BE-010 can implement adapters; BE-005 / BE-007 own eventual persistence and analysis. Do not invent success cache tests without these modules.
4. **Free access:** local assessment configuration marks Open-Meteo usage non-commercial. This is not entitlement for an unknown deployment. REL-001 must verify actual use and quotas; disable fallback if unsuitable.
5. **Operations:** no measured latency/load, production host, repository remotes, CI secrets or release authorization. Targets are plans; no user-count or production-readiness claims.
6. **Design:** no approved screenshot file is available. Written tokens/layout remain authoritative; visual similarity cannot be verified.

## Consistency review

The coverage matrix maps each concept to one primary authority, implementation area, task and verification activity. Trackers preserve requirements and meaningful dependency gates. The checker enforces exact concept IDs, task metadata, reciprocal concept mappings, references and dependency cycles; manual review covers semantics, boundaries and truthful status. [Verification](verification.md) records the executed commands and limits.
