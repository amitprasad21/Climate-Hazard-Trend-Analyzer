# Engineering rules

Apply the [shared AI workflow](../../docs/ai-development-workflow.md) before significant implementation: plan/research/architecture, approved scope, focused build, verification, review, safe simplification and final evidence. Use official version-specific sources when Context7 is unavailable. High/critical review findings block completion. TDD targets risky scientific/validation/cache/fallback behavior; trivial prose changes need documentation checks only.

- Architecture: follow [system boundaries](../../ARCHITECTURE.md). Routes validate/translate; services orchestrate; adapters perform external I/O; repositories own database queries; climate functions calculate. Do not create empty layers.
- API: an API is the agreed interface between caller and service. HTTP method/path identify an operation, JSON describes input/output, and status codes distinguish success from failure. GET reads; POST requests analysis. Use the versioned [contract](../../INTEGRATION_CONTRACT.md), consistent errors, explicit units and boundary validation. Never invent an endpoint.
- Components: prefer one responsibility and composition through props/events. Keep data fetching out of metric/chart presentation. Extract a component when reuse or complexity warrants it, not for every HTML element.
- Frontend: own form state and request lifecycle in the page/hook; render backend data. Abort/ignore obsolete requests. Use semantic controls, visible focus and responsive grid tracks. Test errors, long labels, nulls and narrow containers.
- Backend: avoid blocking network/database work on the event loop. Bound numerical input and offload only measured expensive CPU work. Maintain deterministic calendar and quality behavior.
- Tests: cover risky scientific branches and trust boundaries with focused tests. Contract tests join the repositories; integration tests prove database/provider adapters; browser tests cover the actual workflow. Report which dependencies were real and which were mocked. No fabricated pass counts.
- Traceability: consult the [85-concept matrix](../../docs/system-design-coverage.md), owning task, layer authority and acceptance before implementation. Review affected callers as well as the diff; update task/state/memory only with executed evidence. Deferred concepts are decisions with triggers, not mandatory new infrastructure.

Paths above are workspace-root references from this rules directory; see [root navigation](../../README.md).
