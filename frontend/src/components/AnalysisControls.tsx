import { useState, type FormEvent, type KeyboardEvent, type RefObject } from "react";
import type { RegionResult } from "../api/types";
import { EARLIEST_YEAR, MAX_YEARS, type Draft, type DraftField, type FieldErrors } from "../form";
import type { SearchState } from "../hooks/useRegionSearch";

type Props = {
  draft: Draft;
  errors: FieldErrors;
  latestYear: number;
  pending: boolean;
  search: SearchState;
  fieldRefs: Record<DraftField, RefObject<HTMLInputElement | null>>;
  onChange: (field: DraftField, value: string) => void;
  onSearch: (query: string) => void;
  onSelectPlace: (place: RegionResult) => void;
  onSubmit: () => void;
  onCancel: () => void;
};

export function placeLabel(place: RegionResult): string {
  return [place.name, place.admin1, place.country].filter(Boolean).join(", ").slice(0, 120);
}

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
  const { draft, errors, latestYear, pending, search, fieldRefs, onChange, onSearch, onSelectPlace } = props;
  const [query, setQuery] = useState("");

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
          </div>
          <SearchResults search={search} onSelect={onSelectPlace} />
          {text("label", "label", "Location name", { type: "text", maxLength: 120, autoComplete: "off" })}
          <div className="field-row">
            {text("latitude", "latitude", "Latitude", { type: "number", inputMode: "decimal", min: -90, max: 90, step: "any" }, "−90 to 90")}
            {text("longitude", "longitude", "Longitude", { type: "number", inputMode: "decimal", min: -180, max: 180, step: "any" }, "−180 to 180")}
          </div>
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
            {text("startYear", "start_year", "Start year", { type: "number", inputMode: "numeric", min: EARLIEST_YEAR, max: latestYear, step: 1 })}
            {text("endYear", "end_year", "End year", { type: "number", inputMode: "numeric", min: EARLIEST_YEAR, max: latestYear, step: 1 })}
          </div>
          <span id="period-hint" className="hint">
            Full calendar years from {EARLIEST_YEAR} to {latestYear}, up to {MAX_YEARS} years.
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
