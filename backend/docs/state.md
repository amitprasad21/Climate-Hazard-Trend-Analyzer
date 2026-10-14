# Backend state

Reviewed 2026-10-14. **Connectivity, configuration and request/error schemas with passing deterministic tests; analysis features absent.** BE-001 is DONE; BE-009 is BLOCKED only on the live Atlas ping.

Present: app/settings.py, database.py, main.py, schemas.py and package marker; pyproject.toml, uv.lock, isolated .venv, .gitignore and placeholder .env.example. Local .env references the original credential file without copying secrets. Code drafts a PyMongo async lifespan pool, ping/close, dependency handle, safe liveness/readiness and environment validation. tests/ holds 142 passing deterministic cases for settings, lifecycle, health, request/error/source contract and provider adapters (2026-10-14).

Actual checks: locked install succeeded; Ruff, compileall and offline lock-consistency passed on Python 3.14.2. Both public weather endpoints passed basic no-key 1990–2020 probes (11,323 days each); these were direct HTTP probes, not implemented adapter tests. Atlas ping failed with network_or_availability; closure completed. Restricted DNS probe stalled and was stopped. No successful live DB/health endpoint, storage read/write or cache integration is claimed.

Absent: provider selector, the full AnalysisResponse schema (BE-007), analysis/search routes, repositories, indexes/collections, climate engine, analysis/lookup routes, telemetry, CI and deployment. No frontend application exists. The backend belongs to the single root repository; no commits or remote exist.

The 85-concept documentation/architecture pass DOC-003 is DONE with checker/self-test and manual-review evidence. DOC-004 is DONE: the user approved contract 0.2 and the backend `Source` schema enforces it. Method heatwave-v1 remains the documented fixed-baseline/quality/run/trend design.

DOC-007 aligns [the shared workflow](../../docs/ai-development-workflow.md) with backend planning, version research, risky-logic TDD, broader review, safe simplification and final checks. This documentation-only update does not change code, manifest/lock, environment, method or contract. No new plugin/service installed; conditional DOC-008 does not block manual engineering.

Present since 2026-10-14: app/ingestion.py and app/providers/ (BE-003 DONE, live smoke recorded). Next implementation: BE-010 whole-source selector and BE-002 pure science. BE-009's live ping runs after the Atlas password is rotated. Schema writes are outside the prior connectivity scope and require the later persistence task. See [tasks](tasks.md), [testing](testing.md), [coverage](../../docs/system-design-coverage.md) and [evidence](../../docs/verification.md).
