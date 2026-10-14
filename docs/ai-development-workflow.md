# AI development workflow

Authority: this document owns development roles, stage gates and completion evidence. [AI_WORKFLOW](../AI_WORKFLOW.md) is the entry point and retains the CI plan. [Skills and tools](skills-and-tools.md) owns installation, availability and supported commands; it is not a second workflow. Reviewed 2026-10-14 under DOC-006 and DOC-007. Documentation is complete; optional tool activation (DOC-008) and application tasks remain separate.

## Scope and working model

Use six responsibilities as deliberate passes within the current task. A single Codex session can perform them sequentially; this is not six installed agents or permission to launch autonomous workers. Use subagents only when explicitly authorized by the user or applicable instructions; assign bounded ownership and integrate their results. Do not describe self-review as independent review.

Read root/local AGENTS, PRDs, architecture, state, task, contract and relevant rules first. Inspect Git separately in frontend and backend. Neither directory currently has a repository; use scoped file comparisons until Git exists. Preserve separate histories and unrelated work. Plans belong in the existing local implementation-plan/task documents or decision register, not a parallel tool-specific task system.

## Roles and outputs

| Role | Preferred capability / current fallback | Inputs and required output |
|---|---|---|
| Planner | Superpowers planning guidance; plugin not installed | PRD, existing code, task and edge cases → a small ordered plan identifying files, interfaces, dependencies, acceptance, risks, tests and approval status |
| Researcher | Context7 when connected; official documentation through available web tools now | Installed/intended package version and a precise API question → official source, version applicability, findings and unresolved compatibility limits |
| Reviewer | Codex native review when applicable; direct file/caller review now | Plan, change, callers, tests and contract → prioritized findings with impact, location, fix and verification, including gaps beyond the immediate diff |
| Cleaner | Ponytail principles applied manually; plugin not installed | Reviewed behavior and existing alternatives → smallest adequate implementation with safeguards and tests preserved |
| Product/engineering lead | Selective gstack capability if approved and compatible; manual scope/architecture/release review now | Requirements, boundaries and evidence → justified scope, decisions, trade-offs and readiness gaps; no speculative infrastructure |
| UI/UX specialist | Impeccable guidance applied manually; skill not installed | Product context, canonical frontend design, screens and real states → coherent hierarchy, responsive behavior, accessible interaction and actual visual findings when UI exists |

The [registry](skills-and-tools.md) distinguishes installed, discoverable, documentation-inspected and smoke-tested. Current plugin catalog availability is not installation. Codex review help is verified; no native review run against this project is claimed. Existing browser tooling does not establish a passing UI audit.

## Ten-stage feature workflow

| Stage | Work and exit evidence |
|---|---|
| 1. Plan | Specify the behavior and important edge cases; trace callers and relevant concept IDs; choose one complete slice and update its existing plan/task. Include testable acceptance, likely files, dependencies, rollback approach and known decisions. |
| 2. Research | Inspect manifests/lockfiles and actual installed versions before unfamiliar or version-sensitive APIs. Query Context7 only when available and useful; verify official source/version coverage. Otherwise read official docs directly. Record sources and limitations; a search snippet or a generic latest example is insufficient. |
| 3. Architecture review | Check frontend/backend responsibilities, contract/method/cache versions, security, data integrity and relevant concepts. Select product, engineering or UI review as needed. Reuse established components/platform features/dependencies before adding any. |
| 4. Approval | Present a concrete plan for significant implementation or unresolved decisions and wait for approval of that scope. Record existing approval when it already covers the plan; do not ask again for unchanged authorized work. Apply the installation and external-action boundaries below. |
| 5. Build | Implement one task/slice. For risky logic, run a focused failing test that expresses the expected behavior, implement minimally, then make it pass. Do not generate an entire unfinished application. |
| 6. Verify | Inspect available scripts and run checks appropriate to the change. Distinguish unit/fixture tests, contract tests, real integration and browser evidence. Fix failures or retain an explicit incomplete status. |
| 7. Review | Review correctness, regressions, security, data integrity, contract compatibility, errors, tests, performance, accessibility, responsiveness and unrelated scope. Inspect affected callers/configuration beyond the diff. Fix critical/high findings before completion; record remaining findings and their impact. |
| 8. Simplify | Remove unnecessary duplication or abstraction only where behavior remains clear and equivalent. Preserve validation, resource limits, provider fallback, scientific checks, error handling, accessibility and tests. No cleanup merely for style. |
| 9. Final verification | Re-run checks affected by simplification/fixes, inspect final diff or scoped file comparison, and evaluate acceptance. Do not repeat costly checks without a relevant change or unresolved concern. |
| 10. Document and track | Update the owning task, local state/memory and changed authorities; update shared state/decisions/coverage as needed. Record actual commands/results, limitations, review disposition and next work. DONE requires the task's evidence, not an instruction file or generated test. |

Use the full sequence for a new feature, changed scientific/contract meaning, shared dependency, substantial refactor or security-sensitive change. For a small known fix, combine planning/research/architecture into a short scoped assessment; retain appropriate tests, review and evidence. For prose-only work, documentation checks and semantic review suffice. Explain material skipped stages; never fabricate TDD, an independent review or a browser run.

## Approval and execution boundaries

A significant plan identifies the selected task/requirements, affected frontend/backend interfaces, acceptance and edge cases, ordered slices, exact verification approach, dependencies, risks and rollback. Present it in its existing authoritative plan document. Approval is a recorded human decision, not an elapsed timer or the existence of a TODO task. This document update was expressly requested and needs no extra implementation approval. Future significant code work follows the gate above.

