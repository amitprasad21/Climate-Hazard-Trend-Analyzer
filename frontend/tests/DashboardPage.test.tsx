import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { DashboardPage } from "../src/DashboardPage";
import { syntheticResult } from "./fixtures";

type Deferred = { resolve: (response: Response) => void; reject: (error: unknown) => void };

const json = (body: unknown, status = 200, headers: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", ...headers } });

const failure = (code: string, retryable: boolean) => ({
  error: { code, message: `Synthetic ${code} message.`, request_id: "req-err", details: [], retryable },
});

let fetchMock: ReturnType<typeof vi.fn>;
let pending: Deferred[];

beforeEach(() => {
  pending = [];
  fetchMock = vi.fn(
    (_url: string, init?: RequestInit) =>
      new Promise<Response>((resolve, reject) => {
        pending.push({ resolve, reject });
        init?.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
      }),
  );
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function fill(label: string, value: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}

function fillValid() {
  fill("Location name", "  New Delhi ");
  fill("Latitude", "28.6139");
  fill("Longitude", "77.209");
  fill("Start year", "2001");
  fill("End year", "2003");
}

function submit() {
  fireEvent.submit(screen.getByRole("button", { name: /Analyze trends|Analyzing/ }));
}

async function settle(response: Response, index = 0) {
  await act(async () => {
    pending[index].resolve(response);
  });
}

it("renders one product heading and labeled controls with Heatwave selected", () => {
  render(<DashboardPage />);
  expect(screen.getAllByRole("heading", { level: 1 }).map((h) => h.textContent)).toEqual([
    "Climate Hazard Analyzer",
  ]);
  const hazard = screen.getByLabelText("Hazard") as HTMLSelectElement;
  expect([hazard.value, [...hazard.options].map((o) => o.text)]).toEqual(["heatwave", ["Heatwave"]]);
  expect(screen.getByLabelText("Latitude")).toHaveProperty("min", "-90");
  expect(screen.getByLabelText("Start year")).toHaveProperty("min", "1940");
  expect(screen.getByLabelText("Location name")).toHaveProperty("maxLength", 120);
});

it("shows guidance and no figures before any analysis", () => {
  render(<DashboardPage />);
  const results = screen.getByRole("region", { name: "Results" });
  expect(within(results).getByText("No analysis yet")).toBeTruthy();
  expect(within(results).queryByRole("table")).toBeNull();
  expect(results.textContent).not.toMatch(/°C|events?\b\s*\d/);
});

it("keeps keyboard focus order equal to the reading order", () => {
  const { container } = render(<DashboardPage />);
  expect(container.querySelector("[tabindex]")).toBeNull();
  const focusable = [...container.querySelectorAll<HTMLElement>("input, select, button")];
  expect(focusable.map((element) => element.getAttribute("name") ?? element.textContent)).toEqual([
    "place_query", "Search", "label", "latitude", "longitude", "hazard", "start_year", "end_year",
    "Analyze trends",
  ]);
});

it("validates locally, focuses the first problem and sends nothing", () => {
  render(<DashboardPage />);
  submit();
  expect(document.activeElement).toBe(screen.getByLabelText("Location name"));
  expect(screen.getByLabelText("Location name").getAttribute("aria-invalid")).toBe("true");
  fill("Location name", "Somewhere");
  fill("Latitude", "95");
  fill("Longitude", "10");
  fill("Start year", "2010");
  fill("End year", "2001");
  submit();
  expect(screen.getByText("Use a latitude between −90 and 90.")).toBeTruthy();
  expect(screen.getByText("End year must not be before the start year.")).toBeTruthy();
  fill("Latitude", "10");
  fill("Start year", "1950");
  fill("End year", "2010");
  submit();
  expect(screen.getByText("Choose at most 50 years.")).toBeTruthy();
  expect(fetchMock).not.toHaveBeenCalled();
});

it("submits the exact contract request once and renders backend results", async () => {
  render(<DashboardPage />);
  fillValid();
  submit();
  submit();
  expect(fetchMock).toHaveBeenCalledTimes(1);
  const [url, init] = fetchMock.mock.calls[0];
  expect(url).toBe("/api/v1/analyses/heatwaves");
  expect(JSON.parse(init.body)).toEqual({
    hazard: "heatwave",
    region: { kind: "point", label: "New Delhi", latitude: 28.6139, longitude: 77.209 },
    period: { start_year: 2001, end_year: 2003 },
  });
  expect(screen.getByRole("button", { name: "Analyzing…" })).toHaveProperty("disabled", true);
  expect(screen.getByRole("status").textContent).toMatch(/Analyzing historical weather for New Delhi/);

  await settle(json(syntheticResult()));
  const results = screen.getByRole("region", { name: "Results" });
  expect(within(results).getByText("Synthetic Place")).toBeTruthy();
  expect(within(results).getByText("38.1")).toBeTruthy();
  expect(within(results).getAllByRole("figure")).toHaveLength(3);
  expect(within(results).getByText("Synthetic insight sentence.")).toBeTruthy();
  expect(within(results).getByText("Not reported by the provider")).toBeTruthy();
  expect(within(results).queryByText(/Partial data/)).toBeNull();
  expect(screen.getByRole("status").textContent).toBe("Analysis complete: 6 heatwave events in 2001–2003.");
});

it("discards a late success after the settings change", async () => {
  render(<DashboardPage />);
  fillValid();
  submit();
  fill("End year", "2004");
  expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true);
  await act(async () => {
    pending[0].resolve(json(syntheticResult()));
  });
  expect(screen.queryByText("Synthetic Place")).toBeNull();
  expect(screen.getByText("Settings changed")).toBeTruthy();
});

it("discards a late error after the settings change", async () => {
  render(<DashboardPage />);
  fillValid();
  submit();
  fill("Latitude", "28.7");
  await act(async () => {
    pending[0].resolve(json(failure("PROVIDER_ERROR", true), 502));
  });
  expect(screen.queryByText(/could not be completed/)).toBeNull();
});

it.each([
  ["INSUFFICIENT_DATA", 422, false, /None of the selected years has enough valid daily data/],
  ["RATE_LIMITED", 429, true, /Wait about 30 seconds/],
])("shows typed backend errors (%s)", async (code, status, retryable, guidance) => {
  render(<DashboardPage />);
  fillValid();
  submit();
  await settle(json(failure(code, retryable), status, { "Retry-After": "30" }));
  expect(screen.getByText("Analysis could not be completed")).toBeTruthy();
  expect(screen.getByText(guidance)).toBeTruthy();
  expect(Boolean(screen.queryByRole("button", { name: "Try again" }))).toBe(retryable);
});

it("never shows gateway HTML and retries the same request", async () => {
  render(<DashboardPage />);
  fillValid();
  submit();
  await settle(new Response("<html>Bad gateway</html>", { status: 502, headers: { "Content-Type": "text/html" } }));
  expect(screen.queryByText(/Bad gateway/)).toBeNull();
  expect(screen.getByText("The service could not complete the request.")).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(fetchMock).toHaveBeenCalledTimes(2);
  expect(fetchMock.mock.calls[1][1].body).toBe(fetchMock.mock.calls[0][1].body);
});

it("distinguishes zero events from partial data", async () => {
  render(<DashboardPage />);
  fillValid();
  submit();
  await settle(json(syntheticResult({
    status: "partial",
    events: [],
    summary: { ...syntheticResult().summary, event_count: 0, mean_duration_days: null },
    annual: syntheticResult().annual.map((row) => ({ ...row, event_count: 0, mean_duration_days: null, max_duration_days: null })),
  })));
  expect(screen.getByText("No events, so no duration")).toBeTruthy();
  expect(screen.getByText(/Partial data\./)).toBeTruthy();
  expect(screen.queryByText(/Show all/)).toBeNull();
});

it("searches places and fills the location from a chosen result", async () => {
  render(<DashboardPage />);
  fireEvent.change(screen.getByLabelText("Search for a place"), { target: { value: "Delhi" } });
  fireEvent.keyDown(screen.getByLabelText("Search for a place"), { key: "Enter" });
  expect(fetchMock.mock.calls[0][0]).toBe("/api/v1/regions/search?q=Delhi");
  await settle(json({ results: [{
    id: 1, name: "New Delhi", admin1: "Delhi", country: "India", country_code: "IN",
    latitude: 28.6214, longitude: 77.2148,
  }] }));
  fireEvent.click(screen.getByLabelText(/New Delhi, Delhi, India/));
  expect(screen.getByLabelText("Location name")).toHaveProperty("value", "New Delhi, Delhi, India");
  expect(screen.getByLabelText("Latitude")).toHaveProperty("value", "28.6214");
  expect(screen.getByLabelText("Longitude")).toHaveProperty("value", "77.2148");
});

it.each([
  [{ results: [] }, 200, /No places matched “Nowhere”/],
  [failure("SEARCH_UNAVAILABLE", false), 503, /Place search is not enabled/],
])("explains empty or unavailable search", async (body, status, message) => {
  render(<DashboardPage />);
  fireEvent.change(screen.getByLabelText("Search for a place"), { target: { value: "Nowhere" } });
  fireEvent.click(screen.getByRole("button", { name: "Search" }));
  await settle(json(body, status));
  expect(screen.getByText(message)).toBeTruthy();
});

it("aborts the request when the page unmounts", () => {
  const { unmount } = render(<DashboardPage />);
  fillValid();
  submit();
  unmount();
  expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true);
});

it("discards a success that still arrives after an abort was requested", async () => {
  let resolveLate: (response: Response) => void = () => undefined;
  fetchMock.mockImplementationOnce(() => new Promise<Response>((resolve) => {
    resolveLate = resolve;
  }));
  render(<DashboardPage />);
  fillValid();
  submit();
  fill("Start year", "2002");
  await act(async () => {
    resolveLate(json(syntheticResult()));
  });
  expect(screen.queryByText("Synthetic Place")).toBeNull();
  expect(screen.getByText("Settings changed")).toBeTruthy();
});
