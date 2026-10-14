import { cleanup, fireEvent, render, within } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import { LineChart, niceTicks, segments } from "../src/components/LineChart";

afterEach(cleanup);

it("splits series at null years so lines never bridge gaps", () => {
  expect(segments([1, null, 2, 3, null, null, 4])).toEqual([[0], [2, 3], [6]]);
  expect(segments([null, null])).toEqual([]);
});

it("chooses readable, inclusive tick steps", () => {
  expect(niceTicks(0, 7, 4, true)).toEqual([0, 2, 4, 6, 8]);
  expect(niceTicks(-1.3, 1.7, 4, false)).toEqual([-2, -1, 0, 1, 2]);
  expect(niceTicks(0, 0.9, 4, false)).toEqual([0, 0.2, 0.4, 0.6, 0.8, 1]);
  expect(niceTicks(0, 0, 4, true)).toEqual([0, 1]);
});

it("draws solid primary and dashed secondary series with gaps and a full data table", () => {
  const { container } = render(
    <LineChart
      title="Frequency"
      description="Synthetic"
      years={[2001, 2002, 2003, 2004]}
      unit="events"
      series={[
        { label: "Events", values: [1, null, 2, 3], variant: "primary" },
        { label: "Rolling", values: [null, null, null, 2], variant: "secondary" },
      ]}
    />,
  );
  const primary = container.querySelectorAll(".series-primary");
  expect(primary).toHaveLength(2);
  expect(container.querySelectorAll(".series-primary path")).toHaveLength(1);
  expect(container.querySelectorAll(".series-primary circle")).toHaveLength(3);
  expect(container.querySelectorAll(".series-secondary circle")).toHaveLength(1);
  const svg = container.querySelector("svg[role=img]");
  expect(svg?.getAttribute("aria-labelledby")).toBeTruthy();
  expect(svg?.getAttribute("viewBox")).toBe("0 0 640 280");
  expect(svg?.hasAttribute("width")).toBe(false);
  const rows = within(container.querySelector("table") as HTMLElement).getAllByRole("row");
  expect(rows.map((row) => row.textContent)).toEqual([
    "YearEventsRolling", "20011.0—", "2002——", "20032.0—", "20043.02.0",
  ]);
});

it("explains an empty chart instead of drawing a false line", () => {
  const { container, getByText } = render(
    <LineChart title="Duration" description="Synthetic" years={[2001]} unit="days"
      series={[{ label: "Mean", values: [null], variant: "primary" }]} />,
  );
  expect(container.querySelector("svg[role=img]")).toBeNull();
  expect(getByText("No year in this period has a value for this chart.")).toBeTruthy();
});

it("maps pointer pixels through the viewBox when the drawing is scaled", () => {
  const picked: number[] = [];
  const { container } = render(
    <LineChart title="Frequency" description="Synthetic" years={[2001, 2002, 2003, 2004]} unit="events"
      series={[{ label: "Events", values: [1, 2, 3, 4], variant: "primary" }]} onSelectYear={(year) => picked.push(year)} />,
  );
  const svg = container.querySelector("svg[role=img]") as SVGSVGElement;
  // Drawn at half its 640-unit viewBox width, so 125 px on screen is 250 units: nearest 2002.
  svg.getBoundingClientRect = () => ({ left: 0, top: 0, width: 320, height: 140 }) as DOMRect;
  fireEvent.click(svg, { clientX: 125 });
  expect(picked).toEqual([2002]);
});

it("renders interactive crosshair and floating tooltip on pointer hover", () => {
  const { container } = render(
    <LineChart
      title="Frequency"
      description="Synthetic"
      years={[2001, 2002, 2003, 2004]}
      unit="events"
      series={[
        { label: "Events", values: [1, 2, 3, 4], variant: "primary" },
      ]}
    />,
  );
  const svg = container.querySelector("svg[role=img]") as SVGSVGElement;
  expect(container.querySelector(".crosshair-line")).toBeNull();
  expect(container.querySelector(".chart-tooltip")).toBeNull();

  // Pointer move into svg
  fireEvent.pointerMove(svg, { clientX: 200 });
  expect(container.querySelector(".crosshair-line")).not.toBeNull();
  const tooltip = container.querySelector(".chart-tooltip");
  expect(tooltip).not.toBeNull();
  expect(tooltip?.textContent).toContain("Events:");

  // Pointer leave
  fireEvent.pointerLeave(svg);
  expect(container.querySelector(".crosshair-line")).toBeNull();
  expect(container.querySelector(".chart-tooltip")).toBeNull();
});
