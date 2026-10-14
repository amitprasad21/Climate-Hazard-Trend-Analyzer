# Frontend requirements and use cases

[Root PRD](../../PRD.md) owns requirement IDs. Deliver the user-facing parts of FR-001 through FR-010 and NFR-001 through NFR-004/NFR-006. Keep one analysis page. Audience/context: [PRODUCT](../../PRODUCT.md).

| Use case | Preconditions and action | Expected result / failure |
|---|---|---|
| UC-001 Location | App loaded; enter city, choose disambiguated result or coordinates | Display selected coordinates; keyboard accessible result list; no match differs from network failure |
| UC-002 Period | Location chosen; enter valid full start/end years, Heatwave default | Client guidance and server validation; reversed/future/oversize range blocked with a clear message |
| UC-003 Analyze | Valid form; activate Analyze once | Real pending state, duplicate disabled, matching response becomes metrics/plots/insights |
| UC-004 Read | Successful response | Units, period, threshold, source, coverage and caveats remain visible; chart details accessible by keyboard/table |
| UC-005 No events | Successful response with zero qualifying runs | Count zero, duration unavailable, valid chart zeros; no alarming fabricated finding |
| UC-006 Partial/missing | Partial response or insufficient-data error | Coverage warnings and null gaps; insufficient data never becomes a zero-events conclusion |
| UC-007 Recover | Network/protocol/timeout/rate error | Preserve form, safe message, request ID if available and explicit retry; respect Retry-After |
| UC-008 Edit during work | Pending or populated result; change a parameter | Cancel/ignore old request; old metrics hidden; obsolete errors also ignored |
| UC-009 Narrow/keyboard | Any state at 320px or keyboard-only | Controls readable, no page overflow, usable focus order and chart alternative |
| UC-010 Bounded area | BE-006 available; select supported bbox | Show actual sample points and approximation; larger/unsupported boxes receive clear validation |

Use cases map to UI-LIFECYCLE, UI-RESPONSIVE, UI-A11Y and E2E-ANALYSIS in [testing](testing.md). No route proliferation, account flow or manually written calendar is required.
