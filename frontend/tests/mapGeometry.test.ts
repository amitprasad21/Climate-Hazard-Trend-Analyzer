import { expect, it } from "vitest";
import type { AnalysisResponse } from "../src/api/types";
import {
  cornersToBox,
  draftShapes,
  mapBoxLabel,
  mapPointLabel,
  pickedPoint,
  resultShapes,
} from "../src/map/geometry";
import { syntheticResult } from "./fixtures";

function withSource(changes: Partial<AnalysisResponse["source"]>): AnalysisResponse {
  const base = syntheticResult();
  return { ...base, source: { ...base.source, ...changes } };
}

it("draws a grid cell only when the provider reported the grid point", () => {
  const nasa = resultShapes(syntheticResult());
  expect(nasa.requested).toEqual([[10.5, 20.25]]);
  expect(nasa.resolved).toEqual([]);
  expect(nasa.cells).toEqual([]);
  expect(nasa.box).toBeNull();

  const era5 = resultShapes(
    withSource({
      provider: "open_meteo",
      grid_degrees: { latitude: 0.25, longitude: 0.25 },
      sample_points: [{ requested: { latitude: 10.5, longitude: 20.25 }, resolved: { latitude: 10.5, longitude: 20.375 }, elevation_m: 5 }],
    }),
  );
  expect(era5.resolved).toEqual([[10.5, 20.375]]);
  expect(era5.cells).toEqual([[[10.375, 20.25], [10.625, 20.5]]]);
});

it("frames a point with room around it and a box by its own edges", () => {
  const point = resultShapes(syntheticResult());
  const [[south, west], [north, east]] = point.view;
  expect(south).toBeLessThan(10.5);
  expect(north).toBeGreaterThan(10.5);
  expect(west).toBeLessThan(20.25);
  expect(east).toBeGreaterThan(20.25);

  const samples = [27.5, 28, 28.5].flatMap((latitude) =>
    [77.25, 77.75, 78.25].map((longitude) => ({ requested: { latitude, longitude }, resolved: null, elevation_m: null })),
  );
  const box = resultShapes({
    ...withSource({ sample_points: samples }),
    region: { kind: "bbox", label: "Area", south: 27.25, west: 77, north: 28.75, east: 78.5 },
  });
  expect(box.box).toEqual([[27.25, 77], [28.75, 78.5]]);
  expect(box.view).toEqual(box.box);
  expect(box.requested).toHaveLength(9);
  expect(box.cells).toEqual([]);
});

it("turns a clicked position into a valid, rounded point", () => {
  expect(pickedPoint(28.613949, 77.209012)).toEqual({ latitude: "28.6139", longitude: "77.209" });
  expect(pickedPoint(10, 190)).toEqual({ latitude: "10", longitude: "-170" });
  expect(pickedPoint(10, -200)).toEqual({ latitude: "10", longitude: "160" });
  expect(pickedPoint(95, 0)).toEqual({ latitude: "90", longitude: "0" });
  expect(pickedPoint(-0.00001, -0.00001)).toEqual({ latitude: "0", longitude: "0" });
});

it("orders two clicked corners into a box in either drag direction", () => {
  const expected = { south: "28", west: "77", north: "29.5", east: "78.25" };
  expect(cornersToBox([29.5, 78.25], [28, 77])).toEqual(expected);
  expect(cornersToBox([28, 78.25], [29.5, 77])).toEqual(expected);
  expect(cornersToBox([89, 0], [86, 1])).toEqual({ south: "85", west: "0", north: "85", east: "1" });
});

it("labels map picks with their coordinates", () => {
  expect(mapPointLabel("28.6139", "-77.209")).toBe("Map point 28.6139° N, 77.2090° W");
  expect(mapBoxLabel({ south: "28", west: "77", north: "29", east: "78" })).toBe(
    "Map area 28.0000° N to 29.0000° N, 77.0000° E to 78.0000° E",
  );
});

it("draws typed coordinates only when they are usable", () => {
  const draft = { regionKind: "point" as const, latitude: "28.6", longitude: "77.2", south: "", west: "", north: "", east: "" };
  expect(draftShapes(draft)).toEqual({ point: [28.6, 77.2], box: null });
  expect(draftShapes({ ...draft, longitude: "abc" })).toEqual({ point: null, box: null });
  expect(draftShapes({ ...draft, latitude: "91" })).toEqual({ point: null, box: null });
  const box = { ...draft, regionKind: "bbox" as const, south: "28", west: "77", north: "29", east: "78" };
  expect(draftShapes(box)).toEqual({ point: null, box: [[28, 77], [29, 78]] });
  expect(draftShapes({ ...box, north: "" })).toEqual({ point: null, box: null });
});
