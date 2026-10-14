# Project rule index

`AGENTS.md` is the entry point. `.agent/rules/` contains manually linked project policy; it is not an auto-discovered Codex skill directory (`.agents/skills/` is a different convention).

- [Engineering](rules/engineering.md): API, architecture, components, frontend/backend and tests.
- [Security and Git](rules/security-and-git.md): secrets, settings, input/resource boundaries, permissions and the single root repository.
- [Documentation and tasks](rules/documentation-and-tasks.md): ownership, traceability, memory and completion rules.

The [shared AI workflow](../docs/ai-development-workflow.md) owns the six development roles and their stage/approval gates; these rules add project constraints.

Detailed domain decisions belong in the linked canonical documents, not duplicated policy files. Frontend/backend rule indexes add only local constraints.
