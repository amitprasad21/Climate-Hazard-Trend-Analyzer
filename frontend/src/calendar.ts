import type { HeatwaveEvent } from "./api/types";

export type ExcessBin = "low" | "mid" | "high";

export const EXCESS_BINS: { bin: ExcessBin; label: string }[] = [
  { bin: "low", label: "Peak under 1 °C above the threshold" },
  { bin: "mid", label: "Peak 1 to 2 °C above" },
  { bin: "high", label: "Peak 2 °C or more above" },
];

export type EventSegment = {
  event: HeatwaveEvent;
  year: number;
  startDay: number;
  endDay: number;
  continuesBefore: boolean;
  continuesAfter: boolean;
};

export function daysInYear(year: number): number {
  return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0) ? 366 : 365;
}

export function dayOfYear(iso: string): [number, number] {
  const [year, month, day] = iso.slice(0, 10).split("-").map(Number);
  return [year, (Date.UTC(year, month - 1, day) - Date.UTC(year, 0, 1)) / 86_400_000 + 1];
}

export function eventSegments(events: HeatwaveEvent[]): EventSegment[] {
  return events.flatMap((event) => {
    const [startYear, startDay] = dayOfYear(event.start_date);
    const [endYear, endDay] = dayOfYear(event.end_date);
    const parts: EventSegment[] = [];
    for (let year = startYear; year <= endYear; year += 1) {
      parts.push({
        event,
        year,
        startDay: year === startYear ? startDay : 1,
        endDay: year === endYear ? endDay : daysInYear(year),
        continuesBefore: year > startYear,
        continuesAfter: year < endYear,
      });
    }
    return parts;
  });
}

export function eventsTouching(events: HeatwaveEvent[], year: number): HeatwaveEvent[] {
  return events.filter(
    (event) => Number(event.start_date.slice(0, 4)) <= year && Number(event.end_date.slice(0, 4)) >= year,
  );
}

// Groups the backend's peak excess for shading only; no new statistic is derived.
export function excessBin(peak: number): ExcessBin {
  if (peak >= 2) return "high";
  return peak >= 1 ? "mid" : "low";
}

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
  "November", "December"];

export function exclusionText(reason: string): string {
  if (reason === "year_below_90_percent_valid") return "below 90% valid days in the year";
  const month = /^month_(\d{2})_below_80_percent_valid$/.exec(reason);
  return month ? `${MONTHS[Number(month[1]) - 1]} below 80% valid days` : reason;
}
