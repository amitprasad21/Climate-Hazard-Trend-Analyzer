import { Suspense, useMemo, useRef, useState } from "react";
import type { RegionResult } from "./api/types";
import { AnalysisControls, placeLabel } from "./components/AnalysisControls";
import { ErrorPanel } from "./components/ErrorPanel";
import { LoadingView } from "./components/LoadingView";
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
import { cornersToBox, draftShapes, mapBoxLabel, mapPointLabel, pickedPoint, type LatLon } from "./map/geometry";
import type { MapComponents } from "./map/types";
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

export function DashboardPage({ checkServer, maps }: { checkServer?: HealthCheck; maps?: MapComponents } = {}) {
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [dirty, setDirty] = useState(false);
  const [labelTyped, setLabelTyped] = useState(false);
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
    setLabelTyped(false);
    update({
      label: placeLabel(place),
      latitude: String(place.latitude),
      longitude: String(place.longitude),
    });
  }

  // A map pick keeps a label the user typed; names from search, city buttons or earlier picks no longer fit.
  const keepLabel = labelTyped && draft.label.trim() !== "";

  function pickPoint(latitude: number, longitude: number) {
    const point = pickedPoint(latitude, longitude);
    update({ ...point, ...(!keepLabel && { label: mapPointLabel(point.latitude, point.longitude) }) });
  }

  function pickBox(first: LatLon, second: LatLon) {
    const box = cornersToBox(first, second);
    update({ ...box, ...(!keepLabel && { label: mapBoxLabel(box) }) });
  }

  const drafted = useMemo(() => draftShapes(draft), [draft]);

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
            onChange={(field, value) => {
              if (field === "label") setLabelTyped(true);
              update({ [field]: value });
            }}
            onUpdate={(changes) => {
              if ("label" in changes) setLabelTyped(false);
              update(changes);
            }}
            onSearch={(query) => void search.run(query)}
            onSelectPlace={selectPlace}
            onSubmit={submit}
            onCancel={analysis.cancel}
            map={
              maps && (
                <Suspense fallback={<div className="leaflet-map map-loading" aria-hidden="true" />}>
                  <maps.MapPicker
                    mode={draft.regionKind}
                    point={drafted.point}
                    box={drafted.box}
                    onPickPoint={pickPoint}
                    onPickBox={pickBox}
                  />
                </Suspense>
              )
            }
          />
          <p className="form-notice" role="status">
            {statusMessage(state, dirty)}
          </p>
        </section>

        <section className="panel" aria-labelledby="results-heading" aria-busy={state.phase === "loading"}>
          <h2 id="results-heading">Results</h2>
          {state.phase === "success" && (
            <ResultsView result={state.result} savedInBrowser={state.savedInBrowser} ResultMap={maps?.ResultMap} />
          )}
          {state.phase === "error" && <ErrorPanel error={state.error} onRetry={retry} />}
          {state.phase === "loading" && <LoadingView request={state.request} serverStatus={server.status} />}
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
