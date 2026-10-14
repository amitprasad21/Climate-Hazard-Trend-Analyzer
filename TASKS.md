# Project task overview

Statuses: TODO, IN_PROGRESS, BLOCKED, DONE. Repository trackers own BE/FE tasks; this file owns DOC/REL tasks and cross-repository order. Generated files alone do not complete an application milestone.

## DOC-001 Foundation and tool evaluation

Priority: P0. Status: DONE. Requirements: NFR-004. Dependencies: none.

Scope: audit, root/local instructions, PRD, architecture, method, contract, product/design, skills registry, task plans and evidence. Files: root Markdown, `.agent/`, `docs/`, frontend/backend documentation, documentation checker.

Acceptance: requested topics have one linked authority; scientific assumptions are explicit; all five tools are classified with installation boundaries; no implementation claim is fabricated; links, task references and states agree.

Verification: documentation checker and self-test passed; manual contract/method/design consistency review completed; actual Git/tool inventory recorded. Evidence: [verification record](docs/verification.md), 57 Markdown files, 28 requirements and 16 unique tasks checked. Application implementation and its tests are outside this completed documentation task.

Description: Establish the initial reviewed foundation and tools inventory.

Ownership: shared. Concepts: 1.

Required tests: Documentation checker/self-test and manual method/contract/design review.

Documents/files: Root docs, docs/skills-and-tools.md, docs/verification.md.

Blockers: None for the completed initial phase.

## DOC-002 Establish version ownership

Priority: P1. Status: DONE. Requirements: NFR-004. Dependencies: DOC-001.

Scope: one root Git repository for frontend, backend and shared documents, per the user's 2026-10-14 instruction, which supersedes ADR-016. Acceptance: the workspace root is the only repository; no nested repositories or submodules; local secrets, virtual environments and caches are ignored; only placeholder environment examples are trackable; existing history/remotes untouched; no commit/push without authorization. Files: root and backend `.gitignore`, root instructions.

Verification: `git rev-parse --show-toplevel` is the workspace root; no nested `.git` outside the ignored backend `.uv-cache` package cache; `git check-ignore` covers backend `.env`, `.venv`, `.uv-cache`; untracked-file listing shows `backend/.env.example` as the only environment file; credential-pattern scan of trackable files finds only synthetic test URIs. Evidence: [verification record](docs/verification.md), 2026-10-14. Branch `main` has no commits and no remote; publication is REL-001 scope.

Description: Keep one root history containing all application code and shared documents without changing history implicitly.

Ownership: shared. Concepts: 83.

Required tests: Git root/nesting/ignore checks and trackable-file secret scan.

Documents/files: docs/decisions/README.md (ADR-016 superseded), repository instructions.

Blockers: None. First commit and any remote require explicit user authorization.

## REL-001 Integration, deployment and submission readiness

Priority: P1. Status: TODO. Requirements: NFR-007, SEC-004. Dependencies: BE-007, BE-008, FE-003, FE-005.

Scope: real-provider/real-MongoDB end-to-end verification, dependency review, release configuration, chosen deployment and README evidence. Acceptance: repeated real analysis proves persistence/cache, live UI passes required states and viewports, setup reproducible, public code/deployed links accurate, source attribution and AI disclosure complete. Optional bbox is released only after BE-006/FE-004.

Verification: RELEASE-SMOKE, E2E-ANALYSIS, SECURITY-BOUNDARY and actual deployment checks. Evidence: none. Provider entitlement, credentials/accounts, hosting choice and publication authorization remain future release prerequisites.

Description: Verify the real application and prepare an authorized, reproducible release.

Ownership: shared. Concepts: 67, 72, 74, 79.

Required tests: RELEASE-SMOKE, E2E-ANALYSIS twice, UI-RESPONSIVE/A11Y, SECURITY-BOUNDARY.

Documents/files: Root README, docs/verification.md, local testing/security docs and chosen deployment config.

Blockers: Core application, deployment target/accounts, provider entitlement and publication authorization pending.

## DOC-003 System-design coverage and task alignment

Priority: P0. Status: DONE. Requirements: NFR-004. Dependencies: DOC-001.

Scope/files: audit all established authorities; integrate all 85 concepts; reconcile code facts, provider decisions, rules, tasks, state and documentation checks.

Acceptance: exactly one primary matrix entry for each concept 1–85; every entry maps to an authority, area, task, status and verification; every task has complete metadata and reciprocal concept links; dependencies acyclic; no false implementation claims; manual semantic review completed.

