import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, searchRegions } from "../api/client";
import type { RegionResult } from "../api/types";

export type SearchState =
  | { phase: "idle" }
  | { phase: "loading"; query: string }
  | { phase: "done"; query: string; results: RegionResult[] }
  | { phase: "error"; query: string; error: ApiError };

type Searcher = (query: string, signal: AbortSignal) => Promise<RegionResult[]>;

export function useRegionSearch(search: Searcher = searchRegions) {
  const [state, setState] = useState<SearchState>({ phase: "idle" });
  const active = useRef<AbortController | null>(null);
  const token = useRef(0);

  const clear = useCallback(() => {
    token.current += 1;
    active.current?.abort();
    active.current = null;
    setState({ phase: "idle" });
  }, []);

  const run = useCallback(
    async (query: string) => {
      active.current?.abort();
      const current = ++token.current;
      const controller = new AbortController();
      active.current = controller;
      setState({ phase: "loading", query });
      try {
        const results = await search(query, controller.signal);
        if (current === token.current) setState({ phase: "done", query, results });
      } catch (error) {
        if (current === token.current && !controller.signal.aborted) {
          const apiError =
            error instanceof ApiError
              ? error
              : new ApiError({ status: 0, code: "UNKNOWN", message: "Search failed.", retryable: true });
          setState({ phase: "error", query, error: apiError });
        }
      } finally {
        if (active.current === controller) active.current = null;
      }
    },
    [search],
  );

  useEffect(() => {
    const tokens = token;
    const pending = active;
    return () => {
      tokens.current += 1;
      pending.current?.abort();
    };
  }, []);

  return { state, run, clear };
}
