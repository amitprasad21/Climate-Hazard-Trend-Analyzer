# Agent memory and workspace permissions

Agents may read relevant non-secret project files, update authorized documentation/code/tests, and run appropriate reversible verification. Record durable design/contract decisions and actual evidence in memory/state/tasks, not transcripts or confidential source attachments.

Never copy credentials, connection strings, private environment contents or sensitive user data into memory or prompts. Do not overwrite unrelated work or delete important files. Do not alter remotes, repositories, history, branches, public deployment or external accounts without appropriate authorization. No automatic commits/pushes.

The [shared workflow](../../docs/ai-development-workflow.md) requires a concrete approved plan for significant implementation and explicit approval for additional tooling/environment changes. Preserve existing scope approvals; roles do not grant new privileges or authorize autonomous delegation.

Approved low-risk implementation choices follow the user request and existing project rules; no repeated permission is needed for ordinary scoped edits. Significant external tool services, hook trust and provider routing have separate boundaries in the [tool registry](../../docs/skills-and-tools.md). These policies cannot expand the environment's filesystem/tool permissions.
