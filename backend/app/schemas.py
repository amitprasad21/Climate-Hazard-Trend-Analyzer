"""Wire schemas for INTEGRATION_CONTRACT 0.2; validation is pure and performs no I/O."""

import re
import unicodedata
from collections.abc import Iterable, Mapping
from datetime import date, datetime, timedelta
from itertools import islice
from typing import Annotated, Any, Literal, NamedTuple, Self

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

CONTRACT_VERSION = "0.2"
EARLIEST_YEAR = 1940
ProviderName = Literal["nasa_power", "open_meteo"]
MAX_PERIOD_YEARS = 50
MAX_BBOX_SPAN = 2.0
MIN_BBOX_LATITUDE = -85.0
MAX_BBOX_LATITUDE = 85.0
AVAILABILITY_LAG = timedelta(days=7)
MAX_ERROR_DETAILS = 20
SAFE_SEGMENT = re.compile(r"[A-Za-z0-9_]{1,64}")
REGION_KINDS = {"point", "bbox"}
FIXED_MESSAGES = {
    "missing": "Field is required",
    "extra_forbidden": "Unknown field",
    "json_invalid": "Malformed JSON",
    "literal_error": "Unsupported value",
    "union_tag_invalid": "Unsupported region kind",
    "union_tag_not_found": "Region kind is required",
    "finite_number": "Must be a finite number",
    "float_type": "Must be a number",
    "int_type": "Must be an integer",
    "string_type": "Must be text",
    "string_unicode": "Must be valid Unicode text",
    "model_type": "Must be an object",
    "model_attributes_type": "Must be an object",
    "string_too_short": "Must not be empty",
}


def _canonical_coordinate(value: float) -> float:
    # Adding 0.0 turns -0.0 into 0.0 so equal locations share one cache identity.
    return round(value, 4) + 0.0


def _utc(value: datetime) -> datetime:
    if value.utcoffset() != timedelta(0):
        raise ValueError("Timestamp must be UTC")
    return value


def _plain_text(value: str) -> str:
    if any(unicodedata.category(char) == "Cc" for char in value):
        raise ValueError("Must not contain control characters")
    return value


Latitude = Annotated[
    float, Field(ge=-90, le=90, allow_inf_nan=False), AfterValidator(_canonical_coordinate)
]
Longitude = Annotated[
    float, Field(ge=-180, le=180, allow_inf_nan=False), AfterValidator(_canonical_coordinate)
]
Label = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
    AfterValidator(_plain_text),
]


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, hide_input_in_errors=True)


class PointRegion(StrictModel):
    kind: Literal["point"]
    label: Label
    latitude: Latitude
    longitude: Longitude


class BoxRegion(StrictModel):
    kind: Literal["bbox"]
    label: Label
    south: Latitude
    west: Longitude
    north: Latitude
    east: Longitude


class Period(StrictModel):
    start_year: int
    end_year: int

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.start_year > self.end_year:
            raise ValueError("start_year must not be after end_year")
        return self


class AnalysisRequest(StrictModel):
    hazard: Literal["heatwave"]
    region: Annotated[PointRegion | BoxRegion, Field(discriminator="kind")]
    period: Period


class SourceProfile(NamedTuple):
    model: Literal["MERRA-2", "ERA5"]
    grid_degrees: tuple[float, float]
    first_year: int
    attribution_url: str
    reports_grid_cell: bool


# Contract 0.2 table; any other provider/model/grid/attribution combination is rejected.
SOURCE_PROFILES: dict[str, SourceProfile] = {
    "nasa_power": SourceProfile(
        "MERRA-2", (0.5, 0.625), 1981, "https://power.larc.nasa.gov/", reports_grid_cell=False
    ),
    "open_meteo": SourceProfile(
        "ERA5", (0.25, 0.25), 1940, "https://open-meteo.com/", reports_grid_cell=True
    ),
}


class OutputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Point(OutputModel):
    latitude: Latitude
    longitude: Longitude


class SamplePoint(OutputModel):
    requested: Point
    resolved: Point | None
    elevation_m: Annotated[float, Field(allow_inf_nan=False)] | None


class GridDegrees(OutputModel):
    latitude: Annotated[float, Field(gt=0, le=5)]
    longitude: Annotated[float, Field(gt=0, le=5)]


class Source(OutputModel):
    provider: ProviderName
    model: Literal["MERRA-2", "ERA5"]
    dataset_kind: Literal["reanalysis"]
    grid_degrees: GridDegrees
    time_standard: Literal["UTC"]
    temperature_unit: Literal["celsius"]
    normalization_version: Literal["daily-tmax-v1"]
    sample_points: Annotated[list[SamplePoint], Field(min_length=1, max_length=9)]
    attribution_url: str
    retrieved_at: Annotated[AwareDatetime, AfterValidator(_utc)]

    @model_validator(mode="after")
    def matches_profile(self) -> Self:
        profile = SOURCE_PROFILES[self.provider]
        grid = (self.grid_degrees.latitude, self.grid_degrees.longitude)
        if (self.model, grid, self.attribution_url) != (
            profile.model,
            profile.grid_degrees,
            profile.attribution_url,
        ):
            raise ValueError("Source metadata does not match the provider profile")
        if not profile.reports_grid_cell and any(p.resolved for p in self.sample_points):
            raise ValueError("This provider does not identify a resolved grid cell")
        return self


