import type { ComponentType } from "react";
import type { Bounds, LatLon, MapShapes } from "./geometry";

export type ResultMapProps = { shapes: MapShapes; label: string };

export type MapPickerProps = {
  mode: "point" | "bbox";
  point: LatLon | null;
  box: Bounds | null;
  onPickPoint: (latitude: number, longitude: number) => void;
  onPickBox: (first: LatLon, second: LatLon) => void;
};

export type MapComponents = {
  ResultMap: ComponentType<ResultMapProps>;
  MapPicker: ComponentType<MapPickerProps>;
};
