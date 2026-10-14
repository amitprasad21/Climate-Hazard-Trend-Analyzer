# Climate Hazard Trend Analyzer — UI Design System

> **Status:** Current specified visual source of truth, adopted 2026-10-14 from the user-supplied design update; not implemented or visually verified.  
> **Product:** Climate Hazard Trend Analyzer  
> **Visual direction:** Premium monochrome climate intelligence — pure black, white, and grayscale, with restrained atmospheric weather imagery.

## 1. Purpose

This document defines the visual language and interaction principles for the Climate Hazard Trend Analyzer dashboard. The interface should feel like a precise, premium climate-analysis instrument rather than a generic admin template.

The supplied brief describes a dark storm-weather reference with charcoal panels, thin gray borders, clean typography and understated iconography. No actual reference image or licensed local weather asset accompanied these Markdown files, so use a pure-black canvas and opaque panels initially. No screenshot match is claimed.

The application analyzes historical climate data. **All metrics, charts, heat-intensity views, and generated insights must be based on the backend response or clearly identified development fixtures.** Reference images are design inspiration, not real climate data.

The root [design entry point](../../DESIGN.md) links here without duplicating tokens. [PRD](../../PRD.md) owns requirements, [screens](screens.md) owns composition, [state](state.md) owns request states, and the [API contract](../../INTEGRATION_CONTRACT.md) owns data semantics. This update supersedes the previous colored-accent palette; it does not change scientific methodology or API meanings.

## 2. Design principles

1. **Monochrome only.** Use black, white, and grayscale for the interface, charts, controls, and maps. Do not introduce gold, blue, green, purple, red, or other colored accents.
2. **Data before decoration.** Data visualizations and analysis controls take priority over atmospheric backgrounds, decorative icons, and effects.
3. **Depth through contrast.** Use surface differences, fine borders, spacing, and typography rather than strong gradients or neon glow.
4. **One clear primary action.** The Analyze action should be visually distinct using a white surface and black text.
5. **Scientific honesty.** Never invent findings, present placeholders as real values, or imply statistical significance without valid analysis.
6. **Responsive by design.** The dashboard should reorganize for narrow screens rather than shrink its desktop layout.
7. **Accessible without color.** Meaning, chart series, statuses, errors, and selections must remain understandable without color alone.
8. **Reuse existing patterns.** Follow existing project conventions and components where they meet these requirements. Avoid needless dependencies and abstractions.

## 3. Color tokens

Use CSS variables or the project's equivalent design-token mechanism. Keep these values centralized and avoid ad hoc hex values in individual components.

| Token | Value | Usage |
|---|---|---|
| `--color-bg` | `#000000` | Global page background |
| `--color-surface-1` | `#0A0A0A` | Main cards and panels |
| `--color-surface-2` | `#111111` | Elevated or inset surfaces, popovers |
| `--color-surface-hover` | `#1C1C1C` | Hover and selected backgrounds |
| `--color-border` | `#292929` | Card outlines and separators |
| `--color-border-strong` | `#454545` | Decorative emphasis; insufficient alone for essential control boundaries |
| `--color-control-border` | `#737373` | Accessible input boundary on opaque dark surfaces |
| `--color-focus` | `#FFFFFF` | High-contrast focus outline |
| `--color-text-primary` | `#FFFFFF` | Main headings, values, primary labels |
| `--color-text-secondary` | `#888888` | Secondary labels, helper text, metadata |
| `--color-text-supporting` | `#B3B3B3` | Body copy and secondary chart labels |
| `--color-text-inverse` | `#000000` | Text on white primary actions |
| `--color-control-primary` | `#FFFFFF` | Primary action background and selected high-contrast controls |
| `--color-control-primary-text` | `#000000` | Text/icons on primary action |
| `--color-chart-primary` | `#FFFFFF` | Primary observed time series |
| `--color-chart-secondary` | `#A3A3A3` | Secondary comparison series |
| `--color-chart-tertiary` | `#707070` | Non-text marks only on opaque dark plots; not small axis or legend text |
| `--color-chart-grid` | `#292929` | Chart gridlines and subtle axes |
| `--color-map-low` | `#171717` | Lowest intensity in grayscale map |
| `--color-map-mid` | `#777777` | Mid intensity in grayscale map |
| `--color-map-high` | `#FFFFFF` | Highest intensity in grayscale map |
| `--color-overlay` | `rgba(0, 0, 0, 0.68)` | Overlay behind content on weather imagery |