Evidence: [verification record](docs/verification.md); checker and self-tests passed for 59 Markdown files, 28 requirements, 22 tasks and all 85 concepts; reciprocal mappings/metadata/summary statuses/DAG verified; manual authority, provider/contract, methodology and implementation-state review completed. No runtime acceptance is implied.

Description: Reconcile all 85 concepts with current facts, authoritative documents and meaningful tasks.

Ownership: shared. Concepts: 1, 2, 5, 8, 82, 84.

Required tests: Checker self-test, exact concept coverage, reciprocal references, metadata/DAG and manual semantic review.

Documents/files: docs/system-design-audit.md, docs/system-design-coverage.md, scripts/check_docs.py, all affected authorities.

Blockers: None for this documentation phase. Runtime and approval gaps remain in their separate tasks.

## DOC-004 Provider provenance contract decision

Priority: P0. Status: DONE. Requirements: DATA-001, DATA-007, NFR-004. Dependencies: DOC-003.

Scope/files: review the concrete source/period proposal in the decision register; revise the canonical contract and paired frontend/backend fixtures only after approval.

Acceptance: NASA POWER and ERA5 retain honest provider/model/grid/time metadata; complete baseline and analysis use one source; 1940–1980 eligibility explicit; agreed version and compatibility policy; no deployed consumer receives unexpected semantics.

Evidence: 2026-10-14. The user approved ADR-017 (NASA-first, contract 0.2). INTEGRATION_CONTRACT.md is now 0.2: per-provider source table, `resolved` null for NASA with RESOLVED_LOCATION_UNKNOWN, 1981/1940 eligibility, compatibility note. Backend `Source` schema enforces the table; 13 tests reject mismatched provider/model/grid/attribution, NASA resolved points, non-UTC timestamps and empty samples; four mutants caught. A live NASA probe (API v2.10.0) confirmed `sources` MERRA2, UTC, °C, fill −999 and echoed geometry for 2000 and late 2025. Frontend types/fixtures are created against 0.2 in FE-002 (no consumer existed).

Description: Approve a truthful multi-provider source and historical-eligibility contract before wiring NASA results.

Ownership: shared. Concepts: 7, 8, 34, 43, 78.

Required tests: Contract proposal review, paired fixture/schema compatibility and source-label checks.

Documents/files: INTEGRATION_CONTRACT.md, docs/decisions/README.md (ADR-017).

Blockers: None.

## REL-002 Reproducible checks and continuous integration

Priority: P1. Status: TODO. Requirements: NFR-004, SEC-004. Dependencies: DOC-002, BE-001, FE-001.

Scope/files: root-repository workflows for both applications, locked clean setup, documentation/contract checks and maintained evidence.

Acceptance: backend locked install/lint/unit/contract tests and frontend locked install/type/lint/unit/build checks run in clean CI; shared-doc bundle revision validated; secret scan and dependency advisory policy applied; fork jobs get no secrets; failing regression blocks merge; browser tests have reproducible artifacts. Live tests are separate opt-in jobs with isolated resources and documented missing prerequisites.

Evidence: none; no CI files or repositories exist.

Description: Establish reproducible independent CI pipelines and shared contract/document checks.

Ownership: shared. Concepts: 63, 73, 83, 84, 85.

Required tests: CI-CLEAN, negative regression gate, secret/advisory checks and artifact review.

Documents/files: AI_WORKFLOW.md, future repository CI files, manifests/lockfiles.

Blockers: No commits, remote or frontend scripts yet; live tests must not use supplied production credentials automatically.

## Cross-repository progress and priorities

Detailed task definitions above and in [backend](backend/docs/tasks.md) / [frontend](frontend/docs/tasks.md) remain authoritative; this overview does not duplicate their acceptance lists.

