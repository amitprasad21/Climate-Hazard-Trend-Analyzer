# Responsive behavior and evidence

Responsive behavior is a feature requirement. Measured 2026-10-14 in the Claude desktop browser pane (Chromium) against the live API: idle and populated states at every size, plus synthetic stress data (long label, six-digit numbers, null years, unbroken long text) at 320, 768 and 1920. Two defects were found and fixed: a chart clipped under stale resize measurements, and long unbroken words overflowing result panels. Keyboard order and focus were checked at 320 x 568, and 320 px reflow covers 400% zoom. Screenshots per size were **not** reviewed because the pane was hidden; FE-005 stays open for that.

Re-measured 2026-10-14 after FE-007 with the calendar, year panel and a selected year populated (New Delhi 1995–2024, local API, Claude pane Chromium, emulated sizes): 0 px page overflow at all nine sizes; the calendar and line-chart SVGs match their containers once the resize settles; at 320 px nothing in the results extends past the viewport and month labels become initials; the calendar and year panel share a row from 1024 px. Hidden-pane screenshots again proved unreliable (one 320 px capture showed a different scroll position), so visual review relied on one 1280 px capture plus measurements.

Re-measured 2026-10-15 after FE-008 with the picker map and a box result map on the page: 0 px page overflow and nothing outside the viewport at all nine sizes; both maps fit their containers (255 and 221 px wide at 320 px, 735 and 702 px at 1920 px). Leaflet's own window-resize handling keeps the tiles filled.

| Viewport | Required emphasis | Actual status |
|---|---|---|
| 320 x 568 | Single column, long title/input labels, action reachability, no page overflow | VERIFIED 2026-10-14: no overflow, nothing outside viewport, controls ≥44 px (idle, populated, error, synthetic stress tests pass) |
| 360 x 800 | Touch controls, metric wrapping and plot/table access | VERIFIED 2026-10-14: no overflow, nothing outside viewport, controls ≥44 px (idle, populated, error tests pass) |
| 390 x 844 | Tooltips/focus, region labels and errors | VERIFIED 2026-10-14: no overflow, nothing outside viewport, controls ≥44 px (idle, populated, error tests pass) |
| 430 x 932 | Chart tick density and insight wrapping | VERIFIED 2026-10-14: no overflow, nothing outside viewport, controls ≥44 px (idle, populated, error tests pass) |
| 768 x 1024 | Two-column metrics where viable, stacked narrow plots | VERIFIED 2026-10-14: no overflow, nothing outside viewport, controls ≥44 px (idle, populated, error, synthetic stress tests pass) |
| 1024 x 768 | Toolbar wrapping, balanced panels at limited height | VERIFIED 2026-10-14: no overflow, nothing outside viewport, controls ≥44 px (idle, populated, error tests pass) |
| 1280 x 800 | Desktop chart/geography arrangement | VERIFIED 2026-10-14: no overflow, nothing outside viewport, controls ≥44 px (idle, populated, error tests pass) |
| 1440 x 900 | Header density and secondary-chart balance | VERIFIED 2026-10-14: no overflow, nothing outside viewport, controls ≥44 px (idle, populated, error tests pass) |
| 1920 x 1080 | Centered max-width layout without overstretched plots | VERIFIED 2026-10-14: no overflow, nothing outside viewport, controls ≥44 px (idle, populated, error, synthetic stress tests pass) |

Use Grid/Flexbox with fluid sizing, minmax(0,1fr), min-width:0, wrapping text and inputs constrained to their containers. No device detection or separate mobile codebase. The [design system](design.md) defines token values and candidate content thresholds.

Verify idle, pending, error, no-events, partial and populated states at representative widths, with all nine widths checked for page overflow and primary workflow usability. Use a >100-character region label, large metric values, null duration/trend, long warnings and sparse chart series. Synthetic fixtures are only for test mode and visibly identified when manually viewed.

Automate `scrollWidth <= clientWidth` on the page, but also visually inspect clipping, label overlap, focal order, controls and chart legends; a numerical overflow pass can miss truncation. Save viewport/state/browser/version evidence with screenshots when tools permit. Check keyboard, focus, touch targets, 200% zoom/reflow and reduced-motion separately; viewport size alone does not prove accessibility.

Charts use a responsive container and visible units; fewer ticks on narrow plots, no tiny text workaround. Geography has bounded height and follows the frequency plot in mobile reading order. Long explanations use natural wrapping. Tables may scroll inside a clearly labeled region if necessary; the page itself must not scroll horizontally.

Mobile uses one primary column, intentionally stacked/wrapped filters and a full-width Analyze action; metric cards use one or two columns only when complete labels/values fit. Touch targets aim for at least 44 x 44 CSS pixels. Header identity/action remain understandable without a separate mobile navigation. Tablet may use two metric columns, but plots stack as soon as side-by-side labels become crowded. Desktop uses the larger frequency chart beside restrained geography and balanced secondary plots/insights. Ultra-wide layouts stay centered at the design maximum rather than stretching text and charts indefinitely. Test both pointer and focus detail paths; an available hover tooltip does not establish touch usability.

At each listed viewport record browser/version, state, measured overflow and visual findings, with an artifact path if a screenshot is captured. Check long region/error/insight text, missing metrics and large values. Keyboard order, focus visibility, zoom/reflow, contrast and reduced motion require their own checks. The concept matrix maps responsive design/testing (16/81) to FE-001 and FE-005; all current rows correctly remain NOT RUN.

If browser automation or screenshots cannot run, record that exact limitation and static checks performed. Do not mark FE-005 or the dashboard complete based on CSS alone.
