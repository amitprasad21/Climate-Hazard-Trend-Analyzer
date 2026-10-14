import type { ReactNode } from "react";
import type { AnalysisResponse, TrendDirection } from "../api/types";
import {
  PROVIDER_NAMES,
  formatCoordinate,
  formatDate,
  formatNumber,
  formatPercent,
  formatSigned,
  formatTimestamp,
} from "../format";
import { LineChart } from "./LineChart";

const TRENDS: Record<TrendDirection, { symbol: string; text: string; badgeClass: string }> = {
  increasing: { symbol: "↗", text: "Increasing", badgeClass: "trend-increasing" },
  decreasing: { symbol: "↘", text: "Decreasing", badgeClass: "trend-decreasing" },
  flat: { symbol: "→", text: "No linear change", badgeClass: "trend-flat" },
  insufficient_data: { symbol: "—", text: "Not estimated", badgeClass: "trend-insufficient" },
};

function Metric({ label, value, unit, note }: { label: string; value: ReactNode; unit?: string; note: string }) {
  return (
    <li className="metric">
      <p className="metric-label">{label}</p>
      <div className="metric-value">
        {value}
        {unit && typeof value === "string" && value !== "—" && <span className="metric-unit"> {unit}</span>}
      </div>
      <p className="metric-note">{note}</p>
    </li>
  );
}

function Metrics({ result }: { result: AnalysisResponse }) {
  const { summary, period } = result;
  const trend = TRENDS[summary.trend_direction];
  const eligible = summary.trend_year_count;
  return (
    <ul className="metrics" aria-label="Summary metrics">
      <Metric
        label="Detected heatwave events"
        value={formatNumber(summary.event_count, 0)}
        note={`Started in ${period.start_year}–${period.end_year}, across ${eligible} eligible years`}
      />
      <Metric
        label="Average duration"
        value={formatNumber(summary.mean_duration_days, 1)}
        unit="days"
        note={summary.mean_duration_days === null ? "No events, so no duration" : "Mean over all events"}
      />
      <Metric
        label="Frequency trend"
        value={
          <span className={`trend-badge ${trend.badgeClass}`}>
            <span className="trend-arrow" aria-hidden="true">{trend.symbol}</span>
            <span>{trend.text}</span>
          </span>
        }
        note={
          summary.frequency_slope_per_year === null
            ? `Needs at least 10 eligible years (${eligible} available)`
            : `${formatSigned(summary.frequency_slope_per_year, 3)} events per year, descriptive fit only`
        }
      />
      <Metric
        label="95th-percentile threshold"
        value={formatNumber(summary.threshold_c, 1)}
        unit="°C"
        note="Daily maximum, 1991–2020 baseline at this location"
      />
    </ul>
  );
}

function Charts({ result }: { result: AnalysisResponse }) {
  const years = result.annual.map((row) => row.year);
  return (
    <div className="charts">
      <div className="chart-primary">
        <LineChart
          title="Annual heatwave frequency"
          description="Events starting each year. Gaps mark years excluded for missing data."
          years={years}
          unit="events"
          digits={1}
          integerAxis
          series={[
            { label: "Events per year", values: result.annual.map((r) => r.event_count), variant: "primary" },
            { label: "5-year rolling mean", values: result.annual.map((r) => r.frequency_rolling_5y), variant: "secondary" },
          ]}
        />
      </div>
      <LineChart
        title="Average heatwave duration"
        description="Mean observed days of events starting each year; years without events have no value."
        years={years}
        unit="days"
        series={[
          { label: "Mean duration", values: result.annual.map((r) => r.mean_duration_days), variant: "primary" },
          { label: "Longest event", values: result.annual.map((r) => r.max_duration_days), variant: "secondary" },
        ]}
      />
      <LineChart
        title="Daily maximum temperature anomaly"
        description="Annual mean daily maximum minus the 1991–2020 mean daily maximum at this location."
        years={years}
        unit="°C"
        digits={2}
        zeroLine
        series={[{ label: "Anomaly", values: result.annual.map((r) => r.tmax_anomaly_c), variant: "primary" }]}
      />
    </div>
  );
}

