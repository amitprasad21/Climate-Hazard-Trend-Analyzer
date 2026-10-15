import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { checkHealth } from "../src/api/client";
import { DashboardPage } from "../src/DashboardPage";
import { EMPTY_DRAFT, latestCompleteYear, startYearFloor, validate } from "../src/form";

const NOW = new Date("2026-10-15T00:00:00Z");
const json = (body: unknown) => new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("reads the server's earliest start year and ignores a missing or malformed one", async () => {
  const health = (body: object) => {
    vi.mocked(fetch).mockResolvedValueOnce(json({ status: "ok", api_version: "v1", ...body }));
    return checkHealth(new AbortController().signal);
  };
  expect(await health({ earliest_start_year: 1981 })).toEqual({ earliestStartYear: 1981 });
  expect(await health({})).toEqual({ earliestStartYear: null });
  expect(await health({ earliest_start_year: "1981" })).toEqual({ earliestStartYear: null });
  expect(await health({ earliest_start_year: 1981.5 })).toEqual({ earliestStartYear: null });
});

it("uses a reported year only when it lies inside the outer bounds", () => {
  expect(startYearFloor(1981, 2025)).toBe(1981);
  expect(startYearFloor(null, 2025)).toBe(1940);
  expect(startYearFloor(1930, 2025)).toBe(1940);
  expect(startYearFloor(2026, 2025)).toBe(1940);
});

it("refuses a start year before the server's first year with a message naming it", () => {
  const draft = { ...EMPTY_DRAFT, label: "Place", latitude: "10", longitude: "20", startYear: "1980", endYear: "1990" };
  expect(validate(draft, NOW, 1981).errors.startYear).toBe("Start in 1981 or later, when the data available here begins.");
  expect(validate({ ...draft, startYear: "1981" }, NOW, 1981).request).not.toBeNull();
  expect(validate({ ...draft, startYear: "1980" }, NOW).request).not.toBeNull();
});

it("follows the server's first year in the hint, presets and validation without sending a request", async () => {
  const latest = latestCompleteYear(new Date());
  render(<DashboardPage checkServer={async () => ({ earliestStartYear: 1981 })} />);
  await act(async () => undefined);
  expect(screen.getByText(`Full calendar years from 1981 to ${latest}, up to 50 years.`)).toBeTruthy();
  expect(screen.getByLabelText("Start year").getAttribute("min")).toBe("1981");

  fireEvent.click(screen.getByRole("button", { name: "Full record" }));
  expect((screen.getByLabelText("Start year") as HTMLInputElement).value).toBe(String(Math.max(1981, latest - 49)));

  fireEvent.click(screen.getByRole("button", { name: "New Delhi" }));
  fireEvent.change(screen.getByLabelText("Start year"), { target: { value: "1980" } });
  fireEvent.change(screen.getByLabelText("End year"), { target: { value: "1990" } });
  fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
  expect(screen.getByText("Start in 1981 or later, when the data available here begins.")).toBeTruthy();
  expect(fetch).not.toHaveBeenCalled();
});

it("keeps the 1940 outer bound until the server reports otherwise", () => {
  render(<DashboardPage />);
  expect(screen.getByLabelText("Start year").getAttribute("min")).toBe("1940");
});
