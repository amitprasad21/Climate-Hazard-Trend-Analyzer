// Wire types for INTEGRATION_CONTRACT.md version 0.2. The backend owns every value.

export type Period = { start_year: number; end_year: number };
export type Point = { latitude: number; longitude: number };
export type PointRegion = { kind: "point"; label: string; latitude: number; longitude: number };
export type BoxRegion = {
  kind: "bbox";
  label: string;
  south: number;
  west: number;
  north: number;
  east: number;
};
export type AnalysisRequest = {
  hazard: "heatwave";
  region: PointRegion | BoxRegion;
  period: Period;
};

export type RegionResult = {
  id: number;
  name: string;
  admin1: string | null;
  country: string;
  country_code: string;
  latitude: number;
  longitude: number;
};
export type RegionSearch = { results: RegionResult[] };

export type Coverage = {
  expected_days: number;
  valid_days: number;
  missing_days: number;
  invalid_days: number;
  duplicate_dates: number;
  coverage_fraction: number;
};
export type YearCoverage = Coverage & { year: number; eligible: boolean; excluded_reasons: string[] };
export type SamplePoint = { requested: Point; resolved: Point | null; elevation_m: number | null };
export type HeatwaveEvent = {
  start_date: string;
  end_date: string;
  duration_days: number;
  mean_excess_c: number;
  max_excess_c: number;
  boundary_censored: boolean;
};
export type Annual = {
  year: number;
  eligible: boolean;
  coverage_fraction: number;
  event_count: number | null;
  mean_duration_days: number | null;
  max_duration_days: number | null;
  heatwave_days: number | null;
  mean_tmax_c: number | null;
  tmax_anomaly_c: number | null;
  frequency_rolling_5y: number | null;
};
export type ResultWarning = { code: string; message: string; years: number[] };
export type Insight = {
  code: string;
  text: string;
  evidence: { metric: string; value: number; unit: string; years: number[] }[];
};
export type TrendDirection = "increasing" | "decreasing" | "flat" | "insufficient_data";

export type AnalysisResponse = {
  contract_version: "0.2";
  request_id: string;
  region: PointRegion | BoxRegion;
  period: Period;
  status: "complete" | "partial";
  summary: {
    event_count: number;
    mean_duration_days: number | null;
    threshold_c: number;
    trend_direction: TrendDirection;
    frequency_slope_per_year: number | null;
    trend_year_count: number;
  };
  annual: Annual[];
  events: HeatwaveEvent[];
  insights: Insight[];
  warnings: ResultWarning[];
  methodology: {
    version: "heatwave-v1";
    baseline_start: string;
    baseline_end: string;
    percentile: number;
    percentile_method: "linear";
    minimum_consecutive_days: number;
    comparison: "strictly_greater";
    daily_timezone: "UTC";
    aggregation: "point" | "nine_point_cosine_weighted_mean";
    anomaly_reference: string;
    trend_method: string;
    significance_tested: false;
  };
  data_quality: {
    baseline: Coverage;
    analysis: Coverage;
    years: YearCoverage[];
    eligible_year_count: number;
  };
  source: {
    provider: "nasa_power" | "open_meteo";
    model: "MERRA-2" | "ERA5";
    dataset_kind: "reanalysis";
    grid_degrees: { latitude: number; longitude: number };
    time_standard: "UTC";
    temperature_unit: "celsius";
    normalization_version: string;
    sample_points: SamplePoint[];
    attribution_url: string;
    retrieved_at: string;
  };
  cache: { hit: boolean; generated_at: string; expires_at: string };
};

export type ErrorDetail = { field: string; message: string };
export type ErrorResponse = {
  error: {
    code: string;
    message: string;
    request_id: string;
    details: ErrorDetail[];
    retryable: boolean;
  };
};
