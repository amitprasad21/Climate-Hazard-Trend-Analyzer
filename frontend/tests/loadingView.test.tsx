import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { DashboardPage } from "../src/DashboardPage";

let serverAnswer: (() => void) | null;
const checkServer = vi.fn(
  () =>
    new Promise<void>((resolve) => {
      serverAnswer = resolve;
    }),
);

beforeEach(() => {
  serverAnswer = null;
  vi.useFakeTimers();
  vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(() => undefined)));
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

function startAnalysis() {
  for (const [label, value] of [
    ["Location name", "New Delhi"], ["Latitude", "28.6139"], ["Longitude", "77.209"],
    ["Start year", "1995"], ["End year", "2024"],
  ]) {
    fireEvent.change(screen.getByLabelText(label), { target: { value } });
  }
  fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
}

const results = () => screen.getByRole("region", { name: "Results" });

it("shows real stages, elapsed time and placeholders without numbers", async () => {
  render(<DashboardPage />);
  startAnalysis();
  const region = results();
  expect(region.getAttribute("aria-busy")).toBe("true");
  expect(within(region).getByText(/Analysis requested for New Delhi, 1995–2024/)).toBeTruthy();
  expect(within(region).getByText("0 s elapsed")).toBeTruthy();
  await act(async () => {
    vi.advanceTimersByTime(7000);
  });
  expect(within(region).getByText("7 s elapsed")).toBeTruthy();
  const placeholders = region.querySelector(".placeholder-grid");
  expect(placeholders?.getAttribute("aria-hidden")).toBe("true");
  expect(placeholders?.querySelectorAll(".placeholder-metric")).toHaveLength(4);
  expect(placeholders?.querySelectorAll(".placeholder-chart")).toHaveLength(3);
  expect(placeholders?.textContent).toBe("");
  expect(region.textContent).not.toMatch(/%/);
});

it("includes the server wake-up stage while the server is still waking", async () => {
  render(<DashboardPage checkServer={checkServer} />);
  await act(async () => {
    vi.advanceTimersByTime(2000);
  });
  startAnalysis();
  expect(within(results()).getByText(/Waking the analysis server/)).toBeTruthy();
  await act(async () => {
    serverAnswer?.();
  });
  expect(within(results()).getByText("Analysis server ready")).toBeTruthy();
});

it("explains a long wait after 45 seconds and keeps Cancel available", async () => {
  render(<DashboardPage />);
  startAnalysis();
  expect(within(results()).queryByText(/taking longer than usual/)).toBeNull();
  await act(async () => {
    vi.advanceTimersByTime(46_000);
  });
  expect(within(results()).getByText(/taking longer than usual/)).toBeTruthy();
  expect(screen.getByRole("button", { name: "Cancel" })).toBeTruthy();
});
