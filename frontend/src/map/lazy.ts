import { lazy } from "react";
import type { MapComponents } from "./types";

// Leaflet and its stylesheet load in their own chunk, after the page is interactive.
export const lazyMaps: MapComponents = {
  ResultMap: lazy(() => import("./maps").then((module) => ({ default: module.ResultMap }))),
  MapPicker: lazy(() => import("./maps").then((module) => ({ default: module.MapPicker }))),
};
