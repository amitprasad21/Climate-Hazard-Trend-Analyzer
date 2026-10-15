"""Pure heatwave-v2 calculations (docs/climate-methodology.md); no I/O, clock or provider logic."""

import math
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from fractions import Fraction
from typing import Literal

from app.ingestion import DailyValue
from app.trend import MannKendall, lag1_autocorrelation, mann_kendall, serial_correlation_bound

METHOD_VERSION = "heatwave-v2"
BASELINE_START = date(1991, 1, 1)
BASELINE_END = date(2020, 12, 31)
PERCENTILE = 0.95
MIN_RUN_DAYS = 3
YEAR_MIN_VALID = Fraction(9, 10)
MONTH_MIN_VALID = Fraction(4, 5)
MIN_TREND_YEARS = 10
ROLLING_YEARS = 5
TrendDirection = Literal["increasing", "decreasing", "no_significant_trend", "insufficient_data"]


class InsufficientBaseline(Exception):
    def __init__(self, years: tuple[int, ...]):
        self.years = years
        super().__init__("Baseline years fail coverage gates")


class InsufficientData(Exception):
    pass


@dataclass(frozen=True)
class Coverage:
    expected_days: int
    valid_days: int
    missing_days: int
    invalid_days: int
    duplicate_dates: int

    @property
    def coverage_fraction(self) -> float:
        return self.valid_days / self.expected_days


@dataclass(frozen=True)
class YearCoverage(Coverage):
    year: int
    eligible: bool
    excluded_reasons: tuple[str, ...]


@dataclass(frozen=True)
class Event:
    start: date
    end: date
    duration_days: int
    mean_excess_c: float
    max_excess_c: float
    boundary_censored: bool


@dataclass(frozen=True)
class AnnualRow:
    year: int
    eligible: bool
    coverage_fraction: float
    event_count: int | None
    mean_duration_days: float | None
    max_duration_days: int | None
    heatwave_days: int | None
    mean_tmax_c: float | None
    tmax_anomaly_c: float | None
    frequency_rolling_5y: float | None


@dataclass(frozen=True)
class Notice:
    code: str
    message: str
    years: tuple[int, ...]


@dataclass(frozen=True)
class Evidence:
    metric: str
    value: float
    unit: str
    years: tuple[int, ...]


@dataclass(frozen=True)
class Insight:
    code: str
    text: str
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True)
class HeatwaveResult:
    threshold_c: float
    baseline_mean_tmax_c: float
    baseline: Coverage
    analysis: Coverage
    years: tuple[YearCoverage, ...]
    events: tuple[Event, ...]
    annual: tuple[AnnualRow, ...]
    event_count: int
    mean_duration_days: float | None
    trend_direction: TrendDirection
    frequency_slope_per_year: float | None
    mann_kendall: MannKendall | None
    trend_year_count: int
    status: Literal["complete", "partial"]
    warnings: tuple[Notice, ...]
    insights: tuple[Insight, ...]


