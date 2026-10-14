const DASH = "—";

export function formatNumber(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined) return DASH;
  return value.toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function formatSigned(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined) return DASH;
  const text = formatNumber(Math.abs(value), digits);
  if (value > 0) return `+${text}`;
  return value < 0 ? `−${text}` : text;
}

export function formatPercent(fraction: number): string {
  return `${(fraction * 100).toLocaleString("en-US", { maximumFractionDigits: 1 })}%`;
}

export function formatCoordinate(value: number, axis: "lat" | "lon"): string {
  const hemisphere = axis === "lat" ? (value >= 0 ? "N" : "S") : value >= 0 ? "E" : "W";
  return `${Math.abs(value).toFixed(4)}° ${hemisphere}`;
}

export function formatDate(iso: string): string {
  const [year, month, day] = iso.slice(0, 10).split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day)).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

export function formatTimestamp(iso: string): string {
  return `${new Date(iso).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  })} UTC`;
}

export const PROVIDER_NAMES = { nasa_power: "NASA POWER", open_meteo: "Open-Meteo" } as const;
