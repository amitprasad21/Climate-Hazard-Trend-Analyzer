import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import axe from "axe-core";
import { afterEach, expect, it } from "vitest";
import type { AnalysisResponse, HeatwaveEvent } from "../src/api/types";
import { dayOfYear, daysInYear, eventSegments, excessBin } from "../src/calendar";
import { HeatwaveCalendar } from "../src/components/HeatwaveCalendar";
import { ResultsView } from "../src/components/ResultsView";
import { annualRow, syntheticResult } from "./fixtures";

afterEach(cleanup);

function event(start: string, end: string, peak: number, censored = false): HeatwaveEvent {
  const days = (Date.parse(`${end}T00:00:00Z`) - Date.parse(`${start}T00:00:00Z`)) / 86_400_000 + 1;
  return {
    start_date: start,
    end_date: end,
    duration_days: days,
    mean_excess_c: peak / 2,
    max_excess_c: peak,
    boundary_censored: censored,
  };
}

const EVENTS = [
  event("2001-01-01", "2001-01-03", 0.5, true),
  event("2001-12-30", "2002-01-02", 1.5),
  event("2003-07-10", "2003-07-15", 3.2),
];

// Synthetic test fixture: four years, the last excluded for missing data.
function calendarResult(): AnalysisResponse {
  const base = syntheticResult();
  const excluded = { event_count: null, mean_duration_days: null, max_duration_days: null, heatwave_days: null,
    mean_tmax_c: null, tmax_anomaly_c: null, frequency_rolling_5y: null };
  return {
    ...base,
    period: { start_year: 2001, end_year: 2004 },
    summary: { ...base.summary, event_count: 3 },
    events: EVENTS,
    annual: [
      annualRow(2001, { event_count: 2, heatwave_days: 5, mean_duration_days: 3.5, max_duration_days: 4 }),
      annualRow(2002, { event_count: 0, heatwave_days: 2, mean_duration_days: null, max_duration_days: null }),
      annualRow(2003, { event_count: 1, heatwave_days: 6, mean_duration_days: 6, max_duration_days: 6 }),
      annualRow(2004, { ...excluded, eligible: false, coverage_fraction: 0.8 }),
    ],
    data_quality: {
      ...base.data_quality,
      years: [2001, 2002, 2003, 2004].map((year) => ({
        ...base.data_quality.years[0], year, eligible: year !== 2004,
        excluded_reasons: year === 2004 ? ["year_below_90_percent_valid"] : [],
      })),
      eligible_year_count: 3,
    },
  };
}

it("maps dates to day of year, including leap years", () => {
  expect([daysInYear(2020), daysInYear(2021), daysInYear(2000), daysInYear(1900)]).toEqual([366, 365, 366, 365]);
  expect(dayOfYear("2021-01-01")).toEqual([2021, 1]);
  expect(dayOfYear("2020-12-31")).toEqual([2020, 366]);
  expect(dayOfYear("2021-12-31")).toEqual([2021, 365]);
  expect(dayOfYear("2020-03-01")).toEqual([2020, 61]);
});

it("splits events that cross 31 December into one segment per year", () => {
  const segments = eventSegments(EVENTS);
  expect(segments.map((s) => [s.year, s.startDay, s.endDay, s.continuesBefore, s.continuesAfter])).toEqual([
    [2001, 1, 3, false, false],
    [2001, 364, 365, false, true],
    [2002, 1, 2, true, false],
    [2003, 191, 196, false, false],
  ]);
  const leap = eventSegments([event("2020-12-30", "2021-01-01", 1)]);
  expect(leap.map((s) => [s.year, s.startDay, s.endDay])).toEqual([[2020, 365, 366], [2021, 1, 1]]);
});

it("groups peak excess into three labelled display bins", () => {
  expect([0, 0.99, 1, 1.99, 2, 7].map(excessBin)).toEqual(["low", "low", "mid", "mid", "high", "high"]);
});

it("draws one row per year, shaded bars, censored and excluded markers", () => {
  const result = calendarResult();
  const { container } = render(
    <HeatwaveCalendar
      years={result.annual.map((r) => r.year)}
      excludedYears={[2004]}
      events={result.events}
      activeYear={null}
      selectedYear={null}
      onActiveYearChange={() => undefined}
      onSelectYear={() => undefined}
    />,
  );
  expect(container.querySelectorAll(".calendar-row")).toHaveLength(4);
  const bars = [...container.querySelectorAll(".calendar-bar")];
  expect(bars.map((bar) => bar.getAttribute("class"))).toEqual([
    "calendar-bar bar-low bar-censored",
    "calendar-bar bar-mid",
    "calendar-bar bar-mid",
    "calendar-bar bar-high",
  ]);
  expect(bars.every((bar) => Number(bar.getAttribute("width")) >= 3)).toBe(true);
  expect(container.querySelectorAll(".row-excluded-line")).toHaveLength(1);
  expect(screen.getByText(/Peak under 1 °C above the threshold/)).toBeTruthy();
  expect(screen.getByText(/display grouping/)).toBeTruthy();
});