| Task | Status | Current gate |
|---|---|---|
| DOC-001 | DONE | Initial foundation evidence recorded |
| DOC-003 | DONE | Concept/document checker, self-tests and semantic review passed |
| DOC-005 | DONE | Monochrome authority/rules/plans aligned; documentation/grayscale checks passed |
| DOC-006 | DONE | Official tool audit and local compatibility inventory recorded |
| DOC-007 | DONE | Roles/rules/checkpoints/traceability reviewed; documentation checks passed |
| DOC-008 | TODO | Conditional individual installation/real smoke after explicit approval |
| DOC-002 | DONE | Single root repository verified; no commits/remote authorized |
| DOC-004 | DONE | User approved ADR-017; contract 0.2 and backend Source schema tested |
| BE-001 | DONE | Strict request/error/health schemas; 80 backend tests pass |
| BE-002 | DONE | Pure heatwave-v1 engine; 27 tests, 12 rule mutants caught |
| BE-003 | DONE | NASA POWER and Open-Meteo adapters; mocked tests and live smoke |
| BE-004 | DONE | Geocoding search with bounded cache; live smoke |
| BE-005 | DONE | MongoDB repositories verified on real local MongoDB |
| BE-007 | DONE | Persisted point analysis endpoint; live E2E cold and cached |
| BE-008 | DONE | CORS, body/media limits, rate/capacity limits, safe 500s |
| BE-010 | DONE | Whole-source selector with ordered fallback |
| BE-009 | BLOCKED | 42 deterministic tests pass; live ping awaits Atlas password rotation |
| FE-001 | DONE | Vite/React/TS monochrome shell; 7 tests, build, nine-size overflow and keyboard smoke |
| FE-002 | DONE | Search, validation, request lifecycle; live browser run |
| FE-003 | DONE | Backend-driven metrics, charts, provenance and errors |
| FE-005 | IN_PROGRESS | Nine sizes measured, axe clean; screenshot review pending (pane hidden) |

All other application/release tasks are TODO. No cache, fallback selector, analysis or UI is complete. Current scope is the expressly requested AI-team workflow/document integration following the confirmed design-only update; the original connectivity/provider implementation remains unfinished and visible.

Next ordered work after this phase:

1. BE-001 is DONE. BE-009 deterministic lifecycle is verified; its live ping waits for the rotated Atlas password. The point-analysis backend (BE-002/003/004/005/007/008/010) is DONE and verified against live NASA POWER and a local MongoDB. Next: FE-002 controls and request lifecycle, FE-003 results, FE-005 acceptance, then BE-006/FE-004 boxes.
2. FE-001: establish the UI shell independently from backend science. BE-003 implements normalized no-key adapters; BE-010 adds whole-source fallback; BE-004 provides lookup.
3. Resolve DOC-004 before exposing NASA analysis; complete BE-002 pure science and BE-005 persistence in their own authorized slices. BE-007 integrates the full point path, then BE-008 hardens it.
4. FE-002 final integration depends on lookup and the agreed contract; fixture-based controls/state work need not wait. FE-003 consumes real analysis, FE-005 verifies all viewports/accessibility/performance.
5. BE-011 measures operations; DOC-002 resolves repository/document ownership and REL-002 configures actual CI. They do not authorize commits or public deployment.
6. BE-006/FE-004 add the optional bounded-region extension after the point flow. REL-001 verifies and prepares an authorized release.

Task status changes require evidence and synchronized local/project state. Concept status in the coverage matrix distinguishes documented/planned/implemented/verified/deferred/blocked and must not be inferred from task document existence.


## DOC-005 Monochrome design and implementation-brief alignment

Priority: P0. Status: DONE. Requirements: NFR-001, NFR-002, NFR-003, NFR-004. Dependencies: DOC-003.

Description: Review supplied design/UI brief, adopt grayscale-only direction and reconcile active instructions while preserving historical evidence. User explicitly requested document alignment only.

Ownership: shared. Concepts: 1, 8, 16, 17, 18, 84.

Scope/files: frontend/docs/design.md as visual authority; root DESIGN entry point; relevant root/frontend rules, PRD/product, screens, implementation/testing plan, tasks/state/memory, decision/coverage records and scripts/check_docs.py. No backend code, secret configuration or frontend scaffold changes.

Acceptance: monochrome tokens/white action replace active colored-accent guidance; one token authority; adequate planned control contrast; reference-image absence explicit; no-events distinct from insufficient data; stale-result behavior preserves API; nine responsive sizes and runtime statuses remain honest.

Required tests: Documentation checker/self-test, grayscale-token validation, opaque contrast checks, authority links, task/concept reciprocity and active-guidance search; no app/browser verification claimed.

Documents/files: [Canonical design](frontend/docs/design.md), [screens](frontend/docs/screens.md), [plan](frontend/docs/implementation-plan.md), [decisions](docs/decisions/README.md), [verification](docs/verification.md).

Evidence: [Verification record](docs/verification.md); source files inspected and active guidance/authority conflicts reconciled. Checker/self-tests passed for 59 Markdown files, 28 requirements, 23 tasks and 85 concepts. Grayscale validation and 13 opaque contrast pairs passed. No application or rendered UI acceptance is implied.

Blockers: None for documentation. No UI/reference image/local weather asset exists; rendered accessibility and viewport acceptance remain implementation tasks.

## DOC-006 AI-team tools and Codex compatibility audit

