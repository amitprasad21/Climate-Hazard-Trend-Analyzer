import type { AnalysisRequest, AnalysisResponse } from "./api/types";

export const MAX_SAVED_RESULTS = 20;

// Exact inputs, not rounded copies: a miss is harmless, reusing a different point is not.
export function cacheKey(request: AnalysisRequest): string {
  const { region, period } = request;
  const place =
    region.kind === "point"
      ? [region.kind, region.latitude, region.longitude]
      : [region.kind, region.south, region.west, region.north, region.east];
  return JSON.stringify([request.hazard, place, period.start_year, period.end_year]);
}

export class ResultCache {
  private readonly entries = new Map<string, AnalysisResponse>();
  private readonly limit: number;

  constructor(limit = MAX_SAVED_RESULTS) {
    this.limit = limit;
  }

  get size(): number {
    return this.entries.size;
  }

  get(request: AnalysisRequest, now: number): AnalysisResponse | null {
    const key = cacheKey(request);
    const saved = this.entries.get(key);
    if (!saved) return null;
    this.entries.delete(key);
    if (!(Date.parse(saved.cache.expires_at) > now)) return null;
    this.entries.set(key, saved);
    return { ...saved, region: { ...saved.region, label: request.region.label } };
  }

  set(request: AnalysisRequest, result: AnalysisResponse): void {
    const key = cacheKey(request);
    this.entries.delete(key);
    this.entries.set(key, result);
    while (this.entries.size > this.limit) {
      this.entries.delete(this.entries.keys().next().value as string);
    }
  }
}
