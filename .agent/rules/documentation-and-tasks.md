# Documentation and task rules

[docs/ai-development-workflow.md](../../docs/ai-development-workflow.md) owns roles, stages, approval and completion gates; root AI_WORKFLOW is its entry point and CI plan. The tool registry owns installation/availability. Keep plans and research/review evidence in existing local plans/tasks, decisions or verification records, not separate tool-specific task systems.

Root PRD owns requirements; root contract owns wire semantics; backend methodology owns calculations; [frontend/docs/design.md](../../frontend/docs/design.md) owns visual tokens; root DESIGN is its entry point. Link to those authorities instead of copying them. Local architecture/design/API documents explain repository-specific implications.

Each task has a unique ID/title, description, requirement IDs, concept IDs, ownership, priority, status, dependencies, scope/files, acceptance criteria, required tests, documentation links/files, evidence and named blockers. [Coverage](../../docs/system-design-coverage.md) has exactly one row per concept 1–85 and reciprocal task links. Allowed states: TODO, IN_PROGRESS, BLOCKED, DONE. Dependencies are completion/integration gates; independent fixture/design work may proceed when explicitly noted. Do not expose a dependent feature before its prerequisites pass. BLOCKED names the concrete prerequisite and next action; DONE requires all applicable acceptance, executed checks, review and documentation. For a documentation task this means checked and reviewed documentation, not runtime completion.

Use [TASKS.md](../../TASKS.md) for the cross-repository order and local trackers for actual component tasks. After material changes update local state, tasks and memory; update PROJECT_STATE for cross-repository milestones. Memory stores durable facts, never secrets or conversation transcripts.

Verify relative links and task/requirement references. Distinguish proposed commands from available scripts and planned features from completed behavior. Documentation-only changes need link/content checks, not invented application test results. Record manual review limitations explicitly.
