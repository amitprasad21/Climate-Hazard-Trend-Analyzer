import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import axe from "axe-core";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

vi.hoisted(() => {
  const proto = window.SVGSVGElement.prototype as unknown as { createSVGRect?: () => object };
  proto.createSVGRect ??= () => ({});
});

import { ResultsView } from "../src/components/ResultsView";
import { DashboardPage } from "../src/DashboardPage";
import { mapPointLabel, type MapShapes } from "../src/map/geometry";
import { MapPicker, ResultMap } from "../src/map/maps";
import { syntheticResult } from "./fixtures";

const maps = { ResultMap, MapPicker };
const value = (label: string) => (screen.getByLabelText(label) as HTMLInputElement).value;
const pickerMap = () => screen.getByRole("region", { name: "Map for choosing the location" });

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("fills the point from a map click and keeps only a label the user typed", () => {
  render(<DashboardPage maps={maps} />);
  // Leaflet rounds its pixel origin, so the zero-size map centre sits a fraction of a pixel from 20° N.
  fireEvent.click(pickerMap(), { clientX: 256, clientY: 0 });
  expect(Number(value("Latitude"))).toBeCloseTo(20, 0);
  expect(value("Longitude")).toBe("90");
  expect(value("Location name")).toBe(mapPointLabel(value("Latitude"), "90"));

  // A pick made on the map leaves the view alone, so the centre is still the starting one.
  fireEvent.click(screen.getByRole("button", { name: "Use map centre" }));
  expect(value("Longitude")).toBe("0");
  expect(value("Location name")).toBe(mapPointLabel(value("Latitude"), "0"));

  fireEvent.change(screen.getByLabelText("Location name"), { target: { value: "My farm" } });
  fireEvent.click(pickerMap(), { clientX: 256, clientY: 0 });
  expect(value("Longitude")).toBe("90");
  expect(value("Location name")).toBe("My farm");
});

it("fills a box from two corner clicks", () => {
  render(<DashboardPage maps={maps} />);
  fireEvent.click(screen.getByLabelText("Bounding box (area)"));
  fireEvent.click(pickerMap(), { clientX: 2, clientY: 0 });
  fireEvent.click(pickerMap(), { clientX: 0, clientY: 3 });
  expect(Number(value("West longitude"))).toBe(0);
  expect(Number(value("East longitude"))).toBeGreaterThan(0);
  expect(Number(value("North latitude"))).toBeCloseTo(20, 0);
  expect(Number(value("South latitude"))).toBeLessThan(20);
  expect(value("Region name")).toMatch(/^Map area /);
});

it("centres on a chosen city and renames it once the point is picked on the map", () => {
  const { container } = render(<DashboardPage maps={maps} />);
  expect(container.querySelectorAll(".map-picker path.map-requested")).toHaveLength(0);
  fireEvent.change(screen.getByLabelText("Location name"), { target: { value: "Typed before the city" } });
  fireEvent.click(screen.getByRole("button", { name: "New Delhi" }));
  expect(container.querySelectorAll(".map-picker path.map-requested")).toHaveLength(1);
  fireEvent.click(screen.getByRole("button", { name: "Use map centre" }));
  expect([value("Latitude"), value("Longitude")]).toEqual(["28.6139", "77.209"]);
  expect(value("Location name")).toBe(mapPointLabel("28.6139", "77.209"));
});

it("shows the analysed point on a result map and stays free of detectable violations", async () => {
  vi.mocked(fetch).mockResolvedValueOnce(
    new Response(JSON.stringify(syntheticResult()), { status: 200, headers: { "Content-Type": "application/json" } }),
  );
  render(<DashboardPage maps={maps} />);
  fireEvent.click(screen.getByRole("button", { name: "New Delhi" }));
  fireEvent.change(screen.getByLabelText("Start year"), { target: { value: "2001" } });
  fireEvent.change(screen.getByLabelText("End year"), { target: { value: "2003" } });
  await act(async () => {
    fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
  });
  const region = screen.getByRole("region", { name: "Map of Synthetic Place" });
  expect(region.querySelectorAll("path.map-requested")).toHaveLength(1);
  const legend = document.querySelector(".map-legend") as HTMLElement;
  expect(within(legend).getByText("Requested point")).toBeTruthy();
  expect(within(legend).queryByText(/reported by the provider/)).toBeNull();
  const report = await axe.run(document.body, { rules: { "color-contrast": { enabled: false } } });
  expect(report.violations.map((v) => v.id)).toEqual([]);
});

it("keeps the result map's shapes stable while years are hovered", () => {
  const seen = new Set<MapShapes>();
  const SpyMap = ({ shapes }: { shapes: MapShapes }) => {
    seen.add(shapes);
    return null;
  };
  const { container } = render(<ResultsView result={syntheticResult()} ResultMap={SpyMap} />);
  for (const row of container.querySelectorAll(".calendar-row")) fireEvent.pointerEnter(row);
  expect(container.querySelectorAll(".row-active")).toHaveLength(1);
  expect(seen.size).toBe(1);
});
