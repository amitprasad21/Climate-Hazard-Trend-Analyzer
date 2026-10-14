import { useEffect, useState } from "react";

export type HealthCheck = (signal: AbortSignal) => Promise<void>;
export type ServerStatus = "idle" | "checking" | "waking" | "ready" | "unreachable";

export const SLOW_WAKE_MS = 1500;

export function useServerStatus(check?: HealthCheck) {
  const [status, setStatus] = useState<ServerStatus>(check ? "checking" : "idle");
  const [wasSlow, setWasSlow] = useState(false);

  useEffect(() => {
    if (!check) return;
    const controller = new AbortController();
    let settled = false;
    const timer = setTimeout(() => {
      if (!settled) {
        setWasSlow(true);
        setStatus("waking");
      }
    }, SLOW_WAKE_MS);
    check(controller.signal).then(
      () => {
        settled = true;
        setStatus("ready");
      },
      () => {
        settled = true;
        if (!controller.signal.aborted) setStatus("unreachable");
      },
    ).finally(() => clearTimeout(timer));
    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [check]);

  return { status, wasSlow };
}

export function serverStatusMessage(status: ServerStatus, wasSlow: boolean): string {
  switch (status) {
    case "waking":
      return "Waking up the analysis server. Free hosting pauses it when idle, so this can take up to a minute; you can fill in the form meanwhile.";
    case "ready":
      return wasSlow ? "Analysis server ready." : "";
    case "unreachable":
      return "The analysis server is not responding right now. You can still try an analysis; it will report a clear error if the server stays down.";
    default:
      return "";
  }
}
