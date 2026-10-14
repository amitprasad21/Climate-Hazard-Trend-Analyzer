"""Spatial sampling and cosine-latitude weighted regional aggregation (methodology)."""

import math
from collections.abc import Sequence
from typing import NamedTuple

from app.ingestion import DailySeries, DailyValue
from app.schemas import BoxRegion, PointRegion, _canonical_coordinate


class SampleCoordinate(NamedTuple):
    latitude: float
    longitude: float


CellKey = tuple[tuple[float, float] | None, float | None, tuple[float, float]]


def sample_centers(region: PointRegion | BoxRegion) -> list[SampleCoordinate]:
    """Calculate sample points for a region: 1 point or 3x3 (9) cell centers."""
    if region.kind == "point":
        return [SampleCoordinate(region.latitude, region.longitude)]

    delta_lat = region.north - region.south
    delta_lon = region.east - region.west

    lat_centers = [
        _canonical_coordinate(region.south + (2 * i + 1) * delta_lat / 6.0)
        for i in range(3)
    ]
    lon_centers = [
        _canonical_coordinate(region.west + (2 * j + 1) * delta_lon / 6.0)
        for j in range(3)
    ]

    return [
        SampleCoordinate(lat, lon)
        for lat in lat_centers
        for lon in lon_centers
    ]


def cosine_weights(coordinates: Sequence[SampleCoordinate]) -> list[float]:
    """Calculate normalized weights proportional to cosine(latitude). Sum of weights is 1.0."""
    if len(coordinates) == 1:
        return [1.0]

    raw_weights = [math.cos(math.radians(coord.latitude)) for coord in coordinates]
    total_weight = sum(raw_weights)
    if total_weight <= 0:
        return [1.0 / len(coordinates)] * len(coordinates)
    return [w / total_weight for w in raw_weights]


def aggregate_regional_days(
    coordinates: Sequence[SampleCoordinate],
    weights: Sequence[float],
    series_by_point: Sequence[DailySeries],
) -> tuple[tuple[DailyValue, ...], int]:
    """Aggregate multiple daily series into a single regional daily series.

    Combines weights for sample centers resolving to the same source grid cell and elevation.
    Enforces disjoint quality priority per methodology:
    any invalid sample makes regional day invalid; otherwise any missing sample makes it missing.
    """
    assert len(coordinates) == len(weights) == len(series_by_point)
    if len(series_by_point) == 1:
        return series_by_point[0].days, 1

    # Group sample points by grid cell: (resolved, elevation_m) if resolved is known,
    # else (requested, elevation_m) for providers like NASA POWER that do not report resolved.
    groups: dict[CellKey, list[int]] = {}
    for idx, (coord, series) in enumerate(zip(coordinates, series_by_point, strict=False)):
        if series.resolved is not None:
            key = (series.resolved, series.elevation_m, series.resolved)
        else:
            key = (None, series.elevation_m, (coord.latitude, coord.longitude))
        groups.setdefault(key, []).append(idx)

    unique_cell_count = len(groups)

    # For each unique cell, combine the weights of its sample points
    unique_cells: list[tuple[DailySeries, float]] = []
    for indices in groups.values():
        first_idx = indices[0]
        combined_weight = sum(weights[i] for i in indices)
        unique_cells.append((series_by_point[first_idx], combined_weight))

    first_series = series_by_point[0]
    expected_days = [d.day for d in first_series.days]
    day_maps = [{d.day: d for d in s.days} for s, _ in unique_cells]

    aggregated_days: list[DailyValue] = []
    for day_date in expected_days:
        day_records = [dmap.get(day_date) for dmap in day_maps]

        has_none = any(rec is None for rec in day_records)
        has_invalid = has_none or any(
            rec.quality == "invalid" or (rec.tmax_c is None and rec.quality != "missing")
            for rec in day_records
            if rec is not None
        )
        has_missing = any(
            rec.quality == "missing" or rec.tmax_c is None
            for rec in day_records
            if rec is not None
        )
        has_duplicate = any(rec.duplicate for rec in day_records if rec is not None)

        if has_invalid:
            aggregated_days.append(DailyValue(day_date, None, "invalid", duplicate=has_duplicate))
        elif has_missing:
            aggregated_days.append(DailyValue(day_date, None, "missing", duplicate=has_duplicate))
        else:
            weighted_tmax = sum(
                w * rec.tmax_c for rec, (_, w) in zip(day_records, unique_cells, strict=False)
            )  # type: ignore[operator]
            aggregated_days.append(
                DailyValue(day_date, weighted_tmax, "valid", duplicate=has_duplicate)
            )

    return tuple(aggregated_days), unique_cell_count
