import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { DashboardPage } from "../src/DashboardPage";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

function fill(label: string, value: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}

it("renders one product heading and a labeled analysis form", () => {
  render(<DashboardPage />);
  expect(screen.getAllByRole("heading", { level: 1 }).map((h) => h.textContent)).toEqual([
    "Climate Hazard Analyzer",
  ]);
  const hazard = screen.getByLabelText("Hazard") as HTMLSelectElement;
  expect(hazard.value).toBe("heatwave");
  expect([...hazard.options].map((option) => option.text)).toEqual(["Heatwave"]);
  expect(screen.getByLabelText("Latitude")).toHaveProperty("min", "-90");
  expect(screen.getByLabelText("Longitude")).toHaveProperty("max", "180");
  expect(screen.getByLabelText("Start year")).toHaveProperty("min", "1940");
  expect(screen.getByLabelText("Location name")).toHaveProperty("maxLength", 120);
  expect(screen.getByRole("button", { name: "Analyze trends" })).toHaveProperty("type", "submit");
});

it("shows guidance and no figures before any analysis", () => {
  render(<DashboardPage />);
  const results = screen.getByRole("region", { name: "Results" });
  expect(within(results).getByText("No analysis yet")).toBeTruthy();
  expect(within(results).queryByRole("table")).toBeNull();
  expect(within(results).queryByRole("figure")).toBeNull();
  expect(results.textContent).not.toMatch(/°C|events?\b\s*\d/);
});

it("submitting never calls the network or invents results", () => {
  const fetchSpy = vi.spyOn(globalThis, "fetch");
  render(<DashboardPage />);
  fill("Location name", "New Delhi");
  fill("Latitude", "28.6139");
  fill("Longitude", "77.209");
  fill("Start year", "1990");
  fill("End year", "2020");
  fireEvent.submit(screen.getByRole("button", { name: "Analyze trends" }));
  expect(fetchSpy).not.toHaveBeenCalled();
  expect(screen.getByRole("status").textContent).toMatch(/not connected/);
  expect(screen.getByText("No analysis yet")).toBeTruthy();
});

it("keeps keyboard focus order equal to the reading order", () => {
  const { container } = render(<DashboardPage />);
  expect(container.querySelector("[tabindex]")).toBeNull();
  const focusable = [...container.querySelectorAll<HTMLElement>("input, select, button")];
  expect(focusable.every((element) => !element.hasAttribute("disabled"))).toBe(true);
  expect(focusable.map((element) => element.getAttribute("name"))).toEqual([
    "label", "latitude", "longitude", "hazard", "start_year", "end_year", null,
  ]);
});