### Contrast constraints

Static sRGB checks: secondary text `#888888` is 5.58:1 on surface-1, 5.33:1 on surface-2 and 4.81:1 on hover. Strong decorative border `#454545` is only 1.97:1 on surface-2; use control-border `#737373` where an input boundary is needed (3.98:1 on surface-2, 3.59:1 on hover). Tertiary chart marks `#707070` are 3.81:1 on surface-2, suitable for non-text marks but below the 4.5:1 small-text target. Use supporting text for essential labels and errors. White focus and black-on-white actions remain high contrast.

These are calculated opaque-token checks, not rendered accessibility verification. Imagery/translucency changes the actual background and requires a new rendered contrast check. Keep text/data panels opaque until that evidence exists.

### Color rules

- `#000000` is the page canvas. Cards may use `#0A0A0A` or `#111111` so sections remain visible.
- Use `#FFFFFF` for the most important text, values, and primary action.
- Use `#888888` for secondary labels. Do not make important instructions, error messages, or essential chart labels too dim.
- Use gray for borders, gridlines, inactive controls, and comparison series.
- Do not use colored status badges or colored chart lines. Use text, icons, line patterns, labels, and symbols to distinguish status.
- Do not rely on opacity alone to communicate meaning. Check rendered contrast for any text placed over imagery or translucent surfaces.
- Use visible focus indicators with a high-contrast grayscale outline.

## 4. Typography

Use a consistent, highly legible sans-serif family already available in the project. If the project does not have a suitable choice, use **Plus Jakarta Sans** for UI text and numerals, with appropriate system fallbacks. Do not add a font dependency if the project already has a consistent licensed font with similar readability.

Recommended hierarchy:

- **Product name / page title:** clear and prominent, not oversized enough to crowd the controls.
- **Section headings:** medium weight with concise wording.
- **Metric values:** large, high-contrast, tabular numerals where supported.
- **Field labels and metadata:** small but comfortably readable; use `#888888` only where contrast remains sufficient.
- **Chart axes and legends:** legible at mobile sizes, never clipped or hidden without an accessible alternative.

Keep the existing project choice initially: `ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif`. It is a readable local fallback and requires no new font package or network request. Plus Jakarta Sans remains an optional licensed/local choice if later evidence justifies it.

Use body 16px/1.5, controls 16px, secondary/axis text at least 12px, title `clamp(1.5rem, 2.4vw, 2.25rem)` and metric values `clamp(1.75rem, 3vw, 2.5rem)`. Use tabular numerals for metrics/tables. Avoid excessive font weights, all-caps paragraphs and dense tiny text.

## 5. Layout and spacing

- Use a restrained spacing scale consistently across the UI; prefer existing spacing tokens when available.
- Establish a clear content hierarchy: header, analysis controls, key metrics, primary analysis, supporting visualizations, and insights.
- Use a balanced dashboard grid on large screens and one main column on narrow screens.
- Give charts enough height and width to make axes, labels, and tooltips useful.
- Keep the main content within a sensible maximum width on very wide displays rather than stretching every card indefinitely.
- Avoid card nesting. A section should be a card only when the grouping helps comprehension.
- Align card edges, headings, controls, and chart areas consistently.

Retain the established spacing scale: 4, 8, 12, 16, 24, 32, 48px; panel radius 12px, control radius 8px, 1px panel border. Page padding is fluid from 16px to 32px; content max-width 1600px. Focus is a 2px white outline with 3px offset; primary white buttons use a separated outline visible against the surrounding dark surface. Aim for 44 x 44px interaction targets. Motion is 120–180ms opacity/color only, disabled where nonessential under reduced motion.