function RegionContext({ result }: { result: AnalysisResponse }) {
  const { source, region } = result;

  if (region.kind === "bbox") {
    return (
      <section className="subpanel" aria-labelledby="region-heading">
        <h3 id="region-heading">Region and data source</h3>
        <dl className="facts">
          <dt>Bounding box</dt>
          <dd>
            {formatCoordinate(region.south, "lat")} to {formatCoordinate(region.north, "lat")},{" "}
            {formatCoordinate(region.west, "lon")} to {formatCoordinate(region.east, "lon")}
          </dd>
          <dt>Spatial aggregation</dt>
          <dd>3×3 grid (9 cell centers), cosine-latitude weighted mean</dd>
          <dt>Sample points</dt>
          <dd>{source.sample_points.length} points sampled across regional cells</dd>
          <dt>Source</dt>
          <dd>
            {PROVIDER_NAMES[source.provider]} · {source.model} reanalysis, {source.grid_degrees.latitude}° ×{" "}
            {source.grid_degrees.longitude}° grid
          </dd>
        </dl>
        <p className="muted">
          The regional series is a 3×3 cosine-weighted mean of daily maxima. No station or grid-cell heatmap is
          implied.
        </p>
      </section>
    );
  }

  const point = source.sample_points[0];
  return (
    <section className="subpanel" aria-labelledby="region-heading">
      <h3 id="region-heading">Location and data source</h3>
      <dl className="facts">
        <dt>Requested point</dt>
        <dd>
          {formatCoordinate(point.requested.latitude, "lat")}, {formatCoordinate(point.requested.longitude, "lon")}
        </dd>
        <dt>Grid cell used</dt>
        <dd>
          {point.resolved
            ? `${formatCoordinate(point.resolved.latitude, "lat")}, ${formatCoordinate(point.resolved.longitude, "lon")}`
            : "Not reported by the provider"}
        </dd>
        <dt>Source</dt>
        <dd>
          {PROVIDER_NAMES[source.provider]} · {source.model} reanalysis, {source.grid_degrees.latitude}° ×{" "}
          {source.grid_degrees.longitude}° grid
        </dd>
        {point.elevation_m !== null && (
          <>
            <dt>Elevation</dt>
            <dd>{formatNumber(point.elevation_m, 0)} m</dd>
          </>
        )}
      </dl>
      <p className="muted">
        The analysis uses one reanalysis grid cell, so there is no spatial heat-intensity map; it does not describe
        every neighbourhood.
      </p>
    </section>
  );
}

function Quality({ result }: { result: AnalysisResponse }) {
  const { data_quality: quality } = result;
  const excluded = quality.years.filter((y) => !y.eligible).map((y) => y.year);
  return (
    <section className="subpanel" aria-labelledby="quality-heading">
      <h3 id="quality-heading">Data quality</h3>
      <dl className="facts">
        <dt>Baseline coverage</dt>
        <dd>{formatPercent(quality.baseline.coverage_fraction)} of 1991–2020 days valid</dd>
        <dt>Analysis coverage</dt>
        <dd>{formatPercent(quality.analysis.coverage_fraction)} of requested days valid</dd>
        <dt>Eligible years</dt>
        <dd>
          {quality.eligible_year_count} of {quality.years.length}
          {excluded.length > 0 && ` (excluded: ${excluded.join(", ")})`}
        </dd>
      </dl>
    </section>
  );
}

