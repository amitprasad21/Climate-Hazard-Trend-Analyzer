import type { AnalysisRequest } from "./api/types";

export type RegionKind = "point" | "bbox";

export type Draft = {
  regionKind: RegionKind;
  label: string;
  latitude: string;
  longitude: string;
  south: string;
  west: string;
  north: string;
  east: string;
  startYear: string;
  endYear: string;
};
export type DraftField = keyof Draft;
export type FieldErrors = Partial<Record<DraftField, string>>;

export const EARLIEST_YEAR = 1940;
export const MAX_YEARS = 50;
export const MAX_BBOX_SPAN = 2.0;

export const FIELD_ORDER: DraftField[] = [
  "regionKind",
  "label",
  "latitude",
  "longitude",
  "south",
  "west",
  "north",
  "east",
  "startYear",
  "endYear",
];

export const EMPTY_DRAFT: Draft = {
  regionKind: "point",
  label: "",
  latitude: "",
  longitude: "",
  south: "",
  west: "",
  north: "",
  east: "",
  startYear: "",
  endYear: "",
};

// Mirrors the backend rule as guidance: the latest year whose 31 December is 7+ days in the past.
export function latestCompleteYear(now: Date): number {
  const available = new Date(now.getTime() - 7 * 86_400_000);
  const year = available.getUTCFullYear();
  return available.getUTCMonth() === 11 && available.getUTCDate() === 31 ? year : year - 1;
}

// The server reports which start years its enabled sources can serve; anything else keeps the outer bound.
export function startYearFloor(reported: number | null, latest: number): number {
  return reported !== null && reported >= EARLIEST_YEAR && reported <= latest ? reported : EARLIEST_YEAR;
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
  earliest = EARLIEST_YEAR,
): { errors: FieldErrors; request: AnalysisRequest | null } {
  const errors: FieldErrors = {};
  const label = draft.label.trim();
  if (!label) errors.label = "Enter a location name or choose a search result.";
  else if (label.length > 120) errors.label = "Use 120 characters or fewer.";
  else if (CONTROL_CHARACTERS.test(label)) errors.label = "Remove control characters.";

  let pointCoords: { latitude: number; longitude: number } | null = null;
  let boxCoords: { south: number; west: number; north: number; east: number } | null = null;

  if (draft.regionKind === "point") {
    const [latitude, latitudeError] = coordinate(draft.latitude, 90, "latitude");
    const [longitude, longitudeError] = coordinate(draft.longitude, 180, "longitude");
    if (latitudeError) errors.latitude = latitudeError;
    if (longitudeError) errors.longitude = longitudeError;
    if (latitude !== null && longitude !== null) {
      pointCoords = { latitude, longitude };
    }
  } else {
    const [south, southError] = coordinate(draft.south, 85, "south latitude");
    const [north, northError] = coordinate(draft.north, 85, "north latitude");
    const [west, westError] = coordinate(draft.west, 180, "west longitude");
    const [east, eastError] = coordinate(draft.east, 180, "east longitude");

    if (southError) errors.south = southError;
    if (northError) errors.north = northError;
    if (westError) errors.west = westError;
    if (eastError) errors.east = eastError;

    if (south !== null && north !== null && !errors.south && !errors.north) {
      if (south >= north) {
        errors.north = "North latitude must be greater than south latitude.";
      } else if (north - south > MAX_BBOX_SPAN) {
        errors.north = `Latitude span must be at most ${MAX_BBOX_SPAN}°.`;
      }
    }

    if (west !== null && east !== null && !errors.west && !errors.east) {
      if (west >= east) {
        errors.east = "East longitude must be greater than west longitude.";
      } else if (east - west > MAX_BBOX_SPAN) {
        errors.east = `Longitude span must be at most ${MAX_BBOX_SPAN}°.`;
      }
    }

    if (
      south !== null &&
      north !== null &&
      west !== null &&
      east !== null &&
      !errors.south &&
      !errors.north &&
      !errors.west &&
      !errors.east
    ) {
      boxCoords = { south, west, north, east };
    }
  }

  const latest = latestCompleteYear(now);
  const [start, startError] = year(draft.startYear, "start year");
  const [end, endError] = year(draft.endYear, "end year");
  if (startError) errors.startYear = startError;
  else if (start !== null && start < earliest) {
    errors.startYear = `Start in ${earliest} or later, when the data available here begins.`;
  }
  if (endError) errors.endYear = endError;
  else if (end !== null && end > latest) errors.endYear = `The latest complete year is ${latest}.`;
  if (start !== null && end !== null && !errors.startYear && !errors.endYear) {
    if (start > end) errors.endYear = "End year must not be before the start year.";
    else if (end - start + 1 > MAX_YEARS) errors.endYear = `Choose at most ${MAX_YEARS} years.`;
  }

  const hasRegion = draft.regionKind === "point" ? pointCoords !== null : boxCoords !== null;
  if (Object.keys(errors).length || !hasRegion || start === null || end === null) {
    return { errors, request: null };
  }

  const region =
    draft.regionKind === "point"
      ? ({ kind: "point", label, latitude: pointCoords!.latitude, longitude: pointCoords!.longitude } as const)
      : ({ kind: "bbox", label, ...boxCoords! } as const);

  return {
    errors,
    request: {
      hazard: "heatwave",
      region,
      period: { start_year: start, end_year: end },
    },
  };
}
