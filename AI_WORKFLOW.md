# AI-assisted engineering workflow

Read [the canonical AI development workflow](docs/ai-development-workflow.md) for the six roles, ten stages, plan approvals, research/review/simplification gates and completion evidence. [Skills and tools](docs/skills-and-tools.md) owns availability and installation procedures. This entry point retains the CI plan below; it does not define a competing workflow.

## Task handoff

Identify the existing task and requirement/concept IDs, acceptance, current plan approval, affected interfaces/files and verification. Backend work names contract/method/source versions; frontend work names response states and responsive checks. Use the existing local implementation-plan/task documents. No automatic commit, push or deployment.

## Disclosure and interview readiness

Explain the concrete decisions and their evidence: percentile interpolation, missing-day boundaries, source/cache identity and stale frontend response protection. Record only tools actually used. Reading a skill, discovering a plugin and exercising its installed capability are distinct. A single session's role passes are not independent agent reviews. Delegation follows the canonical workflow and applicable authorization.

## Continuous integration plan (REL-002)

CI is planned, not configured. Use the single root repository and each application's chosen lockfile. Backend jobs install from uv.lock, run Ruff and deterministic unit/contract tests; frontend jobs use the selected package manager's frozen install, typecheck, lint, unit/contract tests and production build. Run shared documentation/concept checks against the same root revision. Browser tests produce artifacts for failed states/viewports; a human still reviews meaningful visual changes.

Pin supported runtime/tool versions and review dependency advisories without unrelated upgrades. Test a clean checkout rather than relying on local environments. Unit/fixture jobs run on pull requests without Atlas credentials. Opt-in live integration uses isolated resources and protected secrets, never fork-provided workflows; missing prerequisites are reported as unverified, not silently passed. Demonstrate that a deliberate test/contract failure blocks merge before calling CI complete.

Definition of DONE spans implementation or documentation as appropriate, required executed checks, review of affected paths, recorded evidence, current task/status/memory and no unresolved acceptance failure. Small logical changes do not imply permission to commit. No CI workflow, remote, branch policy or publishing action is created by this documentation plan.
