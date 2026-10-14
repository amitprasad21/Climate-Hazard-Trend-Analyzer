# Backend documentation

| Source | Read/update when |
|---|---|
| [PRD](PRD.md) | Backend acceptance and boundaries change |
| [System design / architecture](system.backend.md) | Layers, lifecycle, scaling or observability change |
| [API guide](API.md) | Endpoint implementation/validation changes; root contract owns schemas |
| [Climate methodology](climate-methodology.md) | Any scientific rule changes |
| [Database](database.md) | Collections, indexes, consistency or retention change |
| [Data pipeline](data-pipeline.md) | Ingestion, normalization, caching, expiry or concurrency change |
| [Security and settings](security.md) | Configuration, limits, errors or trust boundaries change |
| [Testing](testing.md) | Verification commands/cases gain evidence |
| [Implementation plan](implementation-plan.md) / [tasks](tasks.md) | Scheduling and completion evidence change |
| [State](state.md) / [memory](memory.md) | Verified current status / durable context change |

The [shared AI workflow](../../docs/ai-development-workflow.md) owns roles and completion gates; [tasks](tasks.md) records backend-specific checkpoints.

Architecture, ingestion, caching, error-handling, deployment and observability are intentionally consolidated into these authorities. [Shared decisions](../../docs/decisions/README.md), [concept coverage](../../docs/system-design-coverage.md) and [tools](../../docs/skills-and-tools.md) prevent duplicate records. Settings/lifecycle/health have draft code; business behavior remains planned. State/testing distinguish these facts from verified acceptance.