Priority: P0. Status: DONE. Requirements: NFR-004, SEC-004. Dependencies: DOC-005.

Description: Audit current skills/plugins, official setup, Codex compatibility, prerequisites, overlaps and lifecycle limitations before choosing tooling.

Ownership: shared. Concepts: 73, 84.

Scope/files: docs/skills-and-tools.md and docs/verification.md; read-only upstream/local capability inspection.

Acceptance: all six requested roles have a supported current tool or explicit manual fallback; official versus locally tested commands distinguished; installation writes, permissions, dependencies, update/removal and duplication risks documented; no environment mutation.

Required tests: Local CLI help/inventory and session-tool discovery, official source review, documentation consistency check; actual plugin smoke tests belong to DOC-008.

Documents/files: [Tool registry](docs/skills-and-tools.md), [workflow](docs/ai-development-workflow.md), [verification](docs/verification.md).

Evidence: CLI 0.162.0-alpha.17.2 and plugin/MCP/review help inspected; installed plugin/MCP/skill inventory checked; catalog lists Superpowers/Context7 as not installed; gstack upstream Codex tier experimental and Bun absent. Official Superpowers/Context7/gstack and current Ponytail/Impeccable sources read. No installation, authentication, hook trust or capability smoke run claimed.

Blockers: None for audit; runtime integration remains unverified and unnecessary for documentation.

## DOC-007 Shared AI-development workflow and checkpoint integration

Priority: P0. Status: DONE. Requirements: NFR-004, NFR-002, NFR-003, SEC-004. Dependencies: DOC-006.

Description: Integrate six role responsibilities, significant-feature planning/research/approval, review/simplification/final verification and honest task completion into the existing document system.

Ownership: shared. Concepts: 1, 4, 8, 16, 17, 18, 24, 27, 34, 39, 45, 65, 71, 76, 78, 80, 81, 82, 83, 84.

Scope/files: Canonical docs/ai-development-workflow.md; AI_WORKFLOW entry point/CI plan; root/local AGENTS and rules; local plans/testing/tasks/state/memory; concept matrix and documentation checker.

Acceptance: one workflow authority linked from instructions; all requested roles/stages and risk-based exceptions covered; explicit installation/approval boundaries; local frontend/backend checkpoints aligned; all 85 IDs retained with reciprocal tasks; all metadata/status/dependency/link checks pass; manual consistency review complete. No application milestone promoted from prose.

Required tests: Documentation checker/self-test, entry-point authority links, task/concept reciprocity and dependency/status checks, semantic review against supplied workflow and review of actual write scope; record unavailable Git/baseline comparisons.

Documents/files: [Workflow](docs/ai-development-workflow.md), [coverage](docs/system-design-coverage.md), local trackers, [verification](docs/verification.md).

Evidence: [Verification record](docs/verification.md); documentation checker/self-tests passed for 60 Markdown files, 28 requirements, 26 tasks and all 85 concepts. Thirteen authority links and ten stages checked; all nine viewport rows remain NOT RUN. Semantic review completed; existing FE/BE task definitions and the focused checker diff compared against retained pre-edit output. Full workspace baseline comparison unavailable, explicitly recorded.

Blockers: None for document work; application checks remain in their existing tasks.

## DOC-008 Individually approved tooling and capability smoke tests

Priority: P2. Status: TODO. Requirements: NFR-004, SEC-004. Dependencies: DOC-006, DOC-007.

Description: If a concrete feature benefits, prepare and obtain approval for one selected integration, install it through its supported scope and prove it on a bounded task before considering another.

Ownership: shared. Concepts: 65, 73, 84.

Scope/files: Only approved tool-owned configuration/skill paths; registry, verification and affected instruction diffs. No mandatory application dependency.

Acceptance: each selected tool has recorded approval, source/version, exact commands/working directory, prerequisites, writes/network/credential scope, overlap justification and rollback; review all installer changes; verify registration/discovery and one real role task. Record each independently. No selected tool is silently installed and no untested capability is marked verified.

Required tests: Tool-specific inventory/discovery and relevant smoke from the registry; instruction/config diff review; check unrelated setup remains intact; disable/removal procedure scoped and documented.

Documents/files: [Tool registry](docs/skills-and-tools.md), [verification](docs/verification.md), only explicitly approved configuration.

Evidence: None; no tool selected or approved for installation. Superpowers/Context7 catalog availability and upstream compatibility are audit evidence only.

Blockers: Conditional on demonstrated benefit and explicit installation approval; not a prerequisite for manual engineering or application development.
