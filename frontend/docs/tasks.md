# Frontend task tracker

All source paths are proposed. [Root PRD](../../PRD.md) owns requirements; [testing](testing.md) owns case definitions.

## FE-001 Runnable monochrome foundation

Priority: P0. Status: DONE. Requirements: NFR-001, NFR-004. Dependencies: DOC-001.

Scope/files: package/lock/config, minimal page, tokens/styles, smoke test. Acceptance: supported React/TypeScript/Vite scaffold, semantic heading/form shell, canonical grayscale tokens and white Analyze trends action, safe API-boundary placeholder without fabricated results, exact verified run/type/lint/test/build commands. No fabricated metrics. Verify UI-DESIGN and initial keyboard/narrow layout smoke. Evidence: 2026-10-14. User approved Vite + React + TypeScript via npm. Exact pins, each published before 2026-09-30, installed with `npm install --before=… --ignore-scripts`: React 19.3.0, Vite 8.3.1, plugin-react 6.1.1, TypeScript 6.0.3 (typescript-eslint supports <6.1), Vitest 5.0.2, jsdom 29.1.1 (30.x needs Node ≥24.15; local is 24.12), Testing Library 16.3.3, ESLint 10.11.0. `npm audit` flagged source-map-js 1.2.1 (GHSA-68fv-2mgg-jv7q); an override to 1.2.2 changed one lock entry and audit now reports 0 vulnerabilities. src/ has the token sheet, global styles, semantic DashboardPage and an honest not-connected submit notice; no fetch and no figures. 7 Vitest cases include tokens identical to design.md, grayscale only and no colour literals outside tokens.css; 6 of 6 mutants caught. `npm test`, `npm run typecheck`, `npm run lint` and `npm run build` pass (JS 69.6 kB gzip). Browser pane on the Vite dev server: no console errors; idle shell has no page overflow and no element outside the viewport at all nine design sizes; controls ≥44 px; content capped at 1600 px at 1920. Real Tab presses follow reading order with a 2 px white focus-visible outline, and Enter shows the notice with zero /api requests.

Description: Establish the runnable semantic monochrome shell using one supported frontend stack.

Ownership: frontend. Concepts: 4, 9, 10, 16, 21, 73.

Required tests: UI-DESIGN, keyboard/narrow smoke, exact type/lint/unit/build commands.

Documents/files: package.json, package-lock.json, vite.config.ts, tsconfig.json, eslint.config.js, index.html, src/, tests/; docs/design.md and system.frontend.md.

Blockers: None. Not covered: a visual reference image was never supplied, and the 320 px screenshot was cropped by the capture (DPR 2 against a 480 px frame), although measured layout fit. Full state/zoom/contrast checks belong to FE-005.

## FE-002 Accessible controls and request lifecycle

Priority: P0. Status: TODO. Requirements: FR-001, FR-002, FR-003, FR-008, NFR-006. Dependencies: FE-001, BE-004.

Scope/files: controls, request hook, API client/types, interaction tests. Acceptance: Heatwave default, usable location/year selection, clear validation, actual progress/error/idle states and duplicate protection; parameter edits ignore stale results and errors. Verify UI-LIFECYCLE/CONTRACT-INPUT and E2E-LOCATION. Synthetic responses are test-only. Evidence: none.

Description: Build accessible selection and a stale-safe request lifecycle with one API boundary.

Ownership: frontend. Concepts: 7, 12, 13, 14, 15, 17, 20, 21, 66, 76, 78, 80.

Required tests: UI-LIFECYCLE, CONTRACT-INPUT/OUTPUT, E2E-LOCATION; late success/error and unmount.

Documents/files: Planned controls/useAnalysis/api client/types; docs/state.md/system.frontend.md.

Blockers: Final live lookup and approved source schema required for integration; interaction tests can proceed independently.

## FE-003 Backend-driven result presentation

Priority: P0. Status: TODO. Requirements: FR-005, FR-006, FR-007, FR-008, FR-009, DATA-007. Dependencies: FE-002, BE-007, BE-008.

Scope/files: metric/charts/insights/region-context presentation, result tests. Acceptance: all four metrics and three plots use backend data; source/method/period/coverage are explicit; null/zero/partial/no-event states differ; keyboard/table chart details and valid geography alternative work. Verify UI-METRICS/CHARTS/GEOGRAPHY and real E2E-ANALYSIS. Evidence: none.

Description: Render one returned analysis consistently as metrics, charts, insights and valid geography.

Ownership: frontend. Concepts: 9, 10, 11, 17, 18, 20, 21, 51, 54, 64, 79.

Required tests: UI-METRICS/CHARTS/GEOGRAPHY, partial/error/no-events and real E2E-ANALYSIS.

Documents/files: Planned result components; docs/screens.md/system.frontend.md and root contract.

Blockers: Real persisted backend and hardened errors pending.

## FE-004 Bounded-area selection

Priority: P2. Status: TODO. Requirements: FR-010, FR-009. Dependencies: FE-003, BE-006.

Scope/files: region controls/context, request types only if changed, interaction tests. Acceptance: explicit coordinate-box limits, clear unsupported error, actual sample points and resolution disclosure; no fake heatmap. Reuse numeric/native inputs; add map library only with a justified task. Verify CLIMATE-SPATIAL contract cases and UI-GEOGRAPHY. Evidence: none.

Description: Add constrained area controls and disclose sampled spatial approximation.

Ownership: frontend. Concepts: 58.

Required tests: CLIMATE-SPATIAL contract cases, UI-GEOGRAPHY and keyboard/narrow controls.

Documents/files: Planned bbox controls/context; docs/screens.md and root contract.

Blockers: Bounded backend sampler must pass before exposure.

## FE-005 Responsive and accessible completion

Priority: P0. Status: TODO. Requirements: NFR-002, NFR-003, FR-008. Dependencies: FE-003.

Scope/files: focused layout/chart fixes, browser tests and evidence docs. Acceptance: all nine widths without page overflow, long/missing/large data and every UI state tested, focus/keyboard/reduced motion/zoom and automated accessibility checks plus manual review. Verify UI-RESPONSIVE/A11Y; fix findings and record browser/screenshots actually reviewed; report production compressed bundle size and measured cold/warm interaction cost, optimizing only demonstrated bottlenecks. Evidence: none.

Description: Verify responsive/accessibility/performance acceptance across actual browser states.

Ownership: frontend. Concepts: 16, 17, 19, 21, 71, 81.

Required tests: UI-RESPONSIVE/A11Y at all nine sizes; bundle report and interaction profiling.

Documents/files: Layout/chart fixes and browser evidence; docs/responsiveness.md/testing.md.

Blockers: Dashboard absent; no viewport or browser audit has run.


## Shared workflow checkpoints

[The canonical workflow](../../docs/ai-development-workflow.md) owns the six roles and stage gates. Shared DOC-006 audits tools/compatibility, DOC-007 integrates rules/traceability/checkpoints, and conditional DOC-008 owns individual approved installation plus smoke testing; their definitions remain in root TASKS.

For each significant FE task, expand its slice in [implementation plan](implementation-plan.md), record approval and official research for the chosen package versions, then verify/review/simplify/recheck against its existing acceptance. FE-001 uses UI-DESIGN and initial narrow/keyboard smoke; FE-002 adds request/contract race tests; FE-003 validates backend result meanings and accessible chart alternatives; FE-005 owns all nine real viewport, accessibility and performance evidence. Impeccable/manual review must follow [design](design.md). Record findings, fixes and skipped prerequisites in task evidence; none of these instructions complete FE work.
