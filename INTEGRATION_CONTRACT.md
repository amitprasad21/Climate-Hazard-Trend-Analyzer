# Frontend/backend integration contract

Contract version: **0.2** (approved by the user 2026-10-14 under DOC-004/ADR-017; supersedes the ERA5-only 0.1 source object). Liveness and an additive readiness endpoint are implemented with mocked API tests; backend request/error schemas are tested (BE-001). Search/analysis endpoints and consumer schemas are planned. Schema changes require this document, both consumers, contract tests and method/cache-version review in the same logical change. The backend owns scientific results. The browser only formats, selects and renders returned values. The source object below describes NASA POWER and Open-Meteo ERA5 truthfully; see [Source provenance (0.2)](#source-provenance-02).

## Conventions and validation

JSON keys use snake_case. Temperatures/anomalies are degrees Celsius, durations days, slopes events/year per year. Dates use ISO `YYYY-MM-DD`; timestamps use RFC 3339 UTC with `Z`. Daily temperatures use UTC calendar days; selected years include January 1 through December 31. Coordinates use WGS84 latitude/longitude in decimal degrees. No NaN/Infinity is valid JSON. Required fields always appear; explicitly nullable fields use `null`, never invented zero.

Input objects reject unknown fields and numeric strings. Finite latitude is -90..90 and longitude -180..180. Canonicalize coordinates to four decimal places before fetching/caching and echo the canonical coordinates; do not round distinct requests only in the cache. Labels are plain text, trimmed, 1-120 characters with control characters rejected. Region labels have no scientific meaning and are escaped by React.

Period: integer `start_year` and `end_year`; 1940 <= start <= end (1940 is the outer bound; actual eligibility depends on enabled sources, see source provenance); at most 50 inclusive years; end <= last fully available calendar year, conservatively using current UTC date minus 7 days and requiring that year's December 31 to be in the past availability window. The UI may present this as two native number inputs. The server remains authoritative.

## Endpoints

| Method / path | Request | Success | Failures / caching / limits |
|---|---|---|---|
| `GET /api/v1/health` | None | 200 Health | Liveness only; no DB/provider calls, no cache; deployment-level request limit |
| `GET /api/v1/health/ready` | None | 200 `{status:"ok", api_version:"v1", database:"available"}` | Additive connectivity draft; DB ping, 503 STORAGE_UNAVAILABLE on outage; no-store; mocked API tests only |
| `GET /api/v1/regions/search?q=...` | Trimmed q, 2-100 chars; fixed max 10 results | 200 RegionSearch | 422/429/502/504/500; empty result is 200; proposed in-process 24h bounded cache; 30/min/client |
| `POST /api/v1/analyses/heatwaves` | AnalysisRequest | 200 AnalysisResponse | 422/429/502/503/504/500; server cache only, 5/min/client; no automatic browser retry |

No retrieval endpoint or persisted public analysis ID is required. No 202/job status contract. OPTIONS supports configured CORS preflight. Unknown routes/methods return 404/405 ErrorResponse. Wrong content type returns 415, oversize body 413. All application errors use the same envelope; gateway-generated failures may not, and the client must handle non-JSON errors safely.

## Request schema

The following TypeScript notation defines wire shapes, not implemented frontend code. Unless noted, all properties are required.

```typescript
type Period = { start_year: number; end_year: number };
type Point = { latitude: number; longitude: number };
type PointRegion = {
  kind: "point"; label: string; latitude: number; longitude: number;
};
type BoxRegion = {
  kind: "bbox"; label: string;
  south: number; west: number; north: number; east: number;
};
type AnalysisRequest = {
  hazard: "heatwave"; region: PointRegion | BoxRegion; period: Period;
};
```

First slice implements `point` only. Until BE-006 passes its gates, `bbox` returns 422 `UNSUPPORTED_REGION`; it must not silently become a point. Planned box bounds: south < north, west < east, neither dimension >2 degrees, no antimeridian crossing, latitude inside -85..85. Sampling is exactly the 3x3 cell-center grid described in the methodology. No arbitrary sample count or caller-selected baseline/model.

Illustrative request only (coordinates are input, not climate findings):

```json
{
  "hazard": "heatwave",
  "region": {"kind": "point", "label": "New Delhi", "latitude": 28.6139, "longitude": 77.2090},
  "period": {"start_year": 1990, "end_year": 2020}
}
```

## Response schemas

```typescript
type Health = { status: "ok"; api_version: "v1" };
type RegionResult = {
  id: number; name: string; admin1: string | null; country: string;
  country_code: string; latitude: number; longitude: number;
};
type RegionSearch = { results: RegionResult[] };
type Warning = { code: string; message: string; years: number[] };
type Insight = {
  code: string; text: string;
  evidence: { metric: string; value: number; unit: string; years: number[] }[];
};
type Coverage = {
  expected_days: number; valid_days: number; missing_days: number;
  invalid_days: number; duplicate_dates: number; coverage_fraction: number;
};
type YearCoverage = Coverage & {
  year: number; eligible: boolean; excluded_reasons: string[];
};
type SamplePoint = {
  requested: Point; resolved: Point | null; elevation_m: number | null;
};
type Event = {
  start_date: string; end_date: string; duration_days: number;
  mean_excess_c: number; max_excess_c: number;
  boundary_censored: boolean;
};
type Annual = {
  year: number; eligible: boolean; coverage_fraction: number;
  event_count: number | null; mean_duration_days: number | null;
  max_duration_days: number | null; heatwave_days: number | null;
  mean_tmax_c: number | null; tmax_anomaly_c: number | null;
  frequency_rolling_5y: number | null;
};
type AnalysisResponse = {
  contract_version: "0.2"; request_id: string;
  region: PointRegion | BoxRegion; period: Period;
  status: "complete" | "partial";
  summary: {
    event_count: number; mean_duration_days: number | null;
    threshold_c: number;
    trend_direction: "increasing" | "decreasing" | "flat" | "insufficient_data";
    frequency_slope_per_year: number | null;
    trend_year_count: number;
  };
  annual: Annual[]; events: Event[]; insights: Insight[]; warnings: Warning[];
  methodology: {
    version: "heatwave-v1"; baseline_start: "1991-01-01";
    baseline_end: "2020-12-31"; percentile: 95;
    percentile_method: "linear"; minimum_consecutive_days: 3;
    comparison: "strictly_greater"; daily_timezone: "UTC";
    aggregation: "point" | "nine_point_cosine_weighted_mean";
    anomaly_reference: "baseline_mean_daily_maximum";
    trend_method: "ordinary_least_squares_descriptive";
    significance_tested: false;
  };
  data_quality: {
    baseline: Coverage; analysis: Coverage; years: YearCoverage[];
    eligible_year_count: number;
  };
  source: {
    provider: "nasa_power" | "open_meteo"; model: "MERRA-2" | "ERA5";
    dataset_kind: "reanalysis";
    grid_degrees: { latitude: number; longitude: number };
    time_standard: "UTC"; temperature_unit: "celsius";
    normalization_version: "daily-tmax-v1";
    sample_points: SamplePoint[];
    attribution_url: string; retrieved_at: string;
  };
  cache: { hit: boolean; generated_at: string; expires_at: string };
};
```

`annual` contains one chronologically sorted row for every requested year. Ineligible rows have all scientific numerical fields null except coverage. Eligible no-event rows have event_count=0, heatwave_days=0 and null duration fields. `events` includes only runs eligible under the methodology; summary count equals events.length and sum of annual event_count over eligible years. Events are sorted and non-overlapping, inclusive duration = end-start+1. Heatwave days are apportioned to calendar years; event count and whole-event duration belong to the start year. Mean summary duration is the event-weighted mean, never a mean of annual means.

`status=partial` if analysis coverage is below 100%, any year is excluded, or boundary-censored events occur. Baseline failures never return a plausible threshold: return 422. Analysis with no eligible year also returns 422. Zero events with adequate data returns 200. `trend_year_count` counts eligible years; slope is null and direction insufficient_data with fewer than 10 eligible years. Confidence intervals and p-values are absent because no significance inference is made.

Coverage counts are at regional-day level after normalization/aggregation. `missing_days` counts absent/null dates; `invalid_days` counts rejected non-null/conflicting input dates. These are disjoint, with valid+missing+invalid=expected. `duplicate_dates` is an independent diagnostic count, not added to that sum. Box data additionally fails a day if any unique sampled source series is invalid/missing. Warnings explain missing baseline values, region approximation, shared grid cells, UTC days, cross-boundary truncation and omitted years where applicable.

Calculate at full precision. Serialize temperature/anomaly/excess values to 3 decimal places, duration means to 3, coverage to 6, slope to 6; determine trend direction from the full-precision slope. UI may format temperatures to 1 decimal and mean duration to 1, but must keep an exact threshold in methodology/details to avoid confusion around strict comparison. Integers stay integers. A tiny nonzero slope must not be described as exactly flat merely because display rounding yields zero.

`request_id` identifies the current request and must be fresh even on cache hits. Cached results retain original generated/retrieved times and never pretend to be newly fetched. Echo the current harmless display label rather than the label of another request sharing the same location cache key. `attribution_url` must be a backend-configured HTTPS source, never a provider-supplied arbitrary link.

## Source provenance (0.2)

One source supplies the whole baseline and analysis interval; values from different sources are never mixed. Only these combinations are valid; the backend rejects any other before responding:

| provider | model | grid_degrees (lat x lon) | First available year | attribution_url |
|---|---|---|---|---|
| `nasa_power` | `MERRA-2` | 0.5 x 0.625 | 1981 | `https://power.larc.nasa.gov/` |
| `open_meteo` | `ERA5` | 0.25 x 0.25 | 1940 | `https://open-meteo.com/` |

NASA POWER echoes the requested point rather than identifying a grid cell, so its `resolved` is always `null` and the response carries warning `RESOLVED_LOCATION_UNKNOWN`. Open-Meteo reports the grid-cell centre it used. `elevation_m` is the provider-reported elevation when present. A provider reporting a different source product, time standard or unit is rejected as PROVIDER_ERROR, not relabeled.

NASA POWER is preferred. Open-Meteo is used only when enabled for permitted non-commercial use, and then for the whole dataset: when the period starts before 1981 or after NASA fails. If no enabled source covers the period, the response is 422 UNSUPPORTED_PERIOD. A source switch changes the threshold and cache identity, and the UI shows the actual source. Values from different sources are not scientifically interchangeable even under the same method version.

Compatibility: 0.2 changes only the `source` object, `SamplePoint.resolved` nullability and `contract_version`; all metric, quality, event, error and method semantics are unchanged from 0.1. No 0.1 consumer was ever deployed, so no compatibility shim exists.

## Error schema and behavior

```typescript
type ErrorResponse = {
  error: {
    code: string; message: string; request_id: string;
    details: { field: string; message: string }[];
    retryable: boolean;
  };
};
```

| HTTP | Code | Meaning / UI recovery |
|---|---|---|
| 422 | VALIDATION_ERROR / UNSUPPORTED_PERIOD / UNSUPPORTED_REGION | Fix inputs or select supported range/region |
| 422 | INSUFFICIENT_BASELINE / INSUFFICIENT_DATA | Explain coverage issue; do not substitute example results |
| 429 | RATE_LIMITED | Respect integer-seconds Retry-After; explicit retry when eligible |
| 502 | PROVIDER_ERROR | Invalid/failed upstream response; preserve inputs, manual retry |
| 503 | STORAGE_UNAVAILABLE / CAPACITY_EXCEEDED | Database outage or bounded work capacity reached; retry later |
| 504 | UPSTREAM_TIMEOUT / ANALYSIS_TIMEOUT | Upstream/deadline exhausted; suggest narrower analysis and explicit retry |
| 500 | INTERNAL_ERROR | Generic message and request ID; no exception/secret disclosure |

413/415/404/405 use PAYLOAD_TOO_LARGE/UNSUPPORTED_MEDIA_TYPE/NOT_FOUND/METHOD_NOT_ALLOWED. Error details identify safe field paths, never rejected secret/raw payloads. CORS middleware must also cover error responses. Request ID is returned in `X-Request-ID`; expose it and `Retry-After` through CORS.

## Request lifecycle, caching and compatibility

Browser deadline 100 s; server total budget 90 s including storage and upstream attempts. Disable Analyze during an identical active submission. Use AbortController plus a monotonic request token; both success and error handlers must reject obsolete tokens. Changing any input cancels/hides the old request/result. Browser cancellation does not guarantee backend cancellation; the server still enforces its own budget and caps.

Use exact configured development/production origins; credentials are false. Production preferably proxies `/api` to a single origin. Do not put MongoDB URLs or provider secrets in frontend environment variables. Responses use `Cache-Control: no-store` for browser/intermediary storage; MongoDB result caching is internal.

Before implementing, create backend schema tests and matching frontend types/fixtures. Test null-vs-zero, partial years, backend validation and safe non-JSON failure handling. Additive response fields may be ignored by the frontend; breaking meanings/required fields require an explicit contract version change. Baseline, quality or algorithm changes also increment methodology and cache identity. No consumer recalculates threshold/trend locally.