## 6. Surface treatment and atmospheric imagery

Use near-black panels with subtle charcoal borders and restrained, realistic depth. Mild translucency is acceptable where it improves the relationship between the dashboard and its background, but text and data must remain crisp.

The supplied description mentions dramatic storm-cloud imagery and a monochrome weather atmosphere; the actual image has not been supplied or inspected. If an appropriate existing, licensed, local asset is available, it may be used as a **subtle grayscale background** with a strong dark overlay. Otherwise, use a pure-black background. Do not fetch a random remote image at runtime or make an external image URL essential to the app rendering.

Rules:

- Background imagery must never reduce text or chart legibility.
- Prefer monochrome processing or a grayscale asset.
- Keep imagery low-contrast behind panels; do not put critical text directly over complex clouds without an overlay.
- Do not use animated weather backgrounds, intense blur, excessive glass effects, bright glow, or decorative effects that compete with the charts.
- Panel opacity, borders, and shadows should be consistent across sections.

## 7. Dashboard information architecture

The first version should be a focused, single-page climate analytics dashboard unless the existing PRD explicitly requires additional screens.

### 7.1 Header

Include:

- Product identity: **Climate Hazard Analyzer** or the established project title.
- A concise subtitle explaining historical regional climate analysis.
- Minimal navigation only if the documented product scope requires it.
- No unnecessary profile/avatar controls or fictitious product areas.

### 7.2 Analysis controls

Provide:

- Region selection: city/point and, when implemented, custom latitude/longitude bounding box.
- Hazard selection with **Heatwave selected by default**.
- Start and end years or an equivalent date-range control.
- A clear primary **Analyze trends** action.

Controls must have labels, validation, keyboard support, and responsive wrapping. Prevent invalid ranges and duplicate accidental submissions.

### 7.3 Summary metric cards

The intended metrics are:

- Detected heatwave events.
- Average heatwave duration.
- Trend estimate/direction, when calculated.
- Region-specific 95th-percentile threshold.

Use real backend results. Before an analysis runs, show a clear empty state (for example, an em dash with “Run an analysis to see results”). During analysis, show a purposeful loading state. If a metric is unavailable, explain why rather than inventing a number.

### 7.4 Primary chart: annual heatwave frequency

- Use white for the primary series.
- Use medium gray with a dashed or dotted line for a comparison series, if one is available and methodologically valid.
- Use subtle gray gridlines.
- Include axis titles/units, appropriate year labels, legends, and tooltips.
- Allow responsive resizing without illegible labels or page overflow.
- Never fill the chart with sample results in production mode.

### 7.5 Regional heat-intensity visualization

A map is optional unless required by the agreed PRD. If implemented:

- Use a grayscale intensity ramp from dark to white.
- Include a labeled legend and region context.
- Use real spatial data at an appropriate resolution.
- Do not fake a heatmap by coloring a static image or inventing geographic intensity values.
- Explain when available data resolution is insufficient for the selected region.
- Keep map controls usable on touch screens and keyboard-accessible where supported.

If no valid map data is available, show an informative unavailable state rather than a decorative false visualization.

### 7.6 Supporting charts

Potential charts:

- Average heatwave duration over time.
- Temperature anomalies relative to a documented reference period.

Differentiate series using brightness, line pattern, markers, labels, and chart structure—not color. Define anomaly units and baseline clearly.

### 7.7 Key insights

Insights must be generated from actual analysis results and include relevant context. They should distinguish an estimated trend from a statistically significant trend and disclose material data-quality limitations.

Do not claim a percentage increase, cause, or significance unless the backend supports that statement. Use an explicit empty state before results exist.

## 8. Component guidance

Reuse existing components if suitable. The following is a conceptual inventory, not a requirement to create a separate component for every item:

- Dashboard page/layout.
- Header or compact navigation.
- Region selector.
- Hazard selector.
- Period selector.
- Analyze action.
- Metric card.
- Chart panel.
- Chart legend/tooltip configuration.
- Regional visualization panel.
- Key-insights panel.
- Loading state/skeleton.
- Empty state.
- Error state with safe retry behavior.
- Data source/methodology note.

