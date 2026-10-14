import type { AnalysisRequest } from "./api/types";

export type Draft = {
  label: string;
  latitude: string;
  longitude: string;
  startYear: string;
  endYear: string;
};
export type DraftField = keyof Draft;
export type FieldErrors = Partial<Record<DraftField, string>>;

export const EARLIEST_YEAR = 1940;
export const MAX_YEARS = 50;
export const FIELD_ORDER: DraftField[] = ["label", "latitude", "longitude", "startYear", "endYear"];
export const EMPTY_DRAFT: Draft = { label: "", latitude: "", longitude: "", startYear: "", endYear: "" };

// Mirrors the backend rule as guidance: the latest year whose 31 December is 7+ days in the past.
export function latestCompleteYear(now: Date): number {
  const available = new Date(now.getTime() - 7 * 86_400_000);
  const year = available.getUTCFullYear();
  return available.getUTCMonth() === 11 && available.getUTCDate() === 31 ? year : year - 1;
}

const CONTROL_CHARACTERS = /\p{Cc}/u;

function coordinate(value: string, limit: number, name: string): [number | null, string | null] {
  const text = value.trim();
  if (!text) return [null, `Enter a ${name}.`];
  const number = Number(text);
  if (!Number.isFinite(number)) return [null, `${name[0].toUpperCase()}${name.slice(1)} must be a number.`];
  if (Math.abs(number) > limit) return [null, `Use a ${name} between −${limit} and ${limit}.`];
  return [number, null];
}

function year(value: string, name: string): [number | null, string | null] {
  const text = value.trim();
  if (!text) return [null, `Enter a ${name}.`];
  if (!/^\d{4}$/.test(text)) return [null, `Enter a four-digit ${name}.`];
  return [Number(text), null];
}

export function validate(
  draft: Draft,
  now: Date,
): { errors: FieldErrors; request: AnalysisRequest | null } {
  const errors: FieldErrors = {};
  const label = draft.label.trim();
  if (!label) errors.label = "Enter a location name or choose a search result.";
  else if (label.length > 120) errors.label = "Use 120 characters or fewer.";
  else if (CONTROL_CHARACTERS.test(label)) errors.label = "Remove control characters.";

  const [latitude, latitudeError] = coordinate(draft.latitude, 90, "latitude");
  const [longitude, longitudeError] = coordinate(draft.longitude, 180, "longitude");
  if (latitudeError) errors.latitude = latitudeError;
  if (longitudeError) errors.longitude = longitudeError;

  const latest = latestCompleteYear(now);
  const [start, startError] = year(draft.startYear, "start year");
  const [end, endError] = year(draft.endYear, "end year");
  if (startError) errors.startYear = startError;
  else if (start !== null && start < EARLIEST_YEAR) errors.startYear = `Start in ${EARLIEST_YEAR} or later.`;
  if (endError) errors.endYear = endError;
  else if (end !== null && end > latest) errors.endYear = `The latest complete year is ${latest}.`;
  if (start !== null && end !== null && !errors.startYear && !errors.endYear) {
    if (start > end) errors.endYear = "End year must not be before the start year.";
    else if (end - start + 1 > MAX_YEARS) errors.endYear = `Choose at most ${MAX_YEARS} years.`;
  }

  if (Object.keys(errors).length || latitude === null || longitude === null || start === null || end === null) {
    return { errors, request: null };
  }
  return {
    errors,
    request: {
      hazard: "heatwave",
      region: { kind: "point", label, latitude, longitude },
      period: { start_year: start, end_year: end },
    },
  };
}
