import type {
  AnalysisRequest,
  AnalysisResponse,
  ErrorDetail,
  ErrorResponse,
  RegionSearch,
} from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
export const ANALYSIS_TIMEOUT_MS = 100_000;
export const SEARCH_TIMEOUT_MS = 20_000;
// Free hosting can take about a minute to wake a sleeping server.
export const HEALTH_TIMEOUT_MS = 90_000;

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly retryable: boolean;
  readonly requestId: string | null;
  readonly details: ErrorDetail[];
  readonly retryAfterSeconds: number | null;

  constructor(options: {
    status: number;
    code: string;
    message: string;
    retryable: boolean;
    requestId?: string | null;
    details?: ErrorDetail[];
    retryAfterSeconds?: number | null;
  }) {
    super(options.message);
    this.name = "ApiError";
    this.status = options.status;
    this.code = options.code;
    this.retryable = options.retryable;
    this.requestId = options.requestId ?? null;
    this.details = options.details ?? [];
    this.retryAfterSeconds = options.retryAfterSeconds ?? null;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isErrorResponse(value: unknown): value is ErrorResponse {
  if (!isRecord(value) || !isRecord(value.error)) return false;
  const { code, message, retryable, details } = value.error;
  return (
    typeof code === "string" &&
    typeof message === "string" &&
    typeof retryable === "boolean" &&
    Array.isArray(details)
  );
}

export function isAnalysisResponse(value: unknown): value is AnalysisResponse {
  return (
    isRecord(value) &&
    value.contract_version === "0.2" &&
    isRecord(value.summary) &&
    isRecord(value.source) &&
    isRecord(value.data_quality) &&
    isRecord(value.cache) &&
    Array.isArray(value.annual) &&
    Array.isArray(value.events) &&
    Array.isArray(value.insights) &&
    Array.isArray(value.warnings)
  );
}

function isRegionSearch(value: unknown): value is RegionSearch {
  return isRecord(value) && Array.isArray(value.results);
}

function retryAfter(header: string | null): number | null {
  return header && /^\d+$/.test(header) ? Number(header) : null;
}

function withTimeout(signal: AbortSignal, timeoutMs: number): AbortSignal {
  return AbortSignal.any([signal, AbortSignal.timeout(timeoutMs)]);
}

async function request<T>(
  path: string,
  init: RequestInit,
  timeoutMs: number,
  isExpected: (value: unknown) => value is T,
): Promise<T> {
  const signal = init.signal ?? new AbortController().signal;
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...init, signal: withTimeout(signal, timeoutMs) });
  } catch (error) {
    if (signal.aborted) throw error;
    const timedOut = error instanceof DOMException && error.name === "TimeoutError";
    throw new ApiError({
      status: 0,
      code: timedOut ? "CLIENT_TIMEOUT" : "NETWORK_ERROR",
      message: timedOut
        ? "The analysis took too long to respond."
        : "The analysis service could not be reached.",
      retryable: true,
    });
  }
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (response.ok && isExpected(body)) return body;
  if (isErrorResponse(body)) {
    throw new ApiError({
      status: response.status,
      code: body.error.code,
      message: body.error.message,
      retryable: body.error.retryable,
      requestId: body.error.request_id,
      details: body.error.details,
      retryAfterSeconds: retryAfter(response.headers.get("Retry-After")),
    });
  }
  // Gateways and proxies can return HTML or empty bodies; never surface them verbatim.
  throw new ApiError({
    status: response.status,
    code: response.ok ? "UNEXPECTED_RESPONSE" : `HTTP_${response.status}`,
    message: response.ok
      ? "The service returned a response this page cannot read."
      : "The service could not complete the request.",
    retryable: response.status >= 500 || response.status === 429,
    retryAfterSeconds: retryAfter(response.headers.get("Retry-After")),
  });
}

export function analyzeHeatwaves(body: AnalysisRequest, signal: AbortSignal) {
  return request(
    "/api/v1/analyses/heatwaves",
    {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
      signal,
    },
    ANALYSIS_TIMEOUT_MS,
    isAnalysisResponse,
  );
}

export function searchRegions(query: string, signal: AbortSignal) {
  const params = new URLSearchParams({ q: query });
  return request(
    `/api/v1/regions/search?${params}`,
    { method: "GET", headers: { Accept: "application/json" }, signal },
    SEARCH_TIMEOUT_MS,
    isRegionSearch,
  ).then((body) => body.results);
}

export type ServerInfo = { earliestStartYear: number | null };

function isHealth(value: unknown): value is { status: "ok"; earliest_start_year?: unknown } {
  return isRecord(value) && value.status === "ok";
}

// The year is additive in contract 0.2, so an older backend without it is not an error.
export function checkHealth(signal: AbortSignal): Promise<ServerInfo> {
  return request(
    "/api/v1/health",
    { method: "GET", headers: { Accept: "application/json" }, signal },
    HEALTH_TIMEOUT_MS,
    isHealth,
  ).then((health) => ({
    earliestStartYear: Number.isInteger(health.earliest_start_year) ? (health.earliest_start_year as number) : null,
  }));
}
