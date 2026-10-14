import { useId, useLayoutEffect, useRef, useState, type RefObject } from "react";
import { formatNumber } from "../format";

export type Series = {
  label: string;
  values: (number | null)[];
  variant: "primary" | "secondary";
};

type Props = {
  title: string;
  description: string;
  years: number[];
  series: Series[];
  unit: string;
  digits?: number;
  integerAxis?: boolean;
  zeroLine?: boolean;
};

const HEIGHT = 280;
const MARGIN = { top: 16, right: 20, bottom: 36, left: 56 };
const MIN_LABEL_SPACING = 52;

function useWidth(ref: RefObject<HTMLElement | null>, fallback = 640) {
  const [width, setWidth] = useState(fallback);
  useLayoutEffect(() => {
    const element = ref.current;
    if (!element || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(([entry]) => {
      setWidth(Math.max(240, Math.floor(entry.contentRect.width)));
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, [ref]);
  return width;
}

export function niceTicks(min: number, max: number, count: number, integer: boolean): number[] {
  const span = max - min || 1;
  const raw = span / count;
  const magnitude = 10 ** Math.floor(Math.log10(raw));
  const ratio = raw / magnitude;
  let step = (ratio >= 7.5 ? 10 : ratio >= 3.5 ? 5 : ratio >= 1.5 ? 2 : 1) * magnitude;
  if (integer) step = Math.max(1, Math.round(step));
  const first = Math.floor(min / step) * step;
  const last = Math.ceil(max / step) * step;
  const ticks = [];
  for (let value = first; value <= last + step / 2; value += step) ticks.push(Number(value.toFixed(10)));
  return ticks.length > 1 ? ticks : [first, first + step];
}

export function segments(values: (number | null)[]): number[][] {
  const runs: number[][] = [];
  let current: number[] = [];
  values.forEach((value, index) => {
    if (value === null) {
      if (current.length) runs.push(current);
      current = [];
    } else {
      current.push(index);
    }
  });
  if (current.length) runs.push(current);
  return runs;
}

function LegendSwatch({ variant }: { variant: Series["variant"] }) {
  return (
    <svg width="32" height="12" aria-hidden="true" className={`swatch swatch-${variant}`}>
      <line x1="2" y1="6" x2="30" y2="6" />
      {variant === "primary" && <circle cx="16" cy="6" r="3" />}
    </svg>
  );
}

export function LineChart({
  title,
  description,
  years,
  series,
  unit,
  digits = 1,
  integerAxis = false,
  zeroLine = false,
}: Props) {
  const container = useRef<HTMLDivElement>(null);
  const width = useWidth(container);
  const titleId = useId();
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const plotWidth = width - MARGIN.left - MARGIN.right;
  const plotHeight = HEIGHT - MARGIN.top - MARGIN.bottom;
  const values = series.flatMap((s) => s.values).filter((v): v is number => v !== null);
  const hasData = values.length > 0;
  const ticks = niceTicks(Math.min(0, ...values), Math.max(0, ...values), 4, integerAxis);
  const low = ticks[0];
  const high = ticks[ticks.length - 1];
  const firstYear = years[0];
  const yearSpan = years[years.length - 1] - firstYear;
  const x = (year: number) =>
    MARGIN.left + (yearSpan === 0 ? plotWidth / 2 : ((year - firstYear) / yearSpan) * plotWidth);
  const y = (value: number) => MARGIN.top + plotHeight - ((value - low) / (high - low)) * plotHeight;
  const labelEvery = Math.max(1, Math.ceil(years.length / Math.max(1, Math.floor(plotWidth / MIN_LABEL_SPACING))));
  const gradientId = `area-grad-${titleId.replace(/[^a-zA-Z0-9_-]/g, "_")}`;
  const baselineY = zeroLine && low < 0 ? y(0) : MARGIN.top + plotHeight;

  function handlePointerMove(event: React.PointerEvent<SVGSVGElement>) {
    if (!container.current || years.length === 0) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    if (mouseX < MARGIN.left || mouseX > width - MARGIN.right) {
      setHoveredIndex(null);
      return;
    }
    const relX = (mouseX - MARGIN.left) / plotWidth;
    let closestIndex = 0;
    let minDistance = Infinity;
    years.forEach((year, index) => {
      const yearX = (x(year) - MARGIN.left) / plotWidth;
      const dist = Math.abs(relX - yearX);
      if (dist < minDistance) {
        minDistance = dist;
        closestIndex = index;
      }
    });
    setHoveredIndex(closestIndex);
  }

  function handlePointerLeave() {
    setHoveredIndex(null);
  }

  return (
    <figure className="chart">
      <figcaption>
        <h3 id={titleId}>{title}</h3>
        <p className="chart-description">{description}</p>
      </figcaption>
      <ul className="legend">
        {series.map((s) => (
          <li key={s.label}>
            <LegendSwatch variant={s.variant} />
            {s.label}
          </li>
        ))}
      </ul>
      <div ref={container} className="chart-canvas">
        {hasData ? (
          <>
            <svg
              // The viewBox keeps the drawing fitted even before a resize measurement arrives.
              viewBox={`0 0 ${width} ${HEIGHT}`}
              className="chart-svg"
              role="img"
              aria-labelledby={titleId}
              aria-describedby={`${titleId}-summary`}
              onPointerMove={handlePointerMove}
              onPointerLeave={handlePointerLeave}
            >
            <desc id={`${titleId}-summary`}>
              {`${title}, ${years[0]}–${years[years.length - 1]}. Exact values are in the data table.`}
            </desc>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop className="chart-gradient-top" offset="0%" />
                <stop className="chart-gradient-bottom" offset="100%" />
              </linearGradient>
            </defs>
            {ticks.map((tick) => (
              <g key={tick}>
                <line className="grid-line" x1={MARGIN.left} x2={width - MARGIN.right} y1={y(tick)} y2={y(tick)} />
                <text className="axis-label" x={MARGIN.left - 8} y={y(tick)} textAnchor="end" dominantBaseline="middle">
                  {formatNumber(tick, integerAxis ? 0 : Number.isInteger(tick) ? 0 : 1)}
                </text>
              </g>
            ))}
            {zeroLine && low < 0 && <line className="zero-line" x1={MARGIN.left} x2={width - MARGIN.right} y1={y(0)} y2={y(0)} />}
            {years.map((year, index) =>
              index % labelEvery === 0 ? (
                <text key={year} className="axis-label" x={x(year)} y={HEIGHT - 12} textAnchor="middle">
                  {year}
                </text>
              ) : null,
            )}
            <text className="axis-title" transform={`translate(14 ${MARGIN.top + plotHeight / 2}) rotate(-90)`} textAnchor="middle">
              {unit}
            </text>
            {series.map(
              (s) =>
                s.variant === "primary" &&
                segments(s.values).map(
                  (run) =>
                    run.length > 1 && (
                      <path
                        key={`area-${run[0]}`}
                        className="series-area"
                        fill={`url(#${gradientId})`}
                        d={`M${x(years[run[0]])},${baselineY} ${run.map((i) => `L${x(years[i])},${y(s.values[i] as number)}`).join(" ")} L${x(years[run[run.length - 1]])},${baselineY} Z`}
                      />
                    ),
                ),
            )}
            {series.map((s) =>
              segments(s.values).map((run) => (
                <g key={`${s.label}-${run[0]}`} className={`series series-${s.variant}`}>
                  {run.length > 1 && (
                    <path
                      d={run.map((i, n) => `${n ? "L" : "M"}${x(years[i])},${y(s.values[i] as number)}`).join(" ")}
                    />
                  )}
                  {(s.variant === "primary" || run.length === 1) &&
                    run.map((i) => (
                      <circle key={i} cx={x(years[i])} cy={y(s.values[i] as number)} r={3}>
                        <title>{`${years[i]}: ${formatNumber(s.values[i], digits)} ${unit} (${s.label})`}</title>
                      </circle>
                    ))}
                </g>
              )),
            )}
            {hoveredIndex !== null && (
              <g className="chart-focus" aria-hidden="true">
                <line
                  className="crosshair-line"
                  x1={x(years[hoveredIndex])}
                  x2={x(years[hoveredIndex])}
                  y1={MARGIN.top}
                  y2={HEIGHT - MARGIN.bottom}
                />
                {series.map((s) => {
                  const val = s.values[hoveredIndex];
                  if (val === null) return null;
                  return (
                    <circle
                      key={`focus-${s.label}`}
                      className={`focus-dot focus-dot-${s.variant}`}
                      cx={x(years[hoveredIndex])}
                      cy={y(val)}
                      r={5}
                    />
                  );
                })}
              </g>
            )}
          </svg>
          {hoveredIndex !== null && (
            <div
              className="chart-tooltip"
              aria-hidden="true"
              style={{
                left: `${Math.min(width - 160, Math.max(MARGIN.left, x(years[hoveredIndex]) - 75))}px`,
                top: `${MARGIN.top + 8}px`,
              }}
            >
              <p className="tooltip-year">{years[hoveredIndex]}</p>
              <ul className="tooltip-values">
                {series.map((s) => (
                  <li key={s.label} className="tooltip-row">
                    <span className="tooltip-label">{s.label}:</span>
                    <span className="tooltip-val">
                      {s.values[hoveredIndex] !== null
                        ? `${formatNumber(s.values[hoveredIndex], digits)} ${unit}`
                        : "—"}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
        ) : (
          <p className="chart-empty">No year in this period has a value for this chart.</p>
        )}
      </div>
      <details className="data-table">
        <summary>Show data table</summary>
        <table>
          <caption className="visually-hidden">{title}</caption>
          <thead>
            <tr>
              <th scope="col">Year</th>
              {series.map((s) => (
                <th key={s.label} scope="col">
                  {s.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {years.map((year, index) => (
              <tr key={year}>
                <th scope="row">{year}</th>
                {series.map((s) => (
                  <td key={s.label}>{formatNumber(s.values[index], digits)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  );
}
