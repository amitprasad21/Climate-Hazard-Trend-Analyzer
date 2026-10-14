# Heatwave methodology

Proposed implementation identifier: `heatwave-v1`. These assumptions are explicit project decisions. The assessment supplied an example run definition; it did not prescribe a reference baseline, calendar-day percentile, regional weighting or significance procedure. This is a historical exploratory indicator, not a national heat warning standard.

## Source and reference period

Use one eligible reanalysis source consistently for baseline and analysis. The latest user direction prefers NASA POWER daily T2M_MAX with explicit UTC for supported periods and permits Open-Meteo fixed ERA5/Celsius/GMT as a no-key fallback when terms and coverage allow. [Provider policy](data-pipeline.md) owns access, date coverage, grid/provenance and source selection. Raw 1990–2020 endpoint probes succeeded; adapters and climate integration are not implemented. Contract 0.2 (DOC-004) describes both sources truthfully. Never label NASA data as ERA5 or mix the sources to fill missing days.

Use fixed baseline **1991-01-01 through 2020-12-31**. This 30-year reference is a project assumption chosen for stability between user-selected analysis windows. Fetch baseline independently when it lies outside the selected period. Never recompute the threshold from the selected analysis window. Report overlapping baseline/analysis periods honestly; comparison is descriptive, not independent experimental evidence.

A fixed all-season threshold is deliberately simple and matches the example's single regional percentile. It does not adjust by day of year, may underrepresent unusually hot shoulder seasons, and cannot capture humidity or nighttime stress. A day-of-year threshold is a separate future method requiring new tests and cache version.

## Normalization and quality

1. Create the expected inclusive UTC date sequence, including February 29. Sort provider dates and reject malformed/out-of-range dates or mismatched array lengths.
2. Missing/explicit-null dates are missing. Reject nonfinite numbers, nonnumeric values and maxima outside -90..65 C as invalid; this is a broad plausibility screen, not proof of observational correctness. Never trim high percentiles merely because they are extreme.
3. Identical duplicate date/value records collapse to one and increment duplicate-date diagnostics. Conflicting duplicates invalidate the date; no arbitrary last-write-wins. Keep source retrieval metadata.
4. Never interpolate, forward-fill or bridge invalid/missing days. Such days break exceedance runs. Expose quality counts and warnings.
5. A calendar year is eligible with at least 90% valid days overall and at least 80% in every calendar month. These gates limit gross missingness bias but do not eliminate bias. Percentages use actual leap/month day counts without rounding for eligibility.
6. Every baseline year must meet those same gates; otherwise fail INSUFFICIENT_BASELINE. A baseline with eligible but incomplete data gets a warning. Analysis years failing gates have null science metrics. If none are eligible, fail INSUFFICIENT_DATA.

At regional-day level, valid+missing+invalid must equal expected. Duplicate dates are an independent diagnostic. For box samples: any invalid sample makes the regional day invalid; otherwise any missing sample makes it missing. This priority keeps categories disjoint.

## Regional series

For a point, retain the requested location and report provider-resolved coordinates/elevation only when genuinely known. NASA response geometry can echo the requested point; do not infer a grid-cell center or deduplicate cells from it. Contract 0.2 reports unknown resolved geometry as null with warning RESOLVED_LOCATION_UNKNOWN. The series represents gridded reanalysis near the city, not all neighborhoods or the entire named state.

The later box feature accepts at most 2 degrees in latitude and longitude, within +/-85 latitude, without antimeridian crossing. Subdivide each axis into three equal cells; sample the nine cell centers. For each day calculate the mean of sample daily maxima weighted by cosine(latitude). This approximates a sampled regional series, **not** the maximum of regional mean hourly temperature, an exact area mean, or a regional event footprint. Threshold that aggregated series consistently over baseline and analysis.