Tool installation, authentication, hook trust, upgrades that change the environment and additional services require explicit approval under the latest user requirement. Before requesting it, prepare the exact version/source, working directory, commands, prerequisites, files/settings written, network/data access, overlap analysis, smoke test and rollback. Install one selected integration at a time only after approval. Review installer changes to instructions/configuration; discover the capability in a fresh session and exercise a small relevant task before calling it verified. An installer exit code alone is insufficient.

Do not run auto-build/ship, commits/pushes, destructive cleanup, repository/remotes/history changes, public listeners, cross-provider source uploads or deployment without applicable authorization. Never copy credentials into plans, prompts, logs or tool configuration. Context7 research queries should contain public library/API questions, not private source or secrets. Do not disable sandbox, TLS or security controls to make a tool work. Keep optional gstack/OpenDesign/OmniRoute outside application dependencies; OmniRoute has no current requirement.

Before substantial refactoring, inspect the correct working tree and preserve the pre-change files and unrelated work through an approved scoped snapshot or existing Git baseline. No automatic stash/reset/commit. With no Git repository, record a file-comparison baseline and restore only task-owned changes if needed.

## Research and review records

Use a short entry in the owning task's Evidence or existing decision/verification document: package/tool and installed version; precise question; official URL and date; compatibility finding; chosen API and affected files; test that will verify it. Context7 does not guarantee that every library version is indexed. If exact-version coverage is absent, use official tagged docs/source or report the unresolved assumption. Do not add React/chart packages merely to make a research result available.

Review findings should state severity, file/location, triggering condition, user/data impact, proposed fix and checking method. P0/critical and P1/high findings block completion. Resolve lower-priority findings in scope or name a follow-up and explain the residual risk. Security review is not a certification; unavailable scanners or real integration checks remain visible.

The Cleaner searches in order: existing project implementation, suitable platform/standard-library feature, installed dependency, then minimal new code. Keep tests that protect edge cases. If no simplification is warranted, record that rather than manufacturing a refactor. Review and simplification are responsibilities, not slash commands assumed to exist.

## Frontend application of the workflow

FE-001 plans the semantic shell and researches the chosen React/TypeScript/Vite versions before installation. FE-002 reviews the request lifecycle and approved contract; FE-003 preserves backend values, nulls, provenance and honest geography. FE-005 owns completed responsive/accessibility/performance evidence. All remain TODO; this workflow does not start the scaffold.

The UI specialist reads [PRODUCT](../PRODUCT.md), [canonical design](../frontend/docs/design.md) and [screens](../frontend/docs/screens.md). Preserve pure black, white primary text/action, #888888 secondary labels, near-black surfaces and grayscale charts/statuses. Any future color exception needs explicit approval and a documented reason; no exception is approved now. Storm-cloud atmosphere is subordinate to results; no actual reference image/local licensed asset exists, so use the documented pure-black/opaque fallback. Do not invent or fetch decorative assets automatically.

Use the existing [responsive matrix](../frontend/docs/responsiveness.md) as the sole viewport result log and [testing plan](../frontend/docs/testing.md) for states and accessibility. Check all nine sizes with real layout/overflow and visual review where supported. Check long labels/errors, large/null metrics, chart labels/tooltips/legends, keyboard/focus/touch, 200% zoom and reduced motion. Tool/static token checks complement manual rendered inspection. Missing browser prerequisites keep responsive acceptance open; report exact sizes and states actually tested.

## Backend application of the workflow

BE-009 first needs a bounded connectivity/lifecycle plan and version-specific PyMongo/FastAPI research; preserve its no-schema-write boundary. BE-001 needs strict schemas/contract tests. Research actual locked Python, FastAPI, Pydantic, PyMongo and HTTPX versions; verify Atlas/provider behavior against official sources when changing those boundaries.

Use TDD for climate thresholds/runs/calendar/quality boundaries (BE-002), validation/normalization (BE-001/BE-003), whole-source fallback (BE-010), and expiry/keys/concurrency/partial-write recovery (BE-005/BE-007). Test independent expected outcomes, not copied implementation formulas. Pure unit tests use no live I/O; separately prove real provider/database behavior with authorized isolated resources. Failure tests cover elapsed deadlines, cancellation, safe errors, exhausted sources and prevention of false cached success.

Review [methodology](../backend/docs/climate-methodology.md), [pipeline](../backend/docs/data-pipeline.md), [database](../backend/docs/database.md) and [security](../backend/docs/security.md) at their affected boundaries. Contract 0.2 (DOC-004) defines the NASA/ERA5 source metadata; this workflow changes neither the analysis contract nor heatwave-v1. Broader architecture review precedes the core pipeline; security and release readiness review precede REL-001. No plugin is a weather provider or runtime backend.

## Traceability and completion

[Coverage](system-design-coverage.md) retains all 85 original IDs/names. Planning links requirements/decisions (1/8), architecture review separation (4), research versioning (34), test-first work validation/engine/cache/fallback (24/27/39/45), review secrets/performance/tests (65/71/76/78/80), UI review responsiveness/accessibility/visualization (16/17/18/81), and completion task traceability/small changes/docs (82/83/84). Runtime status stays with its existing owning task.

DOC-006 records the tool/compatibility audit. DOC-007 owns this workflow, rule/checkpoint integration, concept mapping and consistency review. DOC-008 is conditional individual installation plus smoke testing; it remains TODO with no selected/approved installation. Local trackers reference these shared tasks and add repository-specific evidence gates to their existing implementation tasks rather than duplicating tool tasks.

Completion evidence must name what changed and why, actual checks and failures, review findings resolved or outstanding, simplification impact, approvals still pending, and the next task. No test suite, UI or production readiness is implied by completing DOC-007. CI execution remains separately planned under REL-002 in [AI_WORKFLOW](../AI_WORKFLOW.md).
