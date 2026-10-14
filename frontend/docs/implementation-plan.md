# Frontend implementation sequence

[Tasks](tasks.md) owns completion. FE-001 shell is DONE; FE-002 onward is pending. Before significant implementation, follow [the shared workflow](../../docs/ai-development-workflow.md): add a concrete slice plan here with package-version research, files/interfaces, edge cases, tests and approval status. Existing milestones specify order, not approval to build every feature. Apply UI review before extensive markup and review/simplification/final verification after the slice.

| Milestone | Tasks / prerequisites | Verification gate / risk |
|---|---|---|
| Minimal shell | FE-001 after DOC-001, independent of unfinished backend | Verified scripts, token use, semantic shell; do not imply working analysis |
| User input | FE-002 after shell; lookup/contract are final integration gates | Accessible controls and stale-response/error tests; narrow form usability |
| Complete point dashboard | FE-003 after real analysis/hardening | Real source results, null/zero states, accessible charts, no duplicate calculations |
| Responsive acceptance | FE-005 after result view | Nine sizes and actual keyboard/zoom/reduced-motion/automated audit evidence |
| Regional extension | FE-004 after bounded backend sampler | Honest geographic approximation and invalid-box behavior |

Choose the smallest adequate chart dependency during implementation and pin it; no chart/UI/state package has been installed (FE-001 added only React, Vite and test/lint tooling). Inspect an actual reference image if later supplied. Complete frontend/backend point integration before bonus map/export features. Shared-wire changes update both sides before release.

## Supplied monochrome implementation brief

The 2026-10-14 design/UI brief is reconciled into [design](design.md), screens, state and existing tasks; user confirmed document alignment only. Its implementation phases are future work, not executed commands.

| Brief phase | Existing task / authority | Implementation gate |
|---|---|---|
| Inspect | DOC-005; instructions/state | No frontend code/dependencies to reuse yet; keep Git boundaries |
| Centralize tokens | FE-001; design.md | Grayscale tokens, white action/focus, accessible borders; no new font/image dependency required |
| Compose dashboard | FE-001 shell, FE-003 results; screens/system.frontend | Header/form/metrics/frequency/supporting charts/insights; spatial intensity only with valid data |
| Interactions | FE-002, FE-003; state/contract | Real requests, safe errors, stale-response rejection; zero events distinct from insufficient data; no stale-result API extension |
| Responsive review | FE-005; responsiveness/testing | Nine sizes, long/missing/error states, keyboard, contrast and reduced motion actually checked |
| Test/review | Owning FE task | Inspect real scripts, execute checks, review affected callers/diff |
| Evidence | Owning FE task / verification | Record actual results and honest task/state/memory |

Primary series is white/solid/marked; comparison is gray/dashed/labeled. Render backend arrays without interpolation or scientific recalculation. Begin with opaque panels and pure black; no licensed local storm asset exists. Imagery/translucency requires later rendered contrast evidence. No FE task is completed by this document update.