def linear_percentile(values: Iterable[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Percentile of an empty sample")
    position = (len(ordered) - 1) * q
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def coverage(series: Sequence[DailyValue]) -> Coverage:
    counts = Counter(day.quality for day in series)
    return Coverage(
        expected_days=len(series),
        valid_days=counts["valid"],
        missing_days=counts["missing"],
        invalid_days=counts["invalid"],
        duplicate_dates=sum(day.duplicate for day in series),
    )


def year_eligibility(series: Sequence[DailyValue]) -> tuple[bool, tuple[str, ...]]:
    reasons = []
    if Fraction(sum(d.quality == "valid" for d in series), len(series)) < YEAR_MIN_VALID:
        reasons.append("year_below_90_percent_valid")
    months: dict[int, list[DailyValue]] = defaultdict(list)
    for day in series:
        months[day.day.month].append(day)
    for month, values in sorted(months.items()):
        if Fraction(sum(d.quality == "valid" for d in values), len(values)) < MONTH_MIN_VALID:
            reasons.append(f"month_{month:02d}_below_80_percent_valid")
    return not reasons, tuple(reasons)


def _require_span(series: Sequence[DailyValue], start: date, end: date) -> None:
    if not series or any(d.day != start + timedelta(days=i) for i, d in enumerate(series)):
        raise ValueError("Series must be a contiguous daily sequence")
    if series[-1].day != end:
        raise ValueError("Series does not end on the expected date")


def _by_year(series: Sequence[DailyValue]) -> dict[int, list[DailyValue]]:
    years: dict[int, list[DailyValue]] = defaultdict(list)
    for day in series:
        years[day.day.year].append(day)
    return years


def _runs(series: Sequence[DailyValue], threshold: float) -> list[list[DailyValue]]:
    runs, current = [], []
    for day in series:
        if day.quality == "valid" and day.tmax_c is not None and day.tmax_c > threshold:
            current.append(day)
        else:
            if current:
                runs.append(current)
            current = []
    if current:
        runs.append(current)
    return runs


@dataclass(frozen=True)
class Trend:
    direction: TrendDirection
    ols_slope: float | None
    test: MannKendall | None
    serially_correlated_r: float | None


def _trend(rows: Sequence[AnnualRow]) -> Trend:
    points = [(row.year, row.event_count) for row in rows if row.eligible]
    if len(points) < MIN_TREND_YEARS:
        return Trend("insufficient_data", None, None, None)
    n = len(points)
    sx = sum(x for x, _ in points)
    sy = sum(y for _, y in points)
    # Integer least-squares terms keep the descriptive slope exact.
    numerator = n * sum(x * y for x, y in points) - sx * sy
    denominator = n * sum(x * x for x, _ in points) - sx * sx
    test = mann_kendall(points)
    if not test.significant:
        direction = "no_significant_trend"
    else:
        direction = "increasing" if test.s > 0 else "decreasing"
    # Positive serial correlation inflates significance, so only a significant result is flagged.
    r = lag1_autocorrelation([y - test.sens_slope * x for x, y in points])
    flagged = test.significant and r is not None and r > serial_correlation_bound(n)
    return Trend(direction, float(Fraction(numerator, denominator)), test, r if flagged else None)


def _annual(
    years: Sequence[YearCoverage],
    analysis_years: dict[int, list[DailyValue]],
    events: Sequence[Event],
    baseline_mean: float,
) -> tuple[AnnualRow, ...]:
    durations: dict[int, list[int]] = defaultdict(list)
    event_days: Counter[int] = Counter()
    for event in events:
        durations[event.start.year].append(event.duration_days)
        for offset in range(event.duration_days):
            event_days[(event.start + timedelta(days=offset)).year] += 1
    rows = []
    for cover in years:
        if not cover.eligible:
            rows.append(AnnualRow(cover.year, False, cover.coverage_fraction, *([None] * 7)))
            continue
        lengths = durations[cover.year]
        temps = [d.tmax_c for d in analysis_years[cover.year] if d.quality == "valid"]
        mean_tmax = math.fsum(temps) / len(temps)
        rows.append(
            AnnualRow(
                year=cover.year,
                eligible=True,
                coverage_fraction=cover.coverage_fraction,
                event_count=len(lengths),
                mean_duration_days=math.fsum(lengths) / len(lengths) if lengths else None,
                max_duration_days=max(lengths) if lengths else None,
                heatwave_days=event_days[cover.year],
                mean_tmax_c=mean_tmax,
                tmax_anomaly_c=mean_tmax - baseline_mean,
                frequency_rolling_5y=None,
            )
        )
    for index in range(ROLLING_YEARS - 1, len(rows)):
        window = rows[index - ROLLING_YEARS + 1 : index + 1]
        if all(row.eligible for row in window):
            mean = sum(row.event_count for row in window) / ROLLING_YEARS
            rows[index] = AnnualRow(**{**rows[index].__dict__, "frequency_rolling_5y": mean})
    return tuple(rows)


def _insights(
    events: Sequence[Event],
    rows: Sequence[AnnualRow],
    trend: Trend,
    start_year: int,
    end_year: int,
) -> tuple[Insight, ...]:
    eligible = tuple(row.year for row in rows if row.eligible)
    count = len(events)
    noun = "event" if count == 1 else "events"
    insights = [
        Insight(
            "EVENT_TOTAL",
            f"{count} heatwave {noun} started between {start_year} and {end_year} "
            f"across {len(eligible)} eligible years.",
            (Evidence("event_count", count, "events", eligible),),
        )
    ]
    test = trend.test
    if test is None:
        text = (
            f"Only {len(eligible)} eligible years are available; at least "
            f"{MIN_TREND_YEARS} are needed to test for a trend."
        )
        evidence = (Evidence("trend_year_count", len(eligible), "years", eligible),)
    else:
        outcome = (
            f"a statistically significant {trend.direction} trend"
            if test.significant
            else "no statistically significant trend"
        )
        p_text = "< 0.001" if test.p_value < 0.001 else f"= {test.p_value:.3f}"
        cause = " The test describes this record, not its cause." if test.significant else ""
        text = (
            f"Annual heatwave counts show {outcome} across {len(eligible)} eligible years "
            f"({eligible[0]}–{eligible[-1]}): Mann-Kendall p {p_text}, Sen's slope "
            f"{test.sens_slope:+.3f} events per year.{cause}"
        )
        evidence = (
            Evidence("mann_kendall_p_value", test.p_value, "probability", eligible),
            Evidence("sens_slope_per_year", test.sens_slope, "events/year per year", eligible),
        )
    insights.append(Insight("FREQUENCY_TREND", text, evidence))
    if events:
        longest = max(events, key=lambda event: event.duration_days)
        clipped = (
            " It was cut off by the analysis period boundary." if longest.boundary_censored else ""
        )
        insights.append(
            Insight(
                "LONGEST_EVENT",
                f"The longest observed event lasted {longest.duration_days} days, from "
                f"{longest.start.isoformat()} to {longest.end.isoformat()}.{clipped}",
                (Evidence("duration_days", longest.duration_days, "days", (longest.start.year,)),),
            )
        )
    anomalies = [row for row in rows if row.tmax_anomaly_c is not None]
    if anomalies:
        warmest = max(anomalies, key=lambda row: row.tmax_anomaly_c)
        insights.append(
            Insight(
                "WARMEST_YEAR",
                f"{warmest.year} had the highest annual mean daily maximum temperature anomaly, "
                f"{warmest.tmax_anomaly_c:+.2f} °C relative to 1991–2020.",
                (Evidence("tmax_anomaly_c", warmest.tmax_anomaly_c, "°C", (warmest.year,)),),
            )
        )
    return tuple(insights)


def _gap_years(series: Sequence[DailyValue]) -> tuple[int, ...]:
    return tuple(sorted({d.day.year for d in series if d.quality != "valid"}))


def analyze_heatwaves(
    baseline: Sequence[DailyValue], analysis: Sequence[DailyValue]
) -> HeatwaveResult:
    _require_span(baseline, BASELINE_START, BASELINE_END)
    if not analysis:
        raise ValueError("Empty analysis series")
    start, end = analysis[0].day, analysis[-1].day
    if (start.month, start.day, end.month, end.day) != (1, 1, 12, 31):
        raise ValueError("Analysis series must cover whole calendar years")
    _require_span(analysis, start, end)

    failing = tuple(y for y, s in sorted(_by_year(baseline).items()) if not year_eligibility(s)[0])
    if failing:
        raise InsufficientBaseline(failing)
    baseline_values = [d.tmax_c for d in baseline if d.quality == "valid"]
    threshold = linear_percentile(baseline_values, PERCENTILE)
    baseline_mean = math.fsum(baseline_values) / len(baseline_values)

    analysis_years = _by_year(analysis)
    years = []
    for year, values in sorted(analysis_years.items()):
        eligible, reasons = year_eligibility(values)
        years.append(
            YearCoverage(
                **coverage(values).__dict__, year=year, eligible=eligible, excluded_reasons=reasons
            )
        )
    eligible_years = {cover.year for cover in years if cover.eligible}
    if not eligible_years:
        raise InsufficientData()

    events, excluded_years = [], set()
    for run in _runs(analysis, threshold):
        if len(run) < MIN_RUN_DAYS:
            continue
        touched = {d.day.year for d in run}
        if not touched <= eligible_years:
            excluded_years |= touched
            continue
        excess = [d.tmax_c - threshold for d in run]
        events.append(
            Event(
                start=run[0].day,
                end=run[-1].day,
                duration_days=len(run),
                mean_excess_c=math.fsum(excess) / len(excess),
                max_excess_c=max(excess),
                boundary_censored=run[0].day == start or run[-1].day == end,
            )
        )

    rows = _annual(years, analysis_years, events, baseline_mean)
    trend = _trend(rows)
    baseline_cover, analysis_cover = coverage(baseline), coverage(analysis)
    censored = tuple(sorted({e.start.year for e in events if e.boundary_censored}))
    ineligible = tuple(cover.year for cover in years if not cover.eligible)

    warnings = [
        Notice(
            "UTC_CALENDAR_DAYS",
            "Daily maxima use UTC calendar days, which can differ from local days.",
            (),
        )
    ]
    if baseline_cover.valid_days < baseline_cover.expected_days:
        warnings.append(
            Notice(
                "BASELINE_INCOMPLETE",
                "Some 1991–2020 baseline days are missing or invalid; every baseline "
                "year still meets the coverage gates.",
                _gap_years(baseline),
            )
        )
    if analysis_cover.valid_days < analysis_cover.expected_days:
        warnings.append(
            Notice(
                "ANALYSIS_INCOMPLETE",
                "Some analysis days are missing or invalid; they break heatwave runs "
                "and are never filled in.",
                _gap_years(analysis),
            )
        )
    if ineligible:
        warnings.append(
            Notice(
                "YEARS_EXCLUDED",
                "These years fall below the 90% annual or 80% monthly valid-day "
                "gates, so their metrics are omitted.",
                ineligible,
            )
        )
    if excluded_years:
        warnings.append(
            Notice(
                "EVENTS_EXCLUDED_INELIGIBLE_YEAR",
                "Heatwave runs touching an excluded year are not counted.",
                tuple(sorted(excluded_years)),
            )
        )
    if trend.serially_correlated_r is not None:
        warnings.append(
            Notice(
                "SERIAL_CORRELATION",
                f"Annual counts are positively autocorrelated (lag-1 r = "
                f"{trend.serially_correlated_r:.2f}), so the Mann-Kendall test may overstate "
                "significance.",
                (),
            )
        )
    if censored:
        warnings.append(
            Notice(
                "BOUNDARY_CENSORED",
                "Some events touch the start or end of the period; their observed "
                "duration may be shorter than the full event.",
                censored,
            )
        )

    partial = bool(
        ineligible or censored or analysis_cover.valid_days < analysis_cover.expected_days
    )
    durations = [e.duration_days for e in events]
    return HeatwaveResult(
        threshold_c=threshold,
        baseline_mean_tmax_c=baseline_mean,
        baseline=baseline_cover,
        analysis=analysis_cover,
        years=tuple(years),
        events=tuple(events),
        annual=rows,
        event_count=len(events),
        mean_duration_days=math.fsum(durations) / len(durations) if durations else None,
        trend_direction=trend.direction,
        frequency_slope_per_year=trend.ols_slope,
        mann_kendall=trend.test,
        trend_year_count=len(eligible_years),
        status="partial" if partial else "complete",
        warnings=tuple(warnings),
        insights=_insights(events, rows, trend, start.year, end.year),
    )
