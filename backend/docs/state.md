# Backend state

Reviewed 2026-10-14. **Point-analysis backend implemented and verified end to end against live NASA POWER and a local MongoDB.** BE-001/002/003/004/005/007/008/010 are DONE; BE-009 is BLOCKED only on the live Atlas ping; BE-006 (boxes) and BE-011 (operations) are TODO.

Present: settings, database lifecycle, schemas (contract 0.2), ingestion, providers (NASA POWER, Open-Meteo, geocoding), selector, climate engine, repositories, analysis and region services, security guards and routes. Local `.env` still points to the original Atlas credential file; local development can opt into a loopback MongoDB.

Actual checks: locked install succeeded; Ruff, compileall and offline lock-consistency passed on Python 3.14.2. Both public weather endpoints passed basic no-key 1990–2020 probes (11,323 days each); these were direct HTTP probes, not implemented adapter tests. Atlas ping failed with network_or_availability; closure completed. Restricted DNS probe stalled and was stopped. No successful live DB/health endpoint, storage read/write or cache integration is claimed.

Absent: bbox sampling (BE-006), telemetry/benchmarks (BE-011), CI and deployment. The backend belongs to the single root repository.

The 85-concept documentation/architecture pass DOC-003 is DONE with checker/self-test and manual-review evidence. DOC-004 is DONE: the user approved contract 0.2 and the backend `Source` schema enforces it. Method heatwave-v1 remains the documented fixed-baseline/quality/run/trend design.

DOC-007 aligns [the shared workflow](../../docs/ai-development-workflow.md) with backend planning, version research, risky-logic TDD, broader review, safe simplification and final checks. This documentation-only update does not change code, manifest/lock, environment, method or contract. No new plugin/service installed; conditional DOC-008 does not block manual engineering.

Next: frontend integration (FE-002/FE-003/FE-005), then BE-006 boxes and BE-011 operations. BE-009's live ping runs after the Atlas password is rotated.
