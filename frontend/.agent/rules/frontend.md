# Frontend engineering rules

Use [the shared workflow](../../../docs/ai-development-workflow.md): plan significant slices, research actual frontend package versions, apply Impeccable guidance or documented manual UI review, then verify/review/simplify and recheck affected behavior. Keep all tool setup decisions in the shared registry. FE-005 cannot complete without the responsive/accessibility evidence its tracker requires.

Follow [canonical design](../../docs/design.md) and [responsive requirements](../../docs/responsiveness.md). Use pure black, white and grayscale only, including status messages and charts; no colored accents. Use patterns/markers/labels as well as brightness. Use a pure-black background unless a suitable licensed local grayscale asset exists and rendered contrast is verified. Use semantic native controls, visible focus, reduced motion and text/table alternatives to charts. Do not equate a CSS breakpoint with verified responsiveness.

Follow [system design](../../docs/system.frontend.md): keep presentation separate from HTTP/request state. API types follow [contract](../../../INTEGRATION_CONTRACT.md). Use AbortController and response tokens to reject stale results/errors; clear old analysis when parameters change. Do not duplicate backend calculations.

Do not add a calendar, UI framework, map, state store or router until a task demonstrates need. Inspect existing package/scripts before installation/builds. Inputs and API text are untrusted; render as text, avoid raw HTML and keep secrets out of browser settings.

Run relevant tests/type/lint/build and actual viewport checks once tooling exists. Report unavailable checks. Preserve the single root Git history and unrelated work; no automatic commit/push. Update local state/tasks/memory after verified changes.

Consult the [concept matrix](../../../docs/system-design-coverage.md) and owning task before a focused change. Review affected callers as well as the diff. Render source metadata exactly as contract 0.2 defines it; do not invent frontend-only alternatives. Fixture interaction work can proceed independently, but final integration and responsive DONE require real evidence under the task's acceptance.