UtcDatetime = Annotated[AwareDatetime, AfterValidator(_utc)]
Nullable = Annotated[float, Field(allow_inf_nan=False)] | None


class Coverage(OutputModel):
    expected_days: int
    valid_days: int
    missing_days: int
    invalid_days: int
    duplicate_dates: int
    coverage_fraction: Annotated[float, Field(ge=0, le=1)]

    @model_validator(mode="after")
    def disjoint_counts(self) -> Self:
        if self.valid_days + self.missing_days + self.invalid_days != self.expected_days:
            raise ValueError("valid + missing + invalid must equal expected")
        return self


class YearCoverage(Coverage):
    year: int
    eligible: bool
    excluded_reasons: list[str]


class Event(OutputModel):
    start_date: date
    end_date: date
    duration_days: int
    mean_excess_c: float
    max_excess_c: float
    boundary_censored: bool

    @model_validator(mode="after")
    def inclusive_duration(self) -> Self:
        if (self.end_date - self.start_date).days + 1 != self.duration_days:
            raise ValueError("duration_days must equal the inclusive date span")
        return self


class Annual(OutputModel):
    year: int
    eligible: bool
    coverage_fraction: float
    event_count: int | None
    mean_duration_days: Nullable
    max_duration_days: int | None
    heatwave_days: int | None
    mean_tmax_c: Nullable
    tmax_anomaly_c: Nullable
    frequency_rolling_5y: Nullable


class ResultWarning(OutputModel):
    code: str
    message: str
    years: list[int]


class Evidence(OutputModel):
    metric: str
    value: float
    unit: str
    years: list[int]


class Insight(OutputModel):
    code: str
    text: str
    evidence: list[Evidence]


class Summary(OutputModel):
    event_count: int
    mean_duration_days: Nullable
    threshold_c: float
    trend_direction: Literal["increasing", "decreasing", "flat", "insufficient_data"]
    frequency_slope_per_year: Nullable
    trend_year_count: int


class Methodology(OutputModel):
    version: Literal["heatwave-v1"] = "heatwave-v1"
    baseline_start: Literal["1991-01-01"] = "1991-01-01"
    baseline_end: Literal["2020-12-31"] = "2020-12-31"
    percentile: Literal[95] = 95
    percentile_method: Literal["linear"] = "linear"
    minimum_consecutive_days: Literal[3] = 3
    comparison: Literal["strictly_greater"] = "strictly_greater"
    daily_timezone: Literal["UTC"] = "UTC"
    aggregation: Literal["point", "nine_point_cosine_weighted_mean"] = "point"
    anomaly_reference: Literal["baseline_mean_daily_maximum"] = "baseline_mean_daily_maximum"
    trend_method: Literal["ordinary_least_squares_descriptive"] = (
        "ordinary_least_squares_descriptive"
    )
    significance_tested: Literal[False] = False


class DataQuality(OutputModel):
    baseline: Coverage
    analysis: Coverage
    years: list[YearCoverage]
    eligible_year_count: int


class CacheInfo(OutputModel):
    hit: bool
    generated_at: UtcDatetime
    expires_at: UtcDatetime


class AnalysisResponse(OutputModel):
    contract_version: Literal["0.2"]
    request_id: str
    region: Annotated[PointRegion | BoxRegion, Field(discriminator="kind")]
    period: Period
    status: Literal["complete", "partial"]
    summary: Summary
    annual: list[Annual]
    events: list[Event]
    insights: list[Insight]
    warnings: list[ResultWarning]
    methodology: Methodology
    data_quality: DataQuality
    source: Source
    cache: CacheInfo

    @model_validator(mode="after")
    def invariants(self) -> Self:
        years = list(range(self.period.start_year, self.period.end_year + 1))
        if [row.year for row in self.annual] != years:
            raise ValueError("annual must hold one sorted row per requested year")
        counted = sum(row.event_count or 0 for row in self.annual if row.eligible)
        if not self.summary.event_count == len(self.events) == counted:
            raise ValueError("event counts disagree")
        if any(
            a.end_date >= b.start_date for a, b in zip(self.events, self.events[1:], strict=False)
        ):
            raise ValueError("events must be sorted and non-overlapping")
        if self.data_quality.eligible_year_count != self.summary.trend_year_count:
            raise ValueError("eligible year counts disagree")
        return self


