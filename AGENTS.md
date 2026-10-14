# Climate Hazard Trend Analyzer

Read [PRD](PRD.md), [architecture](ARCHITECTURE.md), [project state](PROJECT_STATE.md), [API contract](INTEGRATION_CONTRACT.md), and the affected repository's `AGENTS.md` before editing. Read [global rules](.agent/README.md) and the relevant local rules. Product/design context lives in [PRODUCT.md](PRODUCT.md) and [DESIGN.md](DESIGN.md).

- This workspace began empty. Read current PROJECT_STATE before assuming completion: backend connectivity/health code is partial; analysis, persistence and frontend remain unimplemented. The 85-concept documentation pass is complete; follow the current user request and selected task scope rather than treating prior phase boundaries as permanent.
- Consult [system-design coverage](docs/system-design-coverage.md), the owning task/concept IDs and acceptance criteria before edits. Preserve a single authority per subject; no planned concept becomes implemented merely through prose.
- Follow [the shared AI development workflow](docs/ai-development-workflow.md): plan, research, architecture review, applicable approval, build, verify, review, simplify, final verification and documentation. Select the needed roles; do not launch six agents mechanically.
- Inspect root `git status` before changes. The latest user instruction establishes one root Git repository containing frontend, backend and shared documents; no nested repositories. Do not commit, push, change remotes, rewrite history or destructively clean without explicit authorization.
- Protect unrelated work, credentials, and the confidential assessment brief. Never copy the brief or its screenshots into public deliverables.
- Backend owns climate calculations. Never invent climate findings, spatial heatmaps, significance, or verification evidence.
- Follow the [canonical frontend design](frontend/docs/design.md): pure black, white and grayscale only. The latest supplied design supersedes the prior colored-accent direction. Follow the responsive test matrix; record which checks actually ran.
- Use [skills and tools](docs/skills-and-tools.md) to select guidance. Do not install duplicate skills, auto-trust hooks, launch gateways, or run autonomous build/ship workflows.
- Canonical task trackers are [TASKS.md](TASKS.md), [frontend tasks](frontend/docs/tasks.md), and [backend tasks](backend/docs/tasks.md). Use TODO, IN_PROGRESS, BLOCKED, DONE; DONE requires evidence.
- Significant implementation requires a concrete reviewed plan and authorized scope. The latest master prompt authorizes incremental application implementation through its seven milestones; reuse that authorization without repeatedly requesting approval. Tool installations/environment changes require explicit approval under the shared workflow; unresolved architecture, credentials and destructive actions retain their gates.
- Finish with actual changes/checks, remaining risks, and the next task. Never claim production readiness from generated files.
