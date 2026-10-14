import { useId, useMemo, useRef, useState } from "react";
import type { HeatwaveEvent } from "../api/types";
import { EXCESS_BINS, daysInYear, eventSegments, excessBin, type EventSegment } from "../calendar";
import { formatDate, formatNumber } from "../format";
import { useWidth } from "../hooks/useWidth";

type Props = {
  years: number[];
  excludedYears: number[];
  events: HeatwaveEvent[];
  activeYear: number | null;
  selectedYear: number | null;
  onActiveYearChange: (year: number | null) => void;
  onSelectYear: (year: number | null) => void;
};

const MARGIN = { top: 24, right: 12, bottom: 4, left: 48 };
const MONTH_STARTS = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366];
const MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MIN_BAR_WIDTH = 3;
const MIN_LABEL_SPACING = 14;

const rowHeightFor = (count: number) => Math.min(22, Math.max(8, Math.floor(360 / count)));

function barClass(segment: EventSegment): string {
  const censored = segment.event.boundary_censored ? " bar-censored" : "";
  return `calendar-bar bar-${excessBin(segment.event.max_excess_c)}${censored}`;
}

function SegmentTooltip({ segment, left, top, above }: { segment: EventSegment; left: number; top: number; above: boolean }) {
  const { event, year } = segment;
  const notes = [
    segment.continuesBefore && `Event continues from ${year - 1}`,
    segment.continuesAfter && `Event continues into ${year + 1}`,
    event.boundary_censored && "Cut off by the edge of the period",
  ].filter(Boolean);
  return (
    <div
      className={`chart-tooltip calendar-tooltip${above ? " tooltip-above" : ""}`}
      aria-hidden="true"
      style={{ left: `${left}px`, top: `${top}px` }}
    >
      <p className="tooltip-year">
        {formatDate(event.start_date)} – {formatDate(event.end_date)}
      </p>
      <p className="tooltip-detail">
        {event.duration_days} days, peak {formatNumber(event.max_excess_c, 2)} °C above the threshold
      </p>
      {notes.map((note) => (
        <p key={String(note)} className="tooltip-detail">
          {note}
        </p>
      ))}
    </div>
  );
}