it("keeps a one-day piece of a cross-year event visible", () => {
  const { container } = render(
    <HeatwaveCalendar years={[2002, 2003]} excludedYears={[]} events={[event("2002-12-31", "2003-01-02", 1)]}
      activeYear={null} selectedYear={null} onActiveYearChange={() => undefined} onSelectYear={() => undefined} />,
  );
  const widths = [...container.querySelectorAll(".calendar-bar")].map((bar) => Number(bar.getAttribute("width")));
  expect(widths).toHaveLength(2);
  expect(Math.min(...widths)).toBe(3);
});

it("says plainly when a period has no events", () => {
  render(
    <HeatwaveCalendar years={[2001, 2002]} excludedYears={[]} events={[]} activeYear={null} selectedYear={null}
      onActiveYearChange={() => undefined} onSelectYear={() => undefined} />,
  );
  expect(screen.getByText("No heatwave events in this period.")).toBeTruthy();
});

it("shows event details when a bar is hovered", () => {
  const result = calendarResult();
  const { container } = render(
    <HeatwaveCalendar years={[2001, 2002, 2003, 2004]} excludedYears={[2004]} events={result.events}
      activeYear={null} selectedYear={null} onActiveYearChange={() => undefined} onSelectYear={() => undefined} />,
  );
  fireEvent.pointerEnter(container.querySelectorAll(".calendar-bar")[1]);
  const tooltip = container.querySelector(".calendar-tooltip");
  expect(tooltip?.textContent).toMatch(/30 Dec 2001 – 2 Jan 2002/);
  expect(tooltip?.textContent).toMatch(/4 days/);
  expect(tooltip?.textContent).toMatch(/peak 1\.50 °C/);
  expect(tooltip?.textContent).toMatch(/continues into 2002/);
});

function calendarRow(container: HTMLElement, year: number) {
  return container.querySelector(`.calendar-row[data-year="${year}"]`) as Element;
}

it("links hover across the calendar and the line charts", () => {
  const { container } = render(<ResultsView result={calendarResult()} />);
  fireEvent.pointerEnter(calendarRow(container, 2003));
  expect(calendarRow(container, 2003).getAttribute("class")).toMatch(/row-active/);
  expect(container.querySelectorAll(".chart .crosshair-line")).toHaveLength(3);
  fireEvent.pointerLeave(container.querySelector(".calendar-svg") as Element);
  expect(container.querySelectorAll(".chart .crosshair-line")).toHaveLength(0);
});

it("selects a year by click, keyboard select or chart click, and clears with Escape", async () => {
  const { container } = render(<ResultsView result={calendarResult()} />);
  fireEvent.click(calendarRow(container, 2001));
  const detail = screen.getByRole("region", { name: "2001 in detail" });
  expect(within(detail).getByText("Events started")).toBeTruthy();
  expect(within(detail).getAllByRole("listitem")).toHaveLength(2);
  expect(screen.getByText("Show events touching 2001 (2)")).toBeTruthy();
  expect(container.querySelectorAll(".chart .selected-line")).toHaveLength(3);
  fireEvent.click(calendarRow(container, 2001));
  expect(screen.queryByRole("region", { name: /in detail/ })).toBeNull();

  fireEvent.change(screen.getByLabelText("Inspect a year"), { target: { value: "2004" } });
  const excluded = screen.getByRole("region", { name: "2004 in detail" });
  expect(within(excluded).getByText(/excluded/i)).toBeTruthy();
  expect(within(excluded).getByText(/below 90% valid days/)).toBeTruthy();

  await act(async () => {
    fireEvent.keyDown(document, { key: "Escape" });
  });
  expect(screen.queryByRole("region", { name: /in detail/ })).toBeNull();
  expect((screen.getByLabelText("Inspect a year") as HTMLSelectElement).value).toBe("");
  expect(screen.getByText("Show all 3 events")).toBeTruthy();

  // jsdom reports a zero-origin box, so clientX 250 is nearest the second of four plotted years.
  fireEvent.click(container.querySelector(".chart svg[role=img]:not(.calendar-svg)") as Element, { clientX: 250 });
  expect(screen.getByRole("region", { name: "2002 in detail" })).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Show all years" }));
  expect(screen.queryByRole("region", { name: /in detail/ })).toBeNull();
});

it("has no detectable accessibility violations with a year selected", async () => {
  render(
    <main>
      <ResultsView result={calendarResult()} />
    </main>,
  );
  fireEvent.change(screen.getByLabelText("Inspect a year"), { target: { value: "2003" } });
  const report = await axe.run(document.body, { rules: { "color-contrast": { enabled: false } } });
  expect(report.violations.map((v) => v.id)).toEqual([]);
});
