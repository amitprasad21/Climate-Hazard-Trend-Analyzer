import { useState, type FormEvent, type KeyboardEvent, type ReactNode, type RefObject } from "react";
import type { RegionResult } from "../api/types";
import { MAX_YEARS, type Draft, type DraftField, type FieldErrors } from "../form";
import type { SearchState } from "../hooks/useRegionSearch";

type Props = {
  draft: Draft;
  errors: FieldErrors;
  latestYear: number;
  earliestYear: number;
  pending: boolean;
  search: SearchState;
  fieldRefs: Record<DraftField, RefObject<HTMLInputElement | null>>;
  onChange: (field: DraftField, value: string) => void;
  onUpdate?: (changes: Partial<Draft>) => void;
  onSearch: (query: string) => void;
  onSelectPlace: (place: RegionResult) => void;
  onSubmit: () => void;
  onCancel: () => void;
  map?: ReactNode;
};

export function placeLabel(place: RegionResult): string {
  return [place.name, place.admin1, place.country].filter(Boolean).join(", ").slice(0, 120);
}

export const QUICK_CITIES = [
  { short: "New Delhi", name: "New Delhi, National Capital Territory of Delhi, India", lat: 28.6139, lon: 77.209 },
  { short: "Phoenix", name: "Phoenix, Arizona, United States", lat: 33.4484, lon: -112.074 },
  { short: "London", name: "London, England, United Kingdom", lat: 51.5074, lon: -0.1278 },
  { short: "Tokyo", name: "Tokyo, Japan", lat: 35.6762, lon: 139.6503 },
  { short: "Athens", name: "Athens, Attica, Greece", lat: 37.9838, lon: 23.7275 },
];

function FieldError({ id, message }: { id: string; message?: string }) {
  if (!message) return null;
  return (
    <p id={id} className="field-error">
      <span aria-hidden="true">! </span>
      {message}
    </p>
  );
}

function describedBy(...ids: (string | false | undefined)[]) {
  return ids.filter(Boolean).join(" ") || undefined;
}

function SearchResults({ search, onSelect }: { search: SearchState; onSelect: (p: RegionResult) => void }) {
  if (search.phase === "loading") return <p className="search-status">Searching for “{search.query}”…</p>;
  if (search.phase === "error") {
    const message =
      search.error.code === "SEARCH_UNAVAILABLE"
        ? "Place search is not enabled on this server. Enter the name and coordinates below."
        : `Search failed: ${search.error.message} Try again or enter coordinates below.`;
    return <p className="search-status">{message}</p>;
  }
  if (search.phase !== "done") return null;
  if (search.results.length === 0) {
    return <p className="search-status">No places matched “{search.query}”. Check the spelling or enter coordinates.</p>;
  }
  return (
    <fieldset className="search-results">
      <legend>Choose a place ({search.results.length})</legend>
      {search.results.map((place) => (
        <label key={place.id} className="choice">
          <input type="radio" name="place_result" value={place.id} onChange={() => onSelect(place)} />
          <span>
            {placeLabel(place)}
            <span className="choice-detail">
              {" "}
              ({place.latitude.toFixed(4)}, {place.longitude.toFixed(4)})
            </span>
          </span>
        </label>
      ))}
    </fieldset>
  );
}