export function HeatwaveCalendar({
  years,
  excludedYears,
  events,
  activeYear,
  selectedYear,
  onActiveYearChange,
  onSelectYear,
}: Props) {
  const container = useRef<HTMLDivElement>(null);
  const width = useWidth(container);
  const titleId = useId();
  const [hovered, setHovered] = useState<EventSegment | null>(null);
  const byYear = useMemo(() => {
    const groups = new Map<number, EventSegment[]>();
    for (const segment of eventSegments(events)) {
      groups.set(segment.year, [...(groups.get(segment.year) ?? []), segment]);
    }
    return groups;
  }, [events]);
  const excluded = new Set(excludedYears);
  const rowHeight = rowHeightFor(years.length);
  const height = MARGIN.top + years.length * rowHeight + MARGIN.bottom;
  const plotWidth = width - MARGIN.left - MARGIN.right;
  const rowY = (index: number) => MARGIN.top + index * rowHeight;
  const dayX = (day: number, year: number) => MARGIN.left + ((day - 1) / daysInYear(year)) * plotWidth;
  const labelEvery = Math.ceil(MIN_LABEL_SPACING / rowHeight);
  const shortMonths = plotWidth / 12 < 30;
  const hoveredRow = hovered ? years.indexOf(hovered.year) : -1;
  const hasCensored = events.some((event) => event.boundary_censored);

  function clearHover() {
    setHovered(null);
    onActiveYearChange(null);
  }

  return (
    <figure className="chart calendar">
      <figcaption>
        <h3 id={titleId}>Heatwave calendar</h3>
        <p className="chart-description">
          One row per year; each bar is a heatwave on the days it covered. Shading is a display grouping of each
          event's peak excess above the threshold, not a separate statistic.
        </p>
      </figcaption>
      {events.length > 0 && (
        <ul className="legend">
          {EXCESS_BINS.map(({ bin, label }) => (
            <li key={bin}>
              <svg width="16" height="12" aria-hidden="true" className="swatch">
                <rect className={`swatch-bar bar-${bin}`} x="1" y="1" width="14" height="10" />
              </svg>
              {label}
            </li>
          ))}
          {hasCensored && (
            <li>
              <svg width="16" height="12" aria-hidden="true" className="swatch">
                <rect className="swatch-bar bar-censored" x="1" y="1" width="14" height="10" />
              </svg>
              Cut off by the edge of the period
            </li>
          )}
          {excluded.size > 0 && (
            <li>
              <svg width="16" height="12" aria-hidden="true" className="swatch swatch-excluded">
                <line x1="1" y1="6" x2="15" y2="6" />
              </svg>
              Year excluded for missing data
            </li>
          )}
        </ul>
      )}
      <div ref={container} className="chart-canvas">
        {events.length === 0 ? (
          <p className="chart-empty">No heatwave events in this period.</p>
        ) : (
          <>
            <svg
              viewBox={`0 0 ${width} ${height}`}
              className="chart-svg calendar-svg"
              role="img"
              aria-labelledby={titleId}
              aria-describedby={`${titleId}-summary`}
              onPointerLeave={clearHover}
            >
              <desc id={`${titleId}-summary`}>
                {`Heatwave events by day of year, ${years[0]}–${years[years.length - 1]}.`}
                {excluded.size > 0 && ` Excluded years: ${[...excluded].join(", ")}.`}
                {" Exact dates are in the events table."}
              </desc>
              {MONTH_NAMES.map((name, month) => {
                const start = MARGIN.left + ((MONTH_STARTS[month] - 1) / 365) * plotWidth;
                const end = MARGIN.left + ((MONTH_STARTS[month + 1] - 1) / 365) * plotWidth;
                return (
                  <g key={name}>
                    {month > 0 && (
                      <line className="grid-line" x1={start} x2={start} y1={MARGIN.top} y2={height - MARGIN.bottom} />
                    )}
                    <text className="axis-label" x={(start + end) / 2} y={MARGIN.top - 8} textAnchor="middle">
                      {shortMonths ? name[0] : name}
                    </text>
                  </g>
                );
              })}
              {years.map((year, index) => {
                const top = rowY(index);
                const middle = top + rowHeight / 2;
                const rowClass = [
                  "calendar-row",
                  year === activeYear && "row-active",
                  year === selectedYear && "row-selected",
                ]
                  .filter(Boolean)
                  .join(" ");
                return (
                  <g
                    key={year}
                    className={rowClass}
                    data-year={year}
                    onPointerEnter={() => onActiveYearChange(year)}
                    onClick={() => onSelectYear(year === selectedYear ? null : year)}
                  >
                    <rect className="row-bg" x={0} y={top} width={width} height={rowHeight} />
                    {(index % labelEvery === 0 || year === selectedYear) && (
                      <text className="axis-label" x={MARGIN.left - 8} y={middle} textAnchor="end" dominantBaseline="middle">
                        {year}
                      </text>
                    )}
                    {excluded.has(year) && (
                      <line className="row-excluded-line" x1={MARGIN.left} x2={width - MARGIN.right} y1={middle} y2={middle} />
                    )}
                    {(byYear.get(year) ?? []).map((segment) => {
                      const start = dayX(segment.startDay, year);
                      const end = start + Math.max(MIN_BAR_WIDTH, dayX(segment.endDay + 1, year) - start);
                      return (
                        <g key={segment.event.start_date}>
                          <rect
                            className={barClass(segment)}
                            x={start}
                            y={top + 1}
                            width={end - start}
                            height={rowHeight - 2}
                            onPointerEnter={() => setHovered(segment)}
                            onPointerLeave={() => setHovered(null)}
                          />
                          {segment.continuesAfter && (
                            <polygon className="continuation-mark" points={`${end + 1},${top + 1} ${end + 5},${middle} ${end + 1},${top + rowHeight - 1}`} />
                          )}
                          {segment.continuesBefore && (
                            <polygon className="continuation-mark" points={`${start - 1},${top + 1} ${start - 5},${middle} ${start - 1},${top + rowHeight - 1}`} />
                          )}
                        </g>
                      );
                    })}
                  </g>
                );
              })}
            </svg>
            {hovered && hoveredRow >= 0 && (
              <SegmentTooltip
                segment={hovered}
                left={Math.max(0, Math.min(width - 240, dayX(hovered.startDay, hovered.year) - 24))}
                top={hoveredRow < years.length / 2 ? rowY(hoveredRow) + rowHeight + 4 : rowY(hoveredRow) - 4}
                above={hoveredRow >= years.length / 2}
              />
            )}
          </>
        )}
      </div>
    </figure>
  );
}
