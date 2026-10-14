import { useRef, useState } from "react";
import type { RegionResult } from "./api/types";
import { AnalysisControls, placeLabel } from "./components/AnalysisControls";
import { ErrorPanel } from "./components/ErrorPanel";
import { ResultsView } from "./components/ResultsView";
import {
  EMPTY_DRAFT,
  FIELD_ORDER,
  latestCompleteYear,
  validate,
  type Draft,
  type DraftField,
  type FieldErrors,
} from "./form";
import { useAnalysis, type AnalysisState } from "./hooks/useAnalysis";
import { useRegionSearch } from "./hooks/useRegionSearch";
import { serverStatusMessage, useServerStatus, type HealthCheck } from "./hooks/useServerStatus";

function statusMessage(state: AnalysisState, dirty: boolean): string {
  switch (state.phase) {
    case "loading": {
      const { region, period } = state.request;
      return `Analyzing historical weather for ${region.label}, ${period.start_year}–${period.end_year}. A new location can take up to a minute.`;
    }
    case "success": {
      const { summary, period } = state.result;
      const reused = state.savedInBrowser ? " (saved result, no new request)" : "";
      return `Analysis complete: ${summary.event_count} heatwave events in ${period.start_year}–${period.end_year}${reused}.`;
    }
    case "error":
      return `Analysis failed: ${state.error.message}`;
    default:
      return dirty ? "Settings changed. Run the analysis again to update the results." : "";
  }
}

export function DashboardPage({ checkServer }: { checkServer?: HealthCheck } = {}) {
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [dirty, setDirty] = useState(false);
  const analysis = useAnalysis();
  const search = useRegionSearch();
  const server = useServerStatus(checkServer);
  const latestYear = latestCompleteYear(new Date());
  const fieldRefs = {
    regionKind: useRef<HTMLInputElement>(null),
    label: useRef<HTMLInputElement>(null),
    latitude: useRef<HTMLInputElement>(null),
    longitude: useRef<HTMLInputElement>(null),
    south: useRef<HTMLInputElement>(null),
    west: useRef<HTMLInputElement>(null),
    north: useRef<HTMLInputElement>(null),
    east: useRef<HTMLInputElement>(null),
    startYear: useRef<HTMLInputElement>(null),
    endYear: useRef<HTMLInputElement>(null),
  };

  function invalidateResult() {
    if (analysis.state.phase !== "idle") {
      analysis.cancel();
      setDirty(true);
    }
  }

  function update(changes: Partial<Draft>) {
    setDraft((current) => ({ ...current, ...changes }));
    setErrors((current) => {
      const next = { ...current };
      for (const field of Object.keys(changes) as DraftField[]) delete next[field];
      return next;
    });
    invalidateResult();
  }

  function selectPlace(place: RegionResult) {
    update({
      label: placeLabel(place),
      latitude: String(place.latitude),
      longitude: String(place.longitude),
    });
  }

  function submit() {
    const { errors: found, request } = validate(draft, new Date());
    setErrors(found);
    if (!request) {
      const first = FIELD_ORDER.find((field) => found[field]);
      if (first) fieldRefs[first].current?.focus();
      return;
    }
    setDirty(false);
    void analysis.submit(request);
  }

  function retry() {
    if (analysis.state.phase !== "error") return;
    const request = analysis.state.request;
    analysis.cancel();
    void analysis.submit(request);
  }

  const { state } = analysis;
  return (
    <div className="page">
      <header className="page-header">
        <h1>Climate Hazard Analyzer</h1>
        <p className="subtitle">
          Historical heatwave trends for a chosen location, calculated from reanalysis data.
        </p>
        <p className="server-status" aria-live="polite">
          {serverStatusMessage(server.status, server.wasSlow)}
        </p>
      </header>

      <main className="dashboard">
        <section className="panel" aria-labelledby="settings-heading">
          <h2 id="settings-heading">Analysis settings</h2>
          <AnalysisControls
            draft={draft}
            errors={errors}
            latestYear={latestYear}
            pending={state.phase === "loading"}
            search={search.state}
            fieldRefs={fieldRefs}
            onChange={(field, value) => update({ [field]: value })}
            onUpdate={update}
            onSearch={(query) => void search.run(query)}
            onSelectPlace={selectPlace}
            onSubmit={submit}
            onCancel={analysis.cancel}
          />
          <p className="form-notice" role="status">
            {statusMessage(state, dirty)}
          </p>
        </section>

        <section className="panel" aria-labelledby="results-heading" aria-busy={state.phase === "loading"}>
          <h2 id="results-heading">Results</h2>
          {state.phase === "success" && (
            <ResultsView result={state.result} savedInBrowser={state.savedInBrowser} />
          )}
          {state.phase === "error" && <ErrorPanel error={state.error} onRetry={retry} />}
          {state.phase === "loading" && (
            <p className="empty-state">Fetching and analysing daily maxima. Results appear here when ready.</p>
          )}
          {state.phase === "idle" && (
            <div className="empty-state">
              <p className="empty-title">{dirty ? "Settings changed" : "No analysis yet"}</p>
              <p>
                Choose a location and period, then select Analyze trends. A heatwave is three or more consecutive
                days with a daily maximum temperature above that location's 1991–2020 95th percentile.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
