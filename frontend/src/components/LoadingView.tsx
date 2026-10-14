import { useEffect, useState } from "react";
import type { AnalysisRequest } from "../api/types";
import type { ServerStatus } from "../hooks/useServerStatus";

export const LONG_WAIT_SECONDS = 45;

function useElapsedSeconds(): number {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const started = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - started) / 1000)), 1000);
    return () => clearInterval(timer);
  }, []);
  return elapsed;
}

function serverStage(status: ServerStatus): string | null {
  switch (status) {
    case "waking":
      return "Waking the analysis server (free hosting pauses it when idle)…";
    case "ready":
      return "Analysis server ready";
    case "unreachable":
      return "The server did not answer the wake-up check; the analysis request is still being tried";
    default:
      return null;
  }
}

export function LoadingView({ request, serverStatus }: { request: AnalysisRequest; serverStatus: ServerStatus }) {
  const elapsed = useElapsedSeconds();
  const server = serverStage(serverStatus);
  const { region, period } = request;
  return (
    <div className="loading-view">
      <ol className="loading-stages">
        {server && (
          <li aria-current={serverStatus === "waking" ? "step" : undefined}>{server}</li>
        )}
        <li aria-current={serverStatus === "waking" ? undefined : "step"}>
          Analysis requested for {region.label}, {period.start_year}–{period.end_year}. A new location means
          fetching and storing decades of daily temperatures before the analysis runs.{" "}
          <span className="elapsed">{elapsed} s elapsed</span>
        </li>
        <li>Results appear here as soon as the analysis finishes.</li>
      </ol>
      {elapsed >= LONG_WAIT_SECONDS && (
        <p className="notice">
          This is taking longer than usual: the server may still be waking up or the data provider is slow. You can
          keep waiting or cancel.
        </p>
      )}
      <div className="placeholder-grid" aria-hidden="true">
        <div className="placeholder-metrics">
          {[0, 1, 2, 3].map((index) => (
            <div key={index} className="placeholder-metric" />
          ))}
        </div>
        <div className="placeholder-chart placeholder-chart-wide" />
        <div className="placeholder-chart" />
        <div className="placeholder-chart" />
      </div>
    </div>
  );
}
