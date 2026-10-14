import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, analyzeHeatwaves } from "../api/client";
import type { AnalysisRequest, AnalysisResponse } from "../api/types";

export type AnalysisState =
  | { phase: "idle" }
  | { phase: "loading"; request: AnalysisRequest }
  | { phase: "success"; request: AnalysisRequest; result: AnalysisResponse }
  | { phase: "error"; request: AnalysisRequest; error: ApiError };

type Runner = (request: AnalysisRequest, signal: AbortSignal) => Promise<AnalysisResponse>;

function asApiError(error: unknown): ApiError {
  return error instanceof ApiError
    ? error
    : new ApiError({ status: 0, code: "UNKNOWN", message: "Something went wrong.", retryable: true });
}

export function useAnalysis(run: Runner = analyzeHeatwaves) {
  const [state, setState] = useState<AnalysisState>({ phase: "idle" });
  const active = useRef<AbortController | null>(null);
  const token = useRef(0);

  const cancel = useCallback(() => {
    token.current += 1;
    active.current?.abort();
    active.current = null;
    setState({ phase: "idle" });
  }, []);

  const submit = useCallback(
    async (request: AnalysisRequest) => {
      if (active.current) return;
      const current = ++token.current;
      const controller = new AbortController();
      active.current = controller;
      setState({ phase: "loading", request });
      try {
        const result = await run(request, controller.signal);
        if (current === token.current) setState({ phase: "success", request, result });
      } catch (error) {
        // Late or aborted responses must never replace newer state.
        if (current === token.current && !controller.signal.aborted) {
          setState({ phase: "error", request, error: asApiError(error) });
        }
      } finally {
        if (active.current === controller) active.current = null;
      }
    },
    [run],
  );

  useEffect(() => {
    const tokens = token;
    const pending = active;
    return () => {
      tokens.current += 1;
      pending.current?.abort();
    };
  }, []);

  return { state, submit, cancel };
}
