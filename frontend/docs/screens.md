# Dashboard brief and states

Surface: `/`, mode **Operate**. The user selects where/when and receives an understandable heatwave analysis. The primary action is Analyze trends (white surface, black text). The focal result is annual frequency with threshold/source context, followed by duration/anomaly and limitations. The updated visual authority is [monochrome design](design.md); it supersedes the prior colored-accent direction.

## Sections

| Section | Purpose / input | Interaction and output |
|---|---|---|
| Header | Climate Hazard Analyzer; brief historical-analysis subtitle | One heading; no unrelated navigation |
| Analysis form | City/coordinates, Heatwave, start/end year | Explicit labels, native year inputs, semantic button, inline errors |
| Result context | Response region/period/source | Shows the parameters actually analyzed; never current form with old results |
| Four metrics | Backend event count/duration/trend/threshold | Readable values and units; em dash with explanatory text for null |
| Heatwave calendar | Backend events by year and day of year | One row per year, bars over event days shaded by labelled peak-excess groups, censored/excluded markers, hover details; selecting a row opens the year panel |
| Year panel | Native "Inspect a year" list and the selected year's backend values | Values or exclusion reasons plus the events touching that year; filters the events table; Escape or "Show all years" clears it |
| Frequency plot | Backend annual rows | Solid white annual counts, dashed gray rolling series with explicit labels, focus/table details; hovering or selecting a year is mirrored in every chart and the calendar |
| Geographic context | Coordinates/sample points/source resolution | Grayscale context or unavailable state; no intensity shading without valid spatial data |
| Secondary plots | Backend duration/anomaly | Gaps for nulls, readable years, data table alternative |
| Insights/method | Evidence, coverage and warnings | Wrapping text, method disclosure, attribution links |

No-events is a populated success state; loading, errors and no data are not charts with invented lines. Use a single composed empty state before analysis rather than six nested placeholder cards. Large metrics must wrap or resize within tokens without cutting significant digits. Long region names and error text wrap naturally.

## Lifecycle presentation

Idle: explain the required selection and heatwave rule; show no fabricated figures. Pending: announce “Analyzing historical weather”, disable duplicate Analyze, allow cancellation through edits; list only real stages (server waking or ready, analysis requested with elapsed seconds), static placeholder outlines without numbers, and a slow-wait note after 45 s; no fake percent. A result saved in this browser appears at once and says so. Success: show only the returned period/region. Partial: same layout with prominent coverage warning and omitted-year gaps. Error: short recovery message, retain inputs, focus/announce appropriately. Dirty parameters: hide old results and indicate that analysis needs to run again.

Desktop uses a compact header/form, metric row, primary 2:1 chart/geography row and balanced lower plots/insights. Tablet stacks any plot that becomes cramped. Mobile follows the exact reading order in one column with a full-width Analyze action; map/diagram height stays bounded. The calendar and year panel share a row from 1024 px and stack below it. [Responsive evidence](responsiveness.md) covers all nine sizes.

All controls, charts, statuses and geographic context use grayscale. Errors/partial states use explicit headings, text and symbols; trend direction never acquires a good/bad color. Supporting text remains readable on opaque panels. No atmospheric asset was supplied; pure black is the specified fallback. The reference description is not a screenshot or dataset.

A fresh cache hit retains backend source/generated timestamps and is not labeled stale. The contract prohibits stale-result fallback; no stale-success state or API field is introduced. Insufficient observations remain a typed error; zero detected events remains success.
