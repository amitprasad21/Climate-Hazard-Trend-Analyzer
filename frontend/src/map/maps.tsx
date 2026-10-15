import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useId, useRef, useState } from "react";
import type { LatLon } from "./geometry";
import type { MapPickerProps, ResultMapProps } from "./types";

const TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
const ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const WORLD: L.LatLngBoundsExpression = [[-90, -180], [90, 180]];
const START_VIEW: { center: LatLon; zoom: number } = { center: [20, 0], zoom: 2 };
const POINT_ZOOM = 8;

function createMap(element: HTMLElement): L.Map {
  const map = L.map(element, {
    scrollWheelZoom: false,
    maxBounds: WORLD,
    maxBoundsViscosity: 1,
    minZoom: 1,
    attributionControl: false,
  });
  // The default prefix includes a colored flag; the design is grayscale only.
  L.control.attribution({ prefix: '<a href="https://leafletjs.com">Leaflet</a>' }).addTo(map);
  L.tileLayer(TILE_URL, { attribution: ATTRIBUTION, maxZoom: 19, noWrap: true }).addTo(map);
  return map;
}

export function ResultMap({ shapes, label }: ResultMapProps) {
  const element = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!element.current) return;
    const map = createMap(element.current);
    if (shapes.box) L.rectangle(shapes.box, { className: "map-box", interactive: false }).addTo(map);
    for (const cell of shapes.cells) L.rectangle(cell, { className: "map-cell", interactive: false }).addTo(map);
    for (const point of shapes.resolved) {
      L.circleMarker(point, { radius: 6, className: "map-resolved", interactive: false }).addTo(map);
    }
    for (const point of shapes.requested) {
      L.circleMarker(point, { radius: 4, className: "map-requested", interactive: false }).addTo(map);
    }
    map.fitBounds(shapes.view, { padding: [16, 16], maxZoom: 10 });
    return () => {
      map.remove();
    };
  }, [shapes]);
  return <div ref={element} className="leaflet-map" role="region" aria-label={`Map of ${label}`} />;
}

export function MapPicker({ mode, point, box, onPickPoint, onPickBox }: MapPickerProps) {
  const element = useRef<HTMLDivElement>(null);
  const hintId = useId();
  const [map, setMap] = useState<L.Map | null>(null);
  const [anchor, setAnchor] = useState<LatLon | null>(null);
  const [anchorMode, setAnchorMode] = useState(mode);
  const latest = useRef({ mode, anchor, onPickPoint, onPickBox });
  const pickedHere = useRef(false);
  const shownKey = useRef<string | null>(null);
  if (anchorMode !== mode) {
    setAnchorMode(mode);
    setAnchor(null);
  }

  useEffect(() => {
    latest.current = { mode, anchor, onPickPoint, onPickBox };
  });

  useEffect(() => {
    if (!element.current) return;
    const created = createMap(element.current);
    created.setView(START_VIEW.center, START_VIEW.zoom);
    created.on("click", (event: L.LeafletMouseEvent) => {
      const { lat, lng } = event.latlng;
      const current = latest.current;
      if (current.mode === "point") {
        pickedHere.current = true;
        current.onPickPoint(lat, lng);
      } else if (current.anchor) {
        pickedHere.current = true;
        current.onPickBox(current.anchor, [lat, lng]);
        setAnchor(null);
      } else {
        setAnchor([lat, lng]);
      }
    });
    setMap(created);
    return () => {
      created.remove();
    };
  }, []);

  useEffect(() => {
    if (!map) return;
    const layer = L.layerGroup().addTo(map);
    const shape = mode === "point" ? point : box;
    // Places chosen by typing, search or a city button move the map; picks made on the map do not.
    const key = JSON.stringify(shape);
    const external = !pickedHere.current;
    pickedHere.current = false;
    const moved = key !== shownKey.current;
    shownKey.current = key;
    if (mode === "point" && point) {
      L.circleMarker(point, { radius: 5, className: "map-requested", interactive: false }).addTo(layer);
      if (moved && external) map.setView(point, Math.max(map.getZoom(), POINT_ZOOM));
    }
    if (mode === "bbox" && box) {
      L.rectangle(box, { className: "map-box", interactive: false }).addTo(layer);
      if (moved && external) map.fitBounds(box, { padding: [16, 16] });
    }
    if (mode === "bbox" && anchor) {
      L.circleMarker(anchor, { radius: 4, className: "map-anchor", interactive: false }).addTo(layer);
    }
    return () => {
      layer.remove();
    };
  }, [map, mode, point, box, anchor]);

  function pickCentre() {
    if (!map) return;
    const centre = map.getCenter();
    pickedHere.current = true;
    onPickPoint(centre.lat, centre.lng);
  }

  return (
    <div className="map-picker">
      <div
        ref={element}
        className="leaflet-map"
        role="region"
        aria-label="Map for choosing the location"
        aria-describedby={hintId}
      />
      <div className="map-picker-footer">
        <p id={hintId} className="hint">
          {mode === "point"
            ? "Click the map to set the point, or pan with the arrow keys and choose Use map centre."
            : anchor
              ? "Now click the opposite corner of the box."
              : "Click one corner of the box, then the opposite corner. Edges can also be typed below."}
        </p>
        {mode === "point" && (
          <button type="button" className="secondary-action" onClick={pickCentre} disabled={!map}>
            Use map centre
          </button>
        )}
      </div>
    </div>
  );
}
