import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { analyzeHeatwaves } from "../src/api/client";
import type { AnalysisRequest, AnalysisResponse } from "../src/api/types";
import { ResultsView } from "../src/components/ResultsView";
import { syntheticResult } from "./fixtures";

const REQUEST: AnalysisRequest = {
  hazard: "heatwave",
  region: { kind: "point", label: "Place", latitude: 10.5, longitude: 20.25 },
  period: { start_year: 2001, end_year: 2003 },
};
const json = (body: unknown) => new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });

function tested(significant: boolean, p: number, sens: number): AnalysisResponse {
  const base = syntheticResult();
  return {
    ...base,
    summary: {
      ...base.summary,
      trend_direction: significant ? "increasing" : "no_significant_trend",
      frequency_slope_per_year: 0.012,
      mann_kendall: { s: 45, tau: 1, z: 3.9, p_value: p, sens_slope_per_year: sens, significant },
      trend_year_count: 12,
    },
  };
}

// The previous contract: no test result, descriptive OLS method.
function contract02(): Record<string, unknown> {
  const { mann_kendall: _omitted, ...summary } = syntheticResult().summary;
  void _omitted;
  return {
    ...syntheticResult(),
    contract_version: "0.2",
    summary: { ...summary, trend_direction: "flat", frequency_slope_per_year: 0, trend_year_count: 12 },
    methodology: {
      ...syntheticResult().methodology,
      version: "heatwave-v1",
      trend_method: "ordinary_least_squares_descriptive",
      significance_tested: false,
    },
  };
}

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const card = () => screen.getByText("Frequency trend").closest("li") as HTMLElement;

it("accepts contract 0.3 and, during a rolling deployment, 0.2 without a test result", async () => {
  vi.mocked(fetch).mockResolvedValueOnce(json(tested(true, 0.0004, 1)));
  const current = await analyzeHeatwaves(REQUEST, new AbortController().signal);
  expect(current.summary.mann_kendall?.significant).toBe(true);

  vi.mocked(fetch).mockResolvedValueOnce(json(contract02()));
  const previous = await analyzeHeatwaves(REQUEST, new AbortController().signal);
  expect(previous.summary.mann_kendall).toBeNull();

  vi.mocked(fetch).mockResolvedValueOnce(json({ ...tested(true, 0.0004, 1), contract_version: "0.4" }));
  await expect(analyzeHeatwaves(REQUEST, new AbortController().signal)).rejects.toBeTruthy();
});

it("shows a significant trend with its p-value and Sen's slope", () => {
  render(<ResultsView result={tested(true, 0.0004, 1)} />);
  expect(within(card()).getByText("Increasing")).toBeTruthy();
  expect(within(card()).getByText("Mann-Kendall p < 0.001; Sen's slope +1.000 events per year")).toBeTruthy();
});

it("calls a non-significant result no clear trend instead of naming a direction", () => {
  render(<ResultsView result={tested(false, 0.42, 0.01)} />);
  expect(within(card()).getByText("No clear trend")).toBeTruthy();
  expect(within(card()).getByText("Mann-Kendall p = 0.420 (not significant at 5%); Sen's slope +0.010 events per year")).toBeTruthy();
});

it("explains the test in the method text, and keeps the old wording for 0.2 results", () => {
  render(<ResultsView result={tested(false, 0.42, 0.01)} />);
  const method = screen.getByRole("region", { name: "Method and provenance" });
  expect(within(method).getByText(/two-sided Mann-Kendall test/)).toBeTruthy();
  expect(within(method).getByText(/assumes independent years/)).toBeTruthy();
  cleanup();

  render(<ResultsView result={{ ...(contract02() as unknown as AnalysisResponse), summary: { ...(contract02().summary as AnalysisResponse["summary"]), mann_kendall: null } }} />);
  expect(within(card()).getByText("No linear change")).toBeTruthy();
  const old = screen.getByRole("region", { name: "Method and provenance" });
  expect(within(old).getByText(/no significance test was applied/)).toBeTruthy();
});
