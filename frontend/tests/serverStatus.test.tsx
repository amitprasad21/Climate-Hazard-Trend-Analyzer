import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { DashboardPage } from "../src/DashboardPage";

type Pending = { resolve: () => void; reject: (error: unknown) => void; signal: AbortSignal };

let checks: Pending[];
const checkServer = vi.fn(
  (signal: AbortSignal) =>
    new Promise<void>((resolve, reject) => {
      checks.push({ resolve, reject, signal });
    }),
);

beforeEach(() => {
  checks = [];
  checkServer.mockClear();
  vi.useFakeTimers();
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

const status = () => document.querySelector(".server-status")?.textContent ?? "";

it("pings the server once on load and stays quiet when it answers quickly", async () => {
  render(<DashboardPage checkServer={checkServer} />);
  expect(checkServer).toHaveBeenCalledTimes(1);
  await act(async () => {
    checks[0].resolve();
  });
  await act(async () => {
    vi.advanceTimersByTime(5000);
  });
  expect(status()).toBe("");
});

it("explains a slow wake-up and confirms when the server is ready", async () => {
  render(<DashboardPage checkServer={checkServer} />);
  expect(status()).toBe("");
  await act(async () => {
    vi.advanceTimersByTime(1600);
  });
  expect(status()).toMatch(/Waking up the analysis server/);
  expect(status()).toMatch(/up to a minute/);
  await act(async () => {
    checks[0].resolve();
  });
  expect(status()).toBe("Analysis server ready.");
});

it("reports an unreachable server without blocking the form", async () => {
  render(<DashboardPage checkServer={checkServer} />);
  await act(async () => {
    checks[0].reject(new Error("down"));
  });
  expect(status()).toMatch(/not responding/);
  expect(screen.getByRole("button", { name: "Analyze trends" })).toHaveProperty("disabled", false);
});

it("aborts the ping on unmount and sends none without a checker", () => {
  const { unmount } = render(<DashboardPage checkServer={checkServer} />);
  unmount();
  expect(checks[0].signal.aborted).toBe(true);
  render(<DashboardPage />);
  expect(checkServer).toHaveBeenCalledTimes(1);
  expect(status()).toBe("");
});