Keep presentation components focused. Keep HTTP requests and backend response handling in the established API/client layer. Do not perform authoritative climate calculations in UI components.

## 9. Interaction and UI states

Every applicable screen or control must consider the following states:

1. **Idle:** controls are available and no current result is presented as if calculated.
2. **Validating:** invalid input is explained close to the relevant field.
3. **Loading:** show clear progress feedback; prevent duplicate submissions where appropriate.
4. **Success:** render the returned metrics, charts, data provenance, and insights.
5. **Partial data:** explicitly indicate missing coverage and affected analyses.
6. **No events:** a valid analysis with zero qualifying events is successful; event count is zero and average duration is unavailable. Insufficient observations are a distinct typed error, never a zero-events conclusion.
7. **Error:** show a human-readable message and safe retry action where applicable.
8. **Cache context:** show cache/source timestamps returned by the backend. A fresh cache hit is not stale. The contract does not permit stale-result fallback, so do not invent a stale flag or stale-success path. Such a state requires an explicitly approved future contract.

Prevent old results from being mistaken for the latest selected region or period. Support keyboard interactions and clear focus states. Respect reduced-motion preferences.

## 10. Responsive behavior

Responsiveness is a required feature, not a finishing touch. Use CSS Grid/Flexbox and breakpoints based on layout needs, not device detection.

### Mobile (approximately 320–480 CSS pixels)

- Use a single-column primary layout.
- Ensure no unintended horizontal page scrolling.
- Stack or wrap the region, hazard, and period controls.
- Use an appropriately sized full-width analysis action where useful.
- Display metrics in one or two columns depending on the available width.
- Stack charts vertically and preserve usable chart labels, legends, and tooltips.
- Allow insight text to wrap naturally.
- Ensure maps, if implemented, do not overflow their containers.
- Use comfortably sized touch targets and readable field labels.

### Tablet (approximately 481–1024 CSS pixels)

- Use a balanced one- or two-column arrangement depending on available width.
- Allow controls to wrap without clipping.
- Place metric cards in a compact grid.
- Stack charts when a side-by-side view would make them too narrow.

### Desktop (approximately 1025 CSS pixels and above)

- Use a wider dashboard grid, with summary metrics arranged together.
- Give the annual frequency chart prominence.
- Place the regional visualization beside the primary chart only when both remain readable.
- Arrange supporting charts and insights into balanced columns.

### Ultra-wide displays

- Apply a sensible maximum content width or balanced grid.
- Avoid excessively long chart axes, giant text blocks, and stretched cards.

Representative viewport test sizes:

- 320 × 568
- 360 × 800
- 390 × 844
- 430 × 932
- 768 × 1024
- 1024 × 768
- 1280 × 800
- 1440 × 900
- 1920 × 1080

These are verification sizes, not required breakpoint values. Test long place names, large numbers, missing values, validation messages, empty states, and failed requests at narrow widths. Do not claim responsive verification unless the relevant checks were actually performed.

## 11. Accessibility

- Use semantic HTML and accessible names for inputs, buttons, menus, and chart controls.
- Ensure full keyboard navigation and visible high-contrast focus states.
- Maintain sufficient text contrast; verify all foreground/background combinations.
- Do not use `#888888` for tiny text on a translucent or image-heavy surface unless its rendered contrast remains adequate.
- Do not communicate chart meaning or request status by color alone.
- Pair visual states with text labels or symbols.
- Ensure chart information is available through accessible labels, summaries, or data tables where practical.
- Respect reduced-motion settings.
- Use meaningful alternative text for informative imagery; mark purely decorative backgrounds as decorative.

## 12. Chart and data integrity rules

