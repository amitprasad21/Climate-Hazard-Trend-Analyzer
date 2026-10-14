# Backend requirements

[Root PRD](../../PRD.md) owns IDs and provenance; [contract](../../INTEGRATION_CONTRACT.md) owns wire schemas. This document scopes backend work rather than redefining them.

Deliver FR-001 through FR-004 and FR-007 through FR-010, DATA-001 through DATA-007, SEC-001 through SEC-004 and NFR-004/NFR-005. A valid request must load consistent daily maxima, store/reread observations, apply deterministic quality and heatwave rules, and return metrics/series/insights with limitations.

Acceptance: point/city search and analysis work with real data; cache reuse avoids duplicate upstream work; schema/validation and safe errors agree with the frontend; excluded years stay null; no-event and insufficient-data outcomes differ; request and upstream work are bounded. The later box slice must disclose sampling rather than pretend to integrate a polygon.

MongoDB persistence is part of core acceptance, not an optional adapter demo. An in-memory repository may be a labeled test double only. No user account service, weather forecasting, AI inference or microservices. Tests and evidence are listed in [testing](testing.md); current completion remains in [state](state.md).
