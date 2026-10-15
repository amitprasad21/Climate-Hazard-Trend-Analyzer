import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";

// jsdom lacks createSVGRect, so Leaflet would otherwise fall back to an unavailable canvas renderer.
vi.hoisted(() => {
  const proto = window.SVGSVGElement.prototype as unknown as { createSVGRect?: () => object };
  proto.createSVGRect ??= () => ({});
});

import { resultShapes } from "../src/map/geometry";
import { MapPicker, ResultMap } from "../src/map/maps";
import { syntheticResult } from "./fixtures";

afterEach(cleanup);

const noop = () => undefined;

function mapElement(container: HTMLElement, name: string) {
  return container.querySelector(`[aria-label="${name}"]`) as HTMLElement;
}

it("draws the requested point and a reported grid cell over OpenStreetMap tiles with the credit", () => {
  const base = syntheticResult();
  const shapes = resultShapes({
    ...base,
    source: {
      ...base.source,
      provider: "open_meteo",
      grid_degrees: { latitude: 0.25, longitude: 0.25 },
      sample_points: [{ requested: { latitude: 10.5, longitude: 20.25 }, resolved: { latitude: 10.5, longitude: 20.375 }, elevation_m: 5 }],
    },
  });
  const { container } = render(<ResultMap shapes={shapes} label="Synthetic Place" />);
  expect(screen.getByRole("region", { name: "Map of Synthetic Place" })).toBeTruthy();
  expect(container.querySelectorAll("path.map-requested")).toHaveLength(1);
  expect(container.querySelectorAll("path.map-resolved")).toHaveLength(1);
  expect(container.querySelectorAll("path.map-cell")).toHaveLength(1);
  expect(container.querySelector(".leaflet-tile-pane")).toBeTruthy();
  const credit = container.querySelector(".leaflet-control-attribution")?.textContent ?? "";
  expect(credit).toMatch(/© OpenStreetMap contributors/);
  expect(container.querySelector(".leaflet-tile")?.getAttribute("src")).toMatch(/^https:\/\/tile\.openstreetmap\.org\//);
  expect(container.querySelector(".leaflet-control-attribution svg")).toBeNull();
});

it("draws no cell when the provider did not report one", () => {
  const { container } = render(<ResultMap shapes={resultShapes(syntheticResult())} label="Synthetic Place" />);
  expect(container.querySelectorAll("path.map-requested")).toHaveLength(1);
  expect(container.querySelectorAll("path.map-cell, path.map-resolved")).toHaveLength(0);
});

it("sets a point from a map click or from the map centre", () => {
  const picks: number[][] = [];
  const { container } = render(
    <MapPicker mode="point" point={null} box={null} onPickPoint={(lat, lon) => picks.push([lat, lon])} onPickBox={noop} />,
  );
  const map = mapElement(container, "Map for choosing the location");
  // A zero-size jsdom map puts its centre (20° N, 0°) at the origin; 256 px is a quarter turn east at zoom 2.
  fireEvent.click(map, { clientX: 256, clientY: 0 });
  fireEvent.click(screen.getByRole("button", { name: "Use map centre" }));
  expect(picks.map(([lat, lon]) => [Math.round(lat), Math.round(lon)])).toEqual([[20, 90], [20, 0]]);
});

it("builds a box from two corner clicks and resets when the mode changes", () => {
  const boxes: number[][][] = [];
  const props = { point: null, box: null, onPickPoint: noop, onPickBox: (a: number[], b: number[]) => boxes.push([a, b]) };
  const { container, rerender } = render(<MapPicker mode="bbox" {...props} />);
  const map = mapElement(container, "Map for choosing the location");
  expect(screen.queryByRole("button", { name: "Use map centre" })).toBeNull();
  fireEvent.click(map, { clientX: 0, clientY: 0 });
  expect(screen.getByText("Now click the opposite corner of the box.")).toBeTruthy();
  expect(container.querySelectorAll("path.map-anchor")).toHaveLength(1);
  fireEvent.click(map, { clientX: 256, clientY: 0 });
  expect(boxes.map((pair) => pair.map(([lat, lon]) => [Math.round(lat), Math.round(lon)]))).toEqual([[[20, 0], [20, 90]]]);
  expect(container.querySelectorAll("path.map-anchor")).toHaveLength(0);

  fireEvent.click(map, { clientX: 0, clientY: 0 });
  rerender(<MapPicker mode="point" {...props} />);
  rerender(<MapPicker mode="bbox" {...props} />);
  expect(container.querySelectorAll("path.map-anchor")).toHaveLength(0);
});

it("shows typed coordinates on the map", async () => {
  const { container, rerender } = render(<MapPicker mode="point" point={null} box={null} onPickPoint={noop} onPickBox={noop} />);
  expect(container.querySelectorAll("path.map-requested")).toHaveLength(0);
  await act(async () => {
    rerender(<MapPicker mode="point" point={[28.6, 77.2]} box={null} onPickPoint={noop} onPickBox={noop} />);
  });
  expect(container.querySelectorAll("path.map-requested")).toHaveLength(1);
  await act(async () => {
    rerender(<MapPicker mode="bbox" point={null} box={[[28, 77], [29, 78]]} onPickPoint={noop} onPickBox={noop} />);
  });
  expect(container.querySelectorAll("path.map-requested")).toHaveLength(0);
  expect(container.querySelectorAll("path.map-box")).toHaveLength(1);
});
