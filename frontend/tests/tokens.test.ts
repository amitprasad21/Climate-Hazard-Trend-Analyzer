import { expect, it } from "vitest";
import design from "../docs/design.md?raw";
import tokens from "../src/styles/tokens.css?raw";

const sources = import.meta.glob("../src/**/*.{css,ts,tsx}", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

const COLOR_LITERAL = /#[0-9a-f]{3,8}\b|rgba?\(/i;

function colorMap(entries: IterableIterator<RegExpMatchArray>) {
  return new Map([...entries].map(([, name, value]) => [name, value.trim().toUpperCase()]));
}

const designColors = colorMap(design.matchAll(/^\| `(--color-[a-z0-9-]+)` \| `([^`]+)` \|/gm));
const cssColors = colorMap(tokens.matchAll(/(--color-[a-z0-9-]+):\s*([^;]+);/g));

function isGrayscale(value: string) {
  const hex = value.match(/^#([0-9A-F]{2})([0-9A-F]{2})([0-9A-F]{2})$/);
  if (hex) return hex[1] === hex[2] && hex[2] === hex[3];
  const rgba = value.match(/^RGBA\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)$/);
  return rgba !== null && rgba[1] === rgba[2] && rgba[2] === rgba[3];
}

it("mirrors every canonical design color token exactly", () => {
  expect(designColors.size).toBeGreaterThanOrEqual(22);
  expect(cssColors).toEqual(designColors);
});

it("uses grayscale values only", () => {
  for (const [name, value] of cssColors) expect([name, isGrayscale(value)]).toEqual([name, true]);
});

it("keeps color literals out of every source file except the token sheet", () => {
  expect(Object.keys(sources).length).toBeGreaterThanOrEqual(4);
  expect(Object.values(sources).every((text) => text.length > 0)).toBe(true);
  const offenders = Object.entries(sources)
    .filter(([path, text]) => !path.endsWith("/tokens.css") && COLOR_LITERAL.test(text))
    .map(([path]) => path);
  expect(offenders).toEqual([]);
});
