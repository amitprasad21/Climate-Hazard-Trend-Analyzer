import type { AnalysisResponse } from "../api/types";
import type { Draft } from "../form";
import { formatCoordinate } from "../format";

export type LatLon = [number, number];
export type Bounds = [LatLon, LatLon];

export type MapShapes = {
  requested: LatLon[];
  resolved: LatLon[];
  cells: Bounds[];
  box: Bounds | null;
  view: Bounds;
};

const POINT_VIEW_PADDING = 0.6;
const BOX_LATITUDE_LIMIT = 85;

export function resultShapes(result: AnalysisResponse): MapShapes {
  const { region, source } = result;
  const requested = source.sample_points.map((p): LatLon => [p.requested.latitude, p.requested.longitude]);
  const resolved = source.sample_points
    .map((p) => p.resolved)
    .filter((p) => p !== null)
    .map((p): LatLon => [p.latitude, p.longitude]);
  if (region.kind === "bbox") {
    const box: Bounds = [[region.south, region.west], [region.north, region.east]];
    return { requested, resolved, cells: [], box, view: box };
  }
  const half = { lat: source.grid_degrees.latitude / 2, lon: source.grid_degrees.longitude / 2 };
  const cells = resolved.map(([lat, lon]): Bounds => [[lat - half.lat, lon - half.lon], [lat + half.lat, lon + half.lon]]);
  const { latitude, longitude } = region;
  const view: Bounds = [
    [latitude - POINT_VIEW_PADDING, longitude - POINT_VIEW_PADDING],
    [latitude + POINT_VIEW_PADDING, longitude + POINT_VIEW_PADDING],
  ];
  return { requested, resolved, cells, box: null, view };
}

const round = (value: number) => String(Math.round(value * 1e4) / 1e4 || 0);
const wrapLongitude = (value: number) => ((((value + 180) % 360) + 360) % 360) - 180;
const clamp = (value: number, limit: number) => Math.max(-limit, Math.min(limit, value));

export function pickedPoint(latitude: number, longitude: number): { latitude: string; longitude: string } {
  return { latitude: round(clamp(latitude, 90)), longitude: round(wrapLongitude(longitude)) };
}

export function cornersToBox(a: LatLon, b: LatLon): { south: string; west: string; north: string; east: string } {
  const [lat1, lat2] = [clamp(a[0], BOX_LATITUDE_LIMIT), clamp(b[0], BOX_LATITUDE_LIMIT)];
  const [lon1, lon2] = [wrapLongitude(a[1]), wrapLongitude(b[1])];
  return {
    south: round(Math.min(lat1, lat2)),
    west: round(Math.min(lon1, lon2)),
    north: round(Math.max(lat1, lat2)),
    east: round(Math.max(lon1, lon2)),
  };
}

export function mapPointLabel(latitude: string, longitude: string): string {
  return `Map point ${formatCoordinate(Number(latitude), "lat")}, ${formatCoordinate(Number(longitude), "lon")}`;
}

export function mapBoxLabel(box: { south: string; west: string; north: string; east: string }): string {
  const [south, west, north, east] = [box.south, box.west, box.north, box.east].map(Number);
  return `Map area ${formatCoordinate(south, "lat")} to ${formatCoordinate(north, "lat")}, ${formatCoordinate(
    west,
    "lon",
  )} to ${formatCoordinate(east, "lon")}`;
}

function parse(value: string, limit: number): number | null {
  if (value.trim() === "") return null;
  const number = Number(value);
  return Number.isFinite(number) && Math.abs(number) <= limit ? number : null;
}

type DraftCoordinates = Pick<Draft, "regionKind" | "latitude" | "longitude" | "south" | "west" | "north" | "east">;

export function draftShapes(draft: DraftCoordinates): { point: LatLon | null; box: Bounds | null } {
  if (draft.regionKind === "point") {
    const latitude = parse(draft.latitude, 90);
    const longitude = parse(draft.longitude, 180);
    return { point: latitude !== null && longitude !== null ? [latitude, longitude] : null, box: null };
  }
  const edges = [parse(draft.south, 90), parse(draft.west, 180), parse(draft.north, 90), parse(draft.east, 180)];
  if (edges.some((edge) => edge === null)) return { point: null, box: null };
  const [south, west, north, east] = edges as number[];
  return { point: null, box: [[south, west], [north, east]] };
}
