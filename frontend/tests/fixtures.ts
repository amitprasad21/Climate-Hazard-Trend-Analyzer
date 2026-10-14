// Synthetic test fixtures only: never imported by src/ and never shown in production.
import type { AnalysisResponse, Annual } from "../src/api/types";

export function annualRow(year: number, overrides: Partial<Annual> = {}): Annual {
  return {
    year,
    eligible: true,
    coverage_fraction: 1,
    event_count: 2,
    mean_duration_days: 4,
    max_duration_days: 5,
    heatwave_days: 8,
    mean_tmax_c: 33.1,
    tmax_anomaly_c: 0.4,
    frequency_rolling_5y: null,
    ...overrides,
  };
}

export function syntheticResult(overrides: Partial<AnalysisResponse> = {}): AnalysisResponse {
  const annual = [2001, 2002, 2003].map((year) => annualRow(year));
  const coverage = {
    expected_days: 1095,
    valid_days: 1095,
    missing_days: 0,
    invalid_days: 0,
    duplicate_dates: 0,
    coverage_fraction: 1,
  };
  return {
    contract_version: "0.2",
    request_id: "synthetic-request",
    region: { kind: "point", label: "Synthetic Place", latitude: 10.5, longitude: 20.25 },
    period: { start_year: 2001, end_year: 2003 },
    status: "complete",
    summary: {
      event_count: 6,
      mean_duration_days: 4,
      threshold_c: 38.123,
      trend_direction: "insufficient_data",
      frequency_slope_per_year: null,
      trend_year_count: 3,
    },
    annual,
    events: [
      {
        start_date: "2001-05-01",
        end_date: "2001-05-04",
        duration_days: 4,
        mean_excess_c: 1.5,
        max_excess_c: 2.25,
        boundary_censored: false,
      },
    ],
    insights: [
      {
        code: "EVENT_TOTAL",
        text: "Synthetic insight sentence.",
        evidence: [{ metric: "event_count", value: 6, unit: "events", years: [2001] }],
      },
    ],
    warnings: [{ code: "UTC_CALENDAR_DAYS", message: "Synthetic warning sentence.", years: [] }],
    methodology: {
      version: "heatwave-v1",
      baseline_start: "1991-01-01",
      baseline_end: "2020-12-31",
      percentile: 95,
      percentile_method: "linear",
      minimum_consecutive_days: 3,
      comparison: "strictly_greater",
      daily_timezone: "UTC",
      aggregation: "point",
      anomaly_reference: "baseline_mean_daily_maximum",
      trend_method: "ordinary_least_squares_descriptive",
      significance_tested: false,
    },
    data_quality: {
      baseline: { ...coverage, expected_days: 10958, valid_days: 10958 },
      analysis: coverage,
      years: annual.map((row) => ({ ...coverage, expected_days: 365, valid_days: 365, year: row.year, eligible: true, excluded_reasons: [] })),
      eligible_year_count: 3,
    },
    source: {
      provider: "nasa_power",
      model: "MERRA-2",
      dataset_kind: "reanalysis",
      grid_degrees: { latitude: 0.5, longitude: 0.625 },
      time_standard: "UTC",
      temperature_unit: "celsius",
      normalization_version: "daily-tmax-v1",
      sample_points: [{ requested: { latitude: 10.5, longitude: 20.25 }, resolved: null, elevation_m: 120 }],
      attribution_url: "https://power.larc.nasa.gov/",
      retrieved_at: "2026-10-14T06:00:00Z",
    },
    cache: { hit: false, generated_at: "2026-10-14T06:00:05Z", expires_at: "2026-10-15T06:00:05Z" },
    ...overrides,
  };
}
