import asyncio
from datetime import UTC, date, datetime

import pytest

from app.ingestion import DailySeries, DailyValue
from app.schemas import AnalysisRequest, BoxRegion, PointRegion
from app.services.analysis import cache_key
from app.spatial import (
    SampleCoordinate,
    aggregate_regional_days,
    cosine_weights,
    sample_centers,
)
from tests.fakes import service

TODAY = date(2026, 10, 14)


def test_point_sample_centers_and_weights():
    point = PointRegion(kind="point", label="Delhi", latitude=28.6139, longitude=77.209)
    centers = sample_centers(point)
    assert len(centers) == 1
    assert centers[0] == SampleCoordinate(28.6139, 77.209)
    weights = cosine_weights(centers)
    assert weights == [1.0]


def test_bbox_sample_centers_3x3_grid():
    # 1.2 degree lat span, 1.8 degree lon span
    box = BoxRegion(kind="bbox", label="Area", south=20.0, west=70.0, north=21.2, east=71.8)
    centers = sample_centers(box)
    assert len(centers) == 9

    # Check 3 latitude centers: 20 + (1/6, 3/6, 5/6)*1.2 = 20.2, 20.6, 21.0
    lats = sorted({c.latitude for c in centers})
    assert len(lats) == 3
    assert lats == [20.2, 20.6, 21.0]

    # Check 3 longitude centers: 70 + (1/6, 3/6, 5/6)*1.8 = 70.3, 70.9, 71.5
    lons = sorted({c.longitude for c in centers})
    assert len(lons) == 3
    assert lons == [70.3, 70.9, 71.5]


def test_cosine_weights_sum_to_one_and_reflect_latitude():
    box = BoxRegion(kind="bbox", label="Area", south=10.0, west=0.0, north=12.0, east=2.0)
    centers = sample_centers(box)
    weights = cosine_weights(centers)

    assert len(weights) == 9
    assert pytest.approx(sum(weights), abs=1e-9) == 1.0

    # In northern hemisphere, lower latitude has larger cosine (larger weight)
    # Row 0 (south): centers[0..2]
    # Row 1 (mid):   centers[3..5]
    # Row 2 (north): centers[6..8]
    assert weights[0] > weights[3] > weights[6]
    # Longitude does not affect cosine weight
    assert weights[0] == pytest.approx(weights[1]) == pytest.approx(weights[2])


def test_equator_symmetric_cosine_weights():
    # Box symmetric around equator: -1.2 to 1.2
    box = BoxRegion(kind="bbox", label="Equator", south=-1.2, west=-1.0, north=1.2, east=1.0)
    centers = sample_centers(box)
    weights = cosine_weights(centers)

    assert pytest.approx(sum(weights), abs=1e-9) == 1.0
    # South row and north row have equal absolute latitudes, so equal weights
    assert pytest.approx(weights[0]) == weights[6]
    assert pytest.approx(weights[1]) == weights[7]
    assert pytest.approx(weights[2]) == weights[8]
    # Mid row (lat = 0) has highest weight
    assert weights[3] > weights[0]


def test_aggregate_regional_days_priority_rules():
    coords = [
        SampleCoordinate(0.0, 0.0),
        SampleCoordinate(0.0, 1.0),
        SampleCoordinate(1.0, 0.0),
    ]
    weights = [0.4, 0.3, 0.3]
    d1 = date(2020, 1, 1)
    d2 = date(2020, 1, 2)
    d3 = date(2020, 1, 3)

    now = datetime(2026, 10, 14, tzinfo=UTC)

    # Series 1: all valid
    s1 = DailySeries("nasa_power", (0.0, 0.0), None, 100.0, now, (
        DailyValue(d1, 30.0, "valid"),
        DailyValue(d2, 30.0, "valid"),
        DailyValue(d3, 30.0, "valid"),
    ))
    # Series 2: d2 is missing
    s2 = DailySeries("nasa_power", (0.0, 1.0), None, 100.0, now, (
        DailyValue(d1, 32.0, "valid"),
        DailyValue(d2, None, "missing"),
        DailyValue(d3, 32.0, "valid"),
    ))
    # Series 3: d3 is invalid
    s3 = DailySeries("nasa_power", (1.0, 0.0), None, 100.0, now, (
        DailyValue(d1, 35.0, "valid"),
        DailyValue(d2, None, "missing"),  # also missing on d2
        DailyValue(d3, 999.0, "invalid"),
    ))

    aggregated, unique_count = aggregate_regional_days(coords, weights, [s1, s2, s3])
    assert unique_count == 3
    assert len(aggregated) == 3

    # d1: all valid -> weighted mean: 0.4*30 + 0.3*32 + 0.3*35 = 12 + 9.6 + 10.5 = 32.1
    assert aggregated[0].day == d1
    assert aggregated[0].quality == "valid"
    assert pytest.approx(aggregated[0].tmax_c) == 32.1

    # d2: missing takes effect (no invalid) -> regional day is missing
    assert aggregated[1].day == d2
    assert aggregated[1].quality == "missing"
    assert aggregated[1].tmax_c is None

    # d3: s3 is invalid -> regional day is invalid (invalid priority over valid)
    assert aggregated[2].day == d3
    assert aggregated[2].quality == "invalid"
    assert aggregated[2].tmax_c is None


def test_aggregate_regional_days_deduplicates_matching_grid_cells():
    coords = [
        SampleCoordinate(28.0, 77.0),
        SampleCoordinate(28.1, 77.1),
    ]
    weights = [0.5, 0.5]
    d1 = date(2020, 1, 1)
    now = datetime(2026, 10, 14, tzinfo=UTC)

    # Both resolve to same grid cell (28.0, 77.0) with elevation 200m
    s1 = DailySeries("open_meteo", (28.0, 77.0), (28.0, 77.0), 200.0, now, (
        DailyValue(d1, 34.0, "valid"),
    ))
    s2 = DailySeries("open_meteo", (28.1, 77.1), (28.0, 77.0), 200.0, now, (
        DailyValue(d1, 34.0, "valid"),
    ))

    aggregated, unique_count = aggregate_regional_days(coords, weights, [s1, s2])
    # Combined into 1 unique cell
    assert unique_count == 1
    assert len(aggregated) == 1
    assert aggregated[0].quality == "valid"
    assert pytest.approx(aggregated[0].tmax_c) == 34.0


def test_end_to_end_bbox_analysis_service():
    box = BoxRegion(kind="bbox", label="Delhi NCR", south=28.0, west=77.0, north=29.0, east=78.0)
    request = AnalysisRequest(
        hazard="heatwave",
        region=box,
        period={"start_year": 2001, "end_year": 2010},
    )

    svc, calls = service()
    response = asyncio.run(svc.analyze(request, "req-bbox-123"))

    assert response.contract_version == "0.3"
    assert response.request_id == "req-bbox-123"
    assert response.region.kind == "bbox"
    assert response.region.label == "Delhi NCR"
    assert response.methodology.aggregation == "nine_point_cosine_weighted_mean"
    assert len(response.source.sample_points) == 9

    # Verify warning for spatial approximation
    warning_codes = [w.code for w in response.warnings]
    assert "REGIONAL_APPROXIMATION" in warning_codes

    # Verify cache key reflects bbox
    k = cache_key(request, ("nasa_power",), 100.0)
    assert isinstance(k, str) and len(k) == 64