SearchQuery = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=100),
    AfterValidator(_plain_text),
]


class RegionResult(OutputModel):
    id: int
    name: str
    admin1: str | None
    country: str
    country_code: str
    latitude: Latitude
    longitude: Longitude


class RegionSearch(OutputModel):
    results: Annotated[list[RegionResult], Field(max_length=10)]


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    api_version: Literal["v1"] = "v1"
    earliest_start_year: int


class Readiness(BaseModel):
    status: Literal["ok"] = "ok"
    api_version: Literal["v1"] = "v1"
    database: Literal["available"] = "available"


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str
    details: list[ErrorDetail]
    retryable: bool


class ErrorResponse(BaseModel):
    error: ErrorBody


class UnsupportedRequest(Exception):
    def __init__(self, code: str, message: str, details: list[ErrorDetail]):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def last_complete_year(today: date) -> int:
    available = today - AVAILABILITY_LAG
    return available.year if (available.month, available.day) == (12, 31) else available.year - 1


def ensure_supported(request: AnalysisRequest, today: date) -> None:
    if request.region.kind == "bbox":
        box = request.region
        region_details = []
        if box.south < MIN_BBOX_LATITUDE or box.north > MAX_BBOX_LATITUDE:
            region_details.append(
                ErrorDetail(
                    field="region",
                    message=f"Latitude must be between {MIN_BBOX_LATITUDE} and {MAX_BBOX_LATITUDE}",
                )
            )
        if box.south >= box.north:
            region_details.append(
                ErrorDetail(
                    field="region.south",
                    message="South latitude must be strictly less than north latitude",
                )
            )
        if box.west >= box.east:
            region_details.append(
                ErrorDetail(
                    field="region.west",
                    message="West longitude must be strictly less than east longitude",
                )
            )
        if round(box.north - box.south, 4) > MAX_BBOX_SPAN:
            region_details.append(
                ErrorDetail(
                    field="region",
                    message=f"Latitude span must be at most {MAX_BBOX_SPAN} degrees",
                )
            )
        if round(box.east - box.west, 4) > MAX_BBOX_SPAN:
            region_details.append(
                ErrorDetail(
                    field="region",
                    message=f"Longitude span must be at most {MAX_BBOX_SPAN} degrees",
                )
            )
        if region_details:
            raise UnsupportedRequest(
                "UNSUPPORTED_REGION", "Requested bounding box is not supported", region_details
            )
    elif request.region.kind != "point":
        detail = ErrorDetail(field="region.kind", message="Unsupported region kind")
        raise UnsupportedRequest(
            "UNSUPPORTED_REGION", "Only point and bbox regions are supported", [detail]
        )

    period, latest = request.period, last_complete_year(today)
    details = []
    if period.start_year < EARLIEST_YEAR:
        message = f"Earliest supported year is {EARLIEST_YEAR}"
        details.append(ErrorDetail(field="period.start_year", message=message))
    if period.end_year > latest:
        message = f"Latest complete year is {latest}"
        details.append(ErrorDetail(field="period.end_year", message=message))
    if period.end_year - period.start_year + 1 > MAX_PERIOD_YEARS:
        message = f"At most {MAX_PERIOD_YEARS} years can be analyzed"
        details.append(ErrorDetail(field="period", message=message))
    if details:
        raise UnsupportedRequest("UNSUPPORTED_PERIOD", "Requested period is not supported", details)


def _field(error: Mapping[str, Any]) -> str:
    if error["type"] == "json_invalid":
        return "body"
    parts = list(error["loc"])
    if parts[:1] in (["body"], ["query"]):
        parts = parts[1:]
    # Discriminated unions insert the tag into loc; paths mirror the wire shape instead.
    if len(parts) > 1 and parts[0] == "region" and parts[1] in REGION_KINDS:
        del parts[1]
    safe = (str(p) if isinstance(p, int) or SAFE_SEGMENT.fullmatch(p) else "*" for p in parts)
    return ".".join(safe) or "body"


def _message(error: Mapping[str, Any]) -> str:
    # Pydantic messages can echo input (for example union tags), so only fixed text is returned.
    ctx = error.get("ctx") or {}
    match error["type"]:
        case "value_error":
            return str(ctx.get("error", "Invalid value"))
        case "greater_than_equal":
            return f"Must be at least {ctx['ge']}"
        case "less_than_equal":
            return f"Must be at most {ctx['le']}"
        case "string_too_long":
            return f"Must be at most {ctx['max_length']} characters"
    return FIXED_MESSAGES.get(error["type"], "Invalid value")


def validation_details(errors: Iterable[Mapping[str, Any]]) -> list[ErrorDetail]:
    return [
        ErrorDetail(field=_field(error), message=_message(error))
        for error in islice(errors, MAX_ERROR_DETAILS)
    ]