If multiple sample centers resolve to one source grid cell with the same returned elevation and source settings, reuse the proven identical series, combine their weights, and disclose the number of unique series/cells. Matching coordinates alone do not justify merging differently elevation-adjusted series. Require every unique sampled series each day; never change geographic weights on missing days. No station/grid-cell heatmap is justified by this regional summary. A location/sample-point diagram is a valid geographic alternative.

## Percentile and events

Compute the 95th percentile from all valid baseline regional-day maxima. With sorted values x[0..n-1], h=(n-1)*0.95; interpolate linearly between floor(h) and ceil(h). Use full precision for comparisons, serialize only after calculations. A maximum equal to the threshold does not exceed it.

An event is a maximal run of **at least three consecutive calendar days strictly above** threshold. A date gap, null, invalid value or non-exceedance ends a run. Scan across internal December/January boundaries without resetting. Flush the final run at the period end. Leap days are ordinary days.

Detection is restricted to the requested period. Runs touching the first/last analysis day are flagged `boundary_censored`; observed duration may be shorter than the full event and a two-day clipped segment cannot qualify. Return a warning and partial status. Label durations as observed within the period; do not claim to know the true start outside it. No unbounded padding fetch is required.

Exclude a whole run from event/summary statistics if it touches an ineligible analysis year. This avoids counting the tail as a new event in the next eligible year. Warn about those exclusions. Valid years can still contain gaps that split an event; describe counts/durations as data-limited where applicable.

## Metrics and time series

- Event frequency: count qualifying event starts per calendar year. A cross-year event is counted once in its start year.
- Event duration: inclusive number of observed days. Annual mean/max duration uses events started in that year, including days in the following eligible year. Summary duration averages events, not annual means. No events => duration null, never 0 days.
- Heatwave days: apportion event days to each calendar year, independently of event-count attribution.
- Intensity: event mean and maximum excess above the fixed threshold, in C. Do not map regional intensity onto unsupported spatial cells.
- Anomaly: annual mean daily maximum temperature minus the baseline mean daily maximum temperature of the same regional series. Label it “daily maximum temperature anomaly”; it is not mean-temperature anomaly.
- Rolling frequency: trailing mean over exactly five consecutive eligible annual counts, including zero-event years. Missing/ineligible year => null until a complete five-year window resumes. First four requested years => null.
- Ineligible year: all scientific fields null; retain year and coverage. Charts break at nulls.

## Trend and insights

Use ordinary least squares on actual year numbers and eligible annual event counts with at least ten eligible years. The coefficient is events/year per year. Positive/negative/zero coefficient gives increasing/decreasing/flat; fewer years gives insufficient_data and null slope. Determine sign before rounding; flat does not mean no climatic change. This minimum is a pragmatic project rule, not a statistical significance threshold.

No p-values, confidence intervals, causal claims or “statistically significant” text in v1. Count time series can have autocorrelation, sparse events and non-normal residuals; simple OLS is descriptive only. Do not calculate a percentage increase from a zero denominator. Prefer event totals, observed duration, eligible-year count, slope and explicit coverage warnings over dramatic percentage headlines.

Insights must include numerical evidence and period and be generated from the same result, without an LLM. Always distinguish source limitations, spatial approximation and missing-data bias from a substantive finding.

## Deterministic test design

CLIMATE-BASELINE: known small sorted samples with independently calculated interpolation; equality threshold; baseline outside request; eligibility at/below month/year cutoffs; leap counts.

CLIMATE-RUNS: 2 versus 3 versus longer days; final run flush; absent calendar date; null/invalid separator; exact threshold; duplicated/conflicting date; cross-year one-event attribution; requested-boundary censoring; ineligible-year crossing exclusion; no events.

CLIMATE-TREND: known positive/negative/zero slopes, actual nonconsecutive year coordinates, fewer than 10 years, zero denominators, trailing-five-year gaps and event-weighted summary means.

CLIMATE-SPATIAL: nine centers and cosine weights, collapsed grid cells, missing/invalid sample priority, invalid/large/antimeridian boxes. Test fixtures are explicitly synthetic and confined to tests/development; never production observations.