function Findings({ result }: { result: AnalysisResponse }) {
  return (
    <div className="findings">
      <section className="subpanel" aria-labelledby="insights-heading">
        <h3 id="insights-heading">Key insights</h3>
        <ul className="insights">
          {result.insights.map((insight) => (
            <li key={insight.code}>{insight.text}</li>
          ))}
        </ul>
      </section>
      <section className="subpanel" aria-labelledby="notes-heading">
        <h3 id="notes-heading">Limitations and notes</h3>
        <ul className="notes">
          {result.warnings.map((warning) => (
            <li key={warning.code}>
              {warning.message}
              {warning.years.length > 0 && ` (${warning.years.join(", ")})`}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function exportEventsCsv(result: AnalysisResponse) {
  const rows = [
    ["Start Date", "End Date", "Duration (days)", "Mean Excess (°C)", "Peak Excess (°C)", "Boundary Censored"],
    ...result.events.map((e) => [
      e.start_date,
      e.end_date,
      String(e.duration_days),
      e.mean_excess_c !== null ? String(e.mean_excess_c) : "",
      e.max_excess_c !== null ? String(e.max_excess_c) : "",
      e.boundary_censored ? "true" : "false",
    ]),
  ];
  const csvContent = rows.map((r) => r.map((c) => `"${c.replace(/"/g, '""')}"`).join(",")).join("\r\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const safeName = result.region.label.replace(/[^a-zA-Z0-9_-]/g, "_");
  link.setAttribute("href", url);
  link.setAttribute("download", `heatwaves_${safeName}_${result.period.start_year}_${result.period.end_year}.csv`);
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function Events({ result }: { result: AnalysisResponse }) {
  if (result.events.length === 0) return null;
  return (
    <details className="data-table events">
      <summary>Show all {result.events.length} events</summary>
      <div className="table-toolbar">
        <button
          type="button"
          className="secondary-action"
          onClick={() => exportEventsCsv(result)}
        >
          Export CSV
        </button>
      </div>
      <table>
        <caption className="visually-hidden">Heatwave events</caption>
        <thead>
          <tr>
            <th scope="col">Start</th>
            <th scope="col">End</th>
            <th scope="col">Days</th>
            <th scope="col">Mean excess (°C)</th>
            <th scope="col">Peak excess (°C)</th>
          </tr>
        </thead>
        <tbody>
          {result.events.map((event) => (
            <tr key={event.start_date}>
              <td>{formatDate(event.start_date)}</td>
              <td>{formatDate(event.end_date)}</td>
              <td>
                {event.duration_days}
                {event.boundary_censored && " (cut off by period edge)"}
              </td>
              <td>{formatNumber(event.mean_excess_c, 2)}</td>
              <td>{formatNumber(event.max_excess_c, 2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  );
}

function Method({ result }: { result: AnalysisResponse }) {
  const { methodology: method, source, cache, summary } = result;
  return (
    <section className="method" aria-labelledby="method-heading">
      <h3 id="method-heading">Method and provenance</h3>
      <p>
        A heatwave is {method.minimum_consecutive_days} or more consecutive UTC days whose daily maximum is strictly
        above the {method.percentile}th percentile ({formatNumber(summary.threshold_c, 3)} °C, linear interpolation)
        of {method.baseline_start.slice(0, 4)}–{method.baseline_end.slice(0, 4)} daily maxima. Trends are ordinary
        least squares on eligible annual counts and are descriptive; no significance test was applied.
      </p>
      <p>
        Data from{" "}
        <a href={source.attribution_url} target="_blank" rel="noopener noreferrer">
          {PROVIDER_NAMES[source.provider]}
        </a>{" "}
        ({source.model}), retrieved {formatTimestamp(source.retrieved_at)}. Result {cache.hit ? "served from the cache, " : ""}
        generated {formatTimestamp(cache.generated_at)}.
      </p>
    </section>
  );
}

export function ResultsView({ result }: { result: AnalysisResponse }) {
  return (
    <div className="results-body">
      <p className="result-context">
        <strong>{result.region.label}</strong> · {result.period.start_year}–{result.period.end_year} · Heatwave
      </p>
      {result.status === "partial" && (
        <p className="notice" role="note">
          <strong>Partial data.</strong> Some days or years are missing or cut off; see the notes below.
        </p>
      )}
      <Metrics result={result} />
      <Charts result={result} />
      <div className="details-grid">
        <RegionContext result={result} />
        <Quality result={result} />
      </div>
      <Findings result={result} />
      <Events result={result} />
      <Method result={result} />
    </div>
  );
}
