import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import type { AnalysisResponse } from "../src/api/types";
import { DashboardPage } from "../src/DashboardPage";
import { syntheticResult } from "./fixtures";

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

const validFor = (ms: number): AnalysisResponse =>
  syntheticResult({
    cache: {
      hit: false,
      generated_at: new Date(Date.now() - 1000).toISOString(),
      expires_at: new Date(Date.now() + ms).toISOString(),
    },
  });

const failure = {
  error: { code: "PROVIDER_ERROR", message: "Synthetic failure.", request_id: "r", details: [], retryable: true },
};

let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function fill(label: string, value: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}

async function analyze(label: string, start = "2001") {
  fill("Location name", label);
  fill("Latitude", "28.6139");
  fill("Longitude", "77.209");
  fill("Start year", start);
  fill("End year", "2003");
  await act(async () => {
    fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
  });
}

it("reuses a saved result without a request, relabelled and marked as saved", async () => {
  fetchMock.mockResolvedValueOnce(json(validFor(3_600_000)));
  render(<DashboardPage />);
  await analyze("New Delhi");
  expect(fetchMock).toHaveBeenCalledTimes(1);
  expect(screen.queryByText(/saved in this browser/)).toBeNull();

  await analyze("Delhi, India");
  expect(fetchMock).toHaveBeenCalledTimes(1);
  expect(document.querySelector(".result-context strong")?.textContent).toBe("Delhi, India");
  expect(screen.getByText(/saved in this browser/)).toBeTruthy();
  expect(screen.getByRole("status").textContent).toMatch(/saved result, no new request/);
});

it("requests again when the science inputs change or the saved result has expired", async () => {
  fetchMock
    .mockResolvedValueOnce(json(validFor(3_600_000)))
    .mockResolvedValueOnce(json(validFor(-1)))
    .mockResolvedValueOnce(json(validFor(3_600_000)));
  render(<DashboardPage />);
  await analyze("Place", "2001");
  await analyze("Place", "2002");
  expect(fetchMock).toHaveBeenCalledTimes(2);
  await analyze("Place", "2001");
  expect(fetchMock).toHaveBeenCalledTimes(2);
  await analyze("Place", "2002");
  expect(fetchMock).toHaveBeenCalledTimes(3);
});

it("never saves failures", async () => {
  fetchMock.mockResolvedValueOnce(json(failure, 502)).mockResolvedValueOnce(json(validFor(3_600_000)));
  render(<DashboardPage />);
  await analyze("Place");
  expect(screen.getByText("Analysis could not be completed")).toBeTruthy();
  await analyze("Place again");
  expect(fetchMock).toHaveBeenCalledTimes(2);
  expect(screen.queryByText(/saved in this browser/)).toBeNull();
  expect(document.querySelector(".result-context")).toBeTruthy();
});
