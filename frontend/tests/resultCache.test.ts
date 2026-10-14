import { expect, it } from "vitest";
import type { AnalysisRequest } from "../src/api/types";
import { ResultCache, cacheKey } from "../src/resultCache";
import { syntheticResult } from "./fixtures";

const NOW = Date.parse("2026-10-14T06:00:00Z");

function point(label = "Place", latitude = 28.6139, start = 2001): AnalysisRequest {
  return {
    hazard: "heatwave",
    region: { kind: "point", label, latitude, longitude: 77.209 },
    period: { start_year: start, end_year: 2003 },
  };
}

function box(label = "Area"): AnalysisRequest {
  return {
    hazard: "heatwave",
    region: { kind: "bbox", label, south: 28, west: 77, north: 29, east: 78 },
    period: { start_year: 2001, end_year: 2003 },
  };
}

const fresh = (hours = 1) =>
  syntheticResult({
    cache: {
      hit: false,
      generated_at: "2026-10-14T05:00:00Z",
      expires_at: new Date(NOW + hours * 3_600_000).toISOString(),
    },
  });

it("keys on the exact science inputs and ignores the display label", () => {
  expect(cacheKey(point("A"))).toBe(cacheKey(point("B")));
  expect(cacheKey(point("A", 28.6139))).not.toBe(cacheKey(point("A", 28.61391)));
  expect(cacheKey(point("A", 28.6139, 2001))).not.toBe(cacheKey(point("A", 28.6139, 2002)));
  const east = point("A");
  if (east.region.kind === "point") east.region.longitude = 77.2091;
  expect(cacheKey(east)).not.toBe(cacheKey(point("A")));
  for (const edge of ["south", "west", "north", "east"] as const) {
    const moved = box("A");
    if (moved.region.kind === "bbox") moved.region[edge] += 0.5;
    expect(cacheKey(moved)).not.toBe(cacheKey(box("A")));
  }
  expect(cacheKey(box("A"))).toBe(cacheKey(box("B")));
  expect(cacheKey(box())).not.toBe(cacheKey(point()));
});

it("returns a relabelled copy and leaves the stored result untouched", () => {
  const cache = new ResultCache();
  const stored = fresh();
  cache.set(point("First"), stored);
  const hit = cache.get(point("Second"), NOW);
  expect(hit?.region.label).toBe("Second");
  expect(stored.region.label).toBe("Synthetic Place");
});

it("never serves a result past the backend's expiry", () => {
  const cache = new ResultCache();
  cache.set(point(), fresh(1));
  expect(cache.get(point(), NOW + 59 * 60_000)).not.toBeNull();
  expect(cache.get(point(), NOW + 60 * 60_000)).toBeNull();
  expect(cache.size).toBe(0);
});

it("keeps at most the configured number of results, evicting the least recently used", () => {
  const cache = new ResultCache(3);
  for (const start of [2001, 2002, 2003]) cache.set(point("P", 28.6139, start), fresh());
  expect(cache.get(point("P", 28.6139, 2001), NOW)).not.toBeNull();
  cache.set(point("P", 28.6139, 2000), fresh());
  expect(cache.size).toBe(3);
  expect(cache.get(point("P", 28.6139, 2002), NOW)).toBeNull();
  expect(cache.get(point("P", 28.6139, 2001), NOW)).not.toBeNull();
});
