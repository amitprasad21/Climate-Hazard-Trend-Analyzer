import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import axe from "axe-core";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { DashboardPage } from "../src/DashboardPage";
import { syntheticResult } from "./fixtures";

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

async function violations() {
  // jsdom cannot compute rendered colours; token contrast is checked by scripts/check_docs.py.
  const result = await axe.run(document.body, { rules: { "color-contrast": { enabled: false } } });
  return result.violations.map((v) => `${v.id} (${v.nodes.length}): ${v.help}`);
}

function fillValid() {
  for (const [label, value] of [
    ["Location name", "New Delhi"], ["Latitude", "28.6139"], ["Longitude", "77.209"],
    ["Start year", "2001"], ["End year", "2003"],
  ]) {
    fireEvent.change(screen.getByLabelText(label), { target: { value } });
  }
}

beforeEach(() => vi.stubGlobal("fetch", vi.fn()));
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("has no detectable violations when idle and when showing validation errors", async () => {
  render(<DashboardPage />);
  expect(await violations()).toEqual([]);
  fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
  expect(await violations()).toEqual([]);
});

it("has no detectable violations with search results listed", async () => {
  vi.mocked(fetch).mockResolvedValueOnce(json({ results: [{
    id: 1, name: "New Delhi", admin1: "Delhi", country: "India", country_code: "IN",
    latitude: 28.6214, longitude: 77.2148,
  }] }));
  render(<DashboardPage />);
  fireEvent.change(screen.getByLabelText("Search for a place"), { target: { value: "Delhi" } });
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Search" }));
  });
  expect(await violations()).toEqual([]);
});

it("has no detectable violations with populated results and with an error", async () => {
  vi.mocked(fetch).mockResolvedValueOnce(json(syntheticResult({ status: "partial" })));
  render(<DashboardPage />);
  fillValid();
  await act(async () => {
    fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
  });
  expect(screen.getAllByRole("figure")).toHaveLength(3);
  expect(await violations()).toEqual([]);

  cleanup();
  vi.mocked(fetch).mockResolvedValueOnce(json({ error: {
    code: "PROVIDER_ERROR", message: "Synthetic failure.", request_id: "r", details: [], retryable: true,
  } }, 502));
  render(<DashboardPage />);
  fillValid();
  await act(async () => {
    fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
  });
  expect(screen.getByText("Analysis could not be completed")).toBeTruthy();
  expect(await violations()).toEqual([]);
});

it("detects a real violation, so the passing audits are meaningful", async () => {
  render(<input type="text" />);
  expect((await violations()).some((v) => v.startsWith("label"))).toBe(true);
});
