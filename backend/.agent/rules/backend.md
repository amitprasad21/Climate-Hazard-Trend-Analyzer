# Backend engineering rules

Use [the shared workflow](../../../docs/ai-development-workflow.md) for significant-slice planning/approval, official version-specific research, architecture review, TDD for risky behavior, broader review, safe simplification and final verification. Keep tool setup decisions in the shared registry; preserve validation, timeouts, retry limits, science and cache safeguards through refactors.

Read [methodology](../../docs/climate-methodology.md) before changing calculations, [pipeline](../../docs/data-pipeline.md) before ingestion/cache edits, [database](../../docs/database.md) before query/index changes, and [security](../../docs/security.md) for settings or external I/O.

Keep schemas aligned with [API contract](../../../INTEGRATION_CONTRACT.md). Routes translate failures; services coordinate; provider code validates upstream; database access stays in repositories. Pure climate functions accept normalized data and explicit dates, never live clock/network/database state.

Test equality at threshold, missing and duplicate dates, leap days, cross-year runs, quality exclusions, zero events and unavailable trends. Changing a scientific rule requires method/cache-version review. All observations retain source/model identity. Cache hits must not bypass expiry checks or rewrite source timestamps.

Use fixed provider hosts, bounded attempts, timeouts, resource limits, exact CORS and safe errors. Do not log secrets or suppress failing security checks. Preserve the single root Git history and unrelated changes; no automatic commit/push. Update [tasks](../../docs/tasks.md), [state](../../docs/state.md) and [memory](../../docs/memory.md) with actual evidence.

Read the relevant [concept IDs](../../../docs/system-design-coverage.md) and required tests. Full-source fallback must cover baseline and analysis without blending NASA/ERA5 records. Source/contract changes need coordinated provenance and cache review. Connectivity-only work creates no collections/indexes. Async code still needs elapsed deadlines including DNS, cancellation and closure tests. Keep real provider/DB probes separate from mocked behavior evidence.
