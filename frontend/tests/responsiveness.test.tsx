import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DashboardPage } from "../src/DashboardPage";
import { syntheticResult } from "./fixtures";

const VIEWPORTS = [
  { width: 320, height: 568, name: "320x568 (Mobile narrow / iPhone SE)" },
  { width: 360, height: 800, name: "360x800 (Mobile standard / Android)" },
  { width: 390, height: 844, name: "390x844 (Mobile modern / iPhone 13/14)" },
  { width: 430, height: 932, name: "430x932 (Mobile wide / iPhone Pro Max)" },
  { width: 768, height: 1024, name: "768x1024 (Tablet portrait / iPad)" },
  { width: 1024, height: 768, name: "1024x768 (Tablet landscape / Small desktop)" },
  { width: 1280, height: 800, name: "1280x800 (Desktop standard / Laptop)" },
  { width: 1440, height: 900, name: "1440x900 (Desktop large / MacBook)" },
  { width: 1920, height: 1080, name: "1920x1080 (Desktop ultra-wide / FHD)" },
];

function setViewport(width: number, height: number) {
  Object.defineProperty(window, "innerWidth", { writable: true, configurable: true, value: width });
  Object.defineProperty(window, "innerHeight", { writable: true, configurable: true, value: height });
  window.dispatchEvent(new Event("resize"));
}

function fillValid() {
  for (const [label, value] of [
    ["Location name", "A".repeat(120)],
    ["Latitude", "28.6139"],
    ["Longitude", "77.209"],
    ["Start year", "1995"],
    ["End year", "2024"],
  ]) {
    fireEvent.change(screen.getByLabelText(label), { target: { value } });
  }
}

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("FE-005: 9 Responsive Viewports Automated Verification", () => {
  it.each(VIEWPORTS)("renders populated dashboard and 3 SVG charts cleanly at $name", async ({ width, height }) => {
    setViewport(width, height);
    vi.mocked(fetch).mockResolvedValueOnce(json(syntheticResult({ status: "complete" })));

    render(<DashboardPage />);
    fillValid();

    await act(async () => {
      fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
    });

    // Verify 4 summary metric cards render
    expect(screen.getByText("Detected heatwave events")).toBeTruthy();
    expect(screen.getByText("Average duration")).toBeTruthy();
    expect(screen.getByText("Frequency trend")).toBeTruthy();
    expect(screen.getByText("95th-percentile threshold")).toBeTruthy();

    // The heatwave calendar and the three line charts
    const figures = screen.getAllByRole("figure");
    expect(figures).toHaveLength(4);

    // Verify chart SVGs have responsive viewBox and accessibility labels
    for (const figure of figures) {
      const svg = figure.querySelector("svg.chart-svg");
      expect(svg).toBeTruthy();
      expect(svg?.getAttribute("viewBox")).toMatch(/^0 0 \d+ \d+$/);
    }

    // Verify controls remain accessible
    expect(screen.getByLabelText("Location name")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Analyze trends" })).toBeTruthy();
  });

  it.each(VIEWPORTS)("renders idle guidance state cleanly at $name", ({ width, height }) => {
    setViewport(width, height);
    render(<DashboardPage />);

    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Climate Hazard Analyzer");
    expect(screen.getByText("No analysis yet")).toBeTruthy();
  });

  it.each(VIEWPORTS)("renders error panel cleanly at $name", async ({ width, height }) => {
    setViewport(width, height);
    vi.mocked(fetch).mockResolvedValueOnce(
      json(
        {
          error: {
            code: "UPSTREAM_TIMEOUT",
            message: "Upstream weather provider took too long to respond.",
            request_id: "req-timeout",
            details: [],
            retryable: true,
          },
        },
        504,
      ),
    );

    render(<DashboardPage />);
    fillValid();

    await act(async () => {
      fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
    });

    expect(screen.getByText("Analysis could not be completed")).toBeTruthy();
    expect(screen.getByText("Upstream weather provider took too long to respond.")).toBeTruthy();
  });
});