export function AnalysisControls(props: Props) {
  const { draft, errors, latestYear, earliestYear, pending, search, fieldRefs, onChange, onUpdate, onSearch, onSelectPlace } = props;
  const [query, setQuery] = useState("");

  const yearPresets = [
    { label: "Last 10y", start: Math.max(earliestYear, latestYear - 9), end: latestYear },
    { label: "Last 20y", start: Math.max(earliestYear, latestYear - 19), end: latestYear },
    { label: "Last 30y", start: Math.max(earliestYear, latestYear - 29), end: latestYear },
    { label: "Baseline (1991–2020)", start: 1991, end: 2020 },
    { label: "Full record", start: Math.max(earliestYear, latestYear - MAX_YEARS + 1), end: latestYear },
  ];

  function runSearch() {
    if (query.trim().length >= 2) onSearch(query.trim());
  }

  function handleSearchKey(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      event.preventDefault();
      runSearch();
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    props.onSubmit();
  }

  const text = (field: DraftField, id: string, label: string, extra: object, hint?: string) => (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        ref={fieldRefs[field]}
        id={id}
        name={id}
        value={draft[field]}
        onChange={(event) => onChange(field, event.target.value)}
        aria-invalid={errors[field] ? true : undefined}
        aria-describedby={describedBy(hint && `${id}-hint`, errors[field] && `${id}-error`)}
        {...extra}
      />
      {hint && (
        <span id={`${id}-hint`} className="hint">
          {hint}
        </span>
      )}
      <FieldError id={`${id}-error`} message={errors[field]} />
    </div>
  );

  return (
    <form className="controls" onSubmit={handleSubmit} noValidate>
      <div className="field-groups">
        <fieldset>
          <legend>Location</legend>
          <div className="field">
            <span id="region-kind-label" className="field-label">Region type</span>
            <div className="choice-row" role="radiogroup" aria-labelledby="region-kind-label">
              <label className="choice">
                <input
                  type="radio"
                  name="region_kind"
                  value="point"
                  checked={draft.regionKind === "point"}
                  onChange={() => onChange("regionKind", "point")}
                />
                <span>Single point</span>
              </label>
              <label className="choice">
                <input
                  type="radio"
                  name="region_kind"
                  value="bbox"
                  checked={draft.regionKind === "bbox"}
                  onChange={() => onChange("regionKind", "bbox")}
                />
                <span>Bounding box (area)</span>
              </label>
            </div>
          </div>

          {draft.regionKind === "point" ? (
            <>
              <div className="field">
                <label htmlFor="place_query">Search for a place</label>
                <div className="search-row">
                  <input
                    id="place_query"
                    name="place_query"
                    type="search"
                    value={query}
                    maxLength={100}
                    autoComplete="off"
                    onChange={(event) => setQuery(event.target.value)}
                    onKeyDown={handleSearchKey}
                  />
                  <button type="button" className="secondary-action" onClick={runSearch}>
                    Search
                  </button>
                </div>
                <div className="preset-group" role="group" aria-label="Sample global cities">
                  {QUICK_CITIES.map((city) => {
                    const isSelected =
                      draft.label === city.name &&
                      draft.latitude === String(city.lat) &&
                      draft.longitude === String(city.lon);
                    return (
                      <button
                        key={city.name}
                        type="button"
                        className={`chip-btn ${isSelected ? "active" : ""}`}
                        aria-pressed={isSelected}
                        onClick={() => {
                          if (onUpdate) {
                            onUpdate({
                              label: city.name,
                              latitude: String(city.lat),
                              longitude: String(city.lon),
                            });
                          } else {
                            onChange("label", city.name);
                            onChange("latitude", String(city.lat));
                            onChange("longitude", String(city.lon));
                          }
                        }}
                      >
                        {city.short}
                      </button>
                    );
                  })}
                </div>
              </div>
              <SearchResults search={search} onSelect={onSelectPlace} />
              {text("label", "label", "Location name", { type: "text", maxLength: 120, autoComplete: "off" })}
              <div className="field-row">
                {text("latitude", "latitude", "Latitude", { type: "number", inputMode: "decimal", min: -90, max: 90, step: "any" }, "−90 to 90")}
                {text("longitude", "longitude", "Longitude", { type: "number", inputMode: "decimal", min: -180, max: 180, step: "any" }, "−180 to 180")}
              </div>
            </>
          ) : (
            <>
              {text("label", "label", "Region name", { type: "text", maxLength: 120, autoComplete: "off" })}
              <div className="field-row">
                {text("south", "south", "South latitude", { type: "number", inputMode: "decimal", min: -85, max: 85, step: "any" }, "−85 to 85")}
                {text("north", "north", "North latitude", { type: "number", inputMode: "decimal", min: -85, max: 85, step: "any" }, "−85 to 85, span ≤ 2.0°")}
              </div>
              <div className="field-row">
                {text("west", "west", "West longitude", { type: "number", inputMode: "decimal", min: -180, max: 180, step: "any" }, "−180 to 180")}
                {text("east", "east", "East longitude", { type: "number", inputMode: "decimal", min: -180, max: 180, step: "any" }, "−180 to 180, span ≤ 2.0°")}
              </div>
              <span id="bbox-hint" className="hint">
                Sampled using 9 cell centers (3×3 grid) with cosine-latitude weighting. Maximum 2.0° span.
              </span>
            </>
          )}
          {props.map}
        </fieldset>

        <fieldset>
          <legend>Hazard and period</legend>
          <div className="field">
            <label htmlFor="hazard">Hazard</label>
            <select id="hazard" name="hazard" defaultValue="heatwave">
              <option value="heatwave">Heatwave</option>
            </select>
          </div>
          <div className="field-row">
            {text("startYear", "start_year", "Start year", { type: "number", inputMode: "numeric", min: earliestYear, max: latestYear, step: 1 })}
            {text("endYear", "end_year", "End year", { type: "number", inputMode: "numeric", min: earliestYear, max: latestYear, step: 1 })}
          </div>
          <div className="preset-group" role="group" aria-label="Quick year presets">
            {yearPresets.map((preset) => {
              const isActive = draft.startYear === String(preset.start) && draft.endYear === String(preset.end);
              return (
                <button
                  key={preset.label}
                  type="button"
                  className={`chip-btn ${isActive ? "active" : ""}`}
                  aria-pressed={isActive}
                  onClick={() => {
                    if (onUpdate) {
                      onUpdate({ startYear: String(preset.start), endYear: String(preset.end) });
                    } else {
                      onChange("startYear", String(preset.start));
                      onChange("endYear", String(preset.end));
                    }
                  }}
                >
                  {preset.label}
                </button>
              );
            })}
          </div>
          <span id="period-hint" className="hint">
            Full calendar years from {earliestYear} to {latestYear}, up to {MAX_YEARS} years.
          </span>
        </fieldset>
      </div>

      <div className="actions">
        <button className="primary-action" type="submit" disabled={pending}>
          {pending ? "Analyzing…" : "Analyze trends"}
        </button>
        {pending && (
          <button type="button" className="secondary-action" onClick={props.onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