- Backend calculations are authoritative.
- Keep units, period, source, baseline, and methodology available to the user where relevant.
- Do not fabricate historical observations, event counts, percent changes, significance, or heat intensity.
- Clearly identify development fixtures and keep them separate from production data.
- Use line style, dash pattern, markers, and labels for grayscale series differentiation.
- Ensure axis domains and tick formatting do not misrepresent the trend.
- Display an empty/error state instead of a plausible-looking but false graph.

For this project, frequency means annual event starts; duration means average observed event days for events started in that year; anomaly means annual mean daily maximum temperature minus the fixed baseline mean daily maximum. Render backend values only. Primary annual frequency uses a solid white line with markers; the backend-provided five-year rolling series uses a dashed `#A3A3A3` line. Do not connect across null years. Include explicit series labels, units and an accessible table/detail path. Approximate plot heights are 280–360px; reduce tick density instead of text size.

Regional context can show actual selected coordinates/sample points and source resolution. Intensity shading remains unavailable unless the backend supplies scientifically valid spatial observations; the grayscale map tokens are reserved, not authorization to draw a heatmap.

## 13. Frontend performance

- Reuse the project's existing chart and UI dependencies where practical.
- Avoid adding a second charting library for a single feature.
- Avoid unnecessary rerenders and duplicate requests.
- Keep large visualizations responsive and limit expensive operations on the main thread.
- Do not add animation or image assets that significantly compromise loading performance.
- Measure before applying complex optimizations.

## 14. Rules for implementation agents

Before modifying UI code:

1. Read this file and applicable `AGENTS.md`, `.agent/rules/`, frontend PRD, screen specifications, state documentation, and API contract.
2. Inspect current components, styling, dependencies, and tests.
3. Identify the smallest relevant task and its acceptance criteria.
4. Reuse existing components and tokens when appropriate.
5. Update centralized tokens before adding one-off styling.
6. Implement loading, empty, error, success, and partial-data states relevant to the change.
7. Add or update tests.
8. Run the available lint, type-check, build, and targeted tests.
9. Verify responsive behavior using the supported browser or test tooling when available.
10. Update task status and documentation with actual evidence.

Do not reinstall skills or tools already present. Do not change the approved monochrome theme without explicit product-owner approval. Do not start a separate service or modify Git configuration for a visual change. Do not mark a task complete solely because files were generated.

## 15. Definition of design acceptance

The UI design can be accepted when:

- All visual elements follow the black/white/gray palette.
- The dashboard hierarchy matches the product requirements.
- The approved atmospheric reference is used subtly or replaced by a clean black canvas if no suitable local asset exists.
- Controls are understandable, labeled, and usable.
- Metrics, charts, and insights use real API results or unmistakably labeled development fixtures.
- Every important interaction has appropriate loading, error, empty, and success behavior.
- The dashboard is responsive at the representative viewport sizes, verified to the extent supported by tools.
- No unintended horizontal overflow, clipped controls, or illegible chart labels remain.
- Accessibility checks are performed and outstanding problems are documented.
- Frontend and backend contracts remain consistent.
- Relevant tests and quality checks are run and their results are recorded.
- The implementation does not introduce unnecessary dependencies or unrelated changes.

## 16. Change policy

This document is the authoritative frontend visual-design reference. Update it when a deliberate product-level design decision changes. Do not silently drift from it during implementation.

Record significant design decisions and explain their rationale. If a requirement conflicts with this design system or existing architecture, identify the conflict and propose the smallest consistent resolution rather than making an unsupported change.

## 17. Current implementation and handoff

FE-001 implemented the token sheet (src/styles/tokens.css, test-locked to section 3), global styles and the semantic shell. This document incorporates the supplied design and UI implementation brief; FE-001 starts the runnable shell, FE-002 owns controls/request state, FE-003 owns backend result presentation, and FE-005 owns visual/responsive/accessibility acceptance. The [implementation plan](implementation-plan.md) maps those phases to existing tasks. Do not mark the dashboard implemented merely because these instructions have been updated.

The user-supplied Downloads files remain unchanged. No local weather asset, font package, UI library, service or Git configuration is introduced by the design-document update. See [verification](../../docs/verification.md) for checks actually run.
