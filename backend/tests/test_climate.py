from datetime import date, timedelta

import pytest

from app.climate import (
    BASELINE_END,
    BASELINE_START,
    InsufficientBaseline,
    InsufficientData,
    analyze_heatwaves,
    linear_percentile,
    year_eligibility,
)
from app.ingestion import DailyValue

INVALID = object()


def days(start: date, end: date, base=15.0, overrides=None):
    overrides = overrides or {}
    result, current = [], start
    while current <= end:
        value = overrides.get(current, base)
        if value is None:
            result.append(DailyValue(current, None, "missing"))
        elif value is INVALID:
            result.append(DailyValue(current, None, "invalid", True))
        else:
            result.append(DailyValue(current, float(value), "valid"))
        current += timedelta(days=1)
    return tuple(result)


def baseline(base=20.0, overrides=None):
    return days(BASELINE_START, BASELINE_END, base, overrides)


def analysis(start_year, end_year, overrides=None):
    return days(date(start_year, 1, 1), date(end_year, 12, 31), 15.0, overrides)


def run(start: date, length: int, value=25.0):
    return {start + timedelta(days=offset): value for offset in range(length)}


def missing_spread(year: int, per_month: int):
    return {
        date(year, month, day): None
        for month in range(1, 13)
        for day in range(1, per_month + 1)
    }


@pytest.mark.parametrize("values,expected", [
    ([5, 1, 3, 2, 4], 4.8), ([10, 20], 19.5), ([7], 7.0), ([1, 1, 1, 1], 1.0),
])
def test_linear_percentile_matches_hand_calculation(values, expected):
    assert linear_percentile(values, 0.95) == pytest.approx(expected)


@pytest.mark.parametrize("year,missing,extra,eligible", [
    (2001, missing_spread(2001, 3), {}, True),
    (2001, missing_spread(2001, 3), {date(2001, 6, 20): None}, False),
    (2000, missing_spread(2000, 3), {}, True),
    (2001, {date(2001, 1, day): None for day in range(1, 7)}, {}, True),
    (2001, {date(2001, 1, day): None for day in range(1, 8)}, {}, False),
    (2000, {date(2000, 2, day): None for day in range(1, 6)}, {}, True),
    (2000, {date(2000, 2, day): None for day in range(1, 7)}, {}, False),
])
def test_year_and_month_gates_use_actual_calendar_lengths(year, missing, extra, eligible):
    series = days(date(year, 1, 1), date(year, 12, 31), overrides={**missing, **extra})
    assert year_eligibility(series)[0] is eligible


def test_threshold_equality_does_not_exceed_and_baseline_stats():
    result = analyze_heatwaves(baseline(), analysis(2001, 2001, run(date(2001, 6, 1), 4, 20.0)))
    assert result.threshold_c == 20.0
    assert result.baseline_mean_tmax_c == 20.0
    assert result.events == ()
    assert result.annual[0].event_count == 0
    assert result.annual[0].mean_duration_days is None
    assert result.annual[0].heatwave_days == 0


def test_ineligible_baseline_year_fails_with_year():
    with pytest.raises(InsufficientBaseline) as error:
        analyze_heatwaves(baseline(overrides=missing_spread(1995, 4)), analysis(2001, 2001))
    assert error.value.years == (1995,)


def test_incomplete_but_eligible_baseline_warns():
    result = analyze_heatwaves(baseline(overrides={date(1999, 3, 3): None}), analysis(2001, 2001))
    assert "BASELINE_INCOMPLETE" in {w.code for w in result.warnings}
    assert result.baseline.missing_days == 1


def test_run_rules_lengths_separators_and_flush():
    overrides = {
        **run(date(2001, 3, 1), 2),
        **run(date(2001, 4, 1), 3),
        **run(date(2001, 5, 1), 6),
        **run(date(2001, 6, 1), 3), date(2001, 6, 4): 20.0, **run(date(2001, 6, 5), 3),
        **run(date(2001, 7, 1), 2), date(2001, 7, 3): None, **run(date(2001, 7, 4), 2),
        **run(date(2001, 8, 1), 2), date(2001, 8, 3): INVALID, **run(date(2001, 8, 4), 2),
        **run(date(2001, 9, 1), 3, 22.0), date(2001, 9, 2): 26.0,
    }
    result = analyze_heatwaves(baseline(), analysis(2001, 2001, overrides))
    assert [(e.start.isoformat(), e.duration_days) for e in result.events] == [
        ("2001-04-01", 3), ("2001-05-01", 6), ("2001-06-01", 3), ("2001-06-05", 3),
        ("2001-09-01", 3),
    ]
    september = result.events[-1]
    assert september.mean_excess_c == pytest.approx(10 / 3)
    assert september.max_excess_c == pytest.approx(6.0)
    assert not any(e.boundary_censored for e in result.events)
    assert result.annual[0].heatwave_days == 18
    assert result.analysis.invalid_days == 1 and result.analysis.duplicate_dates == 1


def test_cross_year_event_counted_once_and_days_apportioned():
    result = analyze_heatwaves(baseline(), analysis(2001, 2002, run(date(2001, 12, 30), 4)))
    assert len(result.events) == 1
    first, second = result.annual
    assert (first.event_count, first.heatwave_days, first.max_duration_days) == (1, 2, 4)
    assert (second.event_count, second.heatwave_days, second.mean_duration_days) == (0, 2, None)


def test_runs_touching_period_boundaries_are_censored_and_partial():
    overrides = {
        **run(date(2001, 1, 1), 3), **run(date(2001, 12, 29), 3), **run(date(2001, 2, 1), 2)
    }
    result = analyze_heatwaves(baseline(), analysis(2001, 2001, overrides))
    assert [e.boundary_censored for e in result.events] == [True, True]
    assert result.status == "partial"
    assert "BOUNDARY_CENSORED" in {w.code for w in result.warnings}


def test_run_touching_ineligible_year_is_excluded_with_warning():
    overrides = {**missing_spread(2002, 4), **run(date(2001, 12, 30), 4)}
    result = analyze_heatwaves(baseline(), analysis(2001, 2002, overrides))
    assert result.events == ()
    first, second = result.annual
    assert first.event_count == 0 and first.heatwave_days == 0
    assert second.eligible is False and second.event_count is None and second.mean_tmax_c is None
    assert second.coverage_fraction == pytest.approx(319 / 365)
    codes = {w.code: w.years for w in result.warnings}
    assert codes["EVENTS_EXCLUDED_INELIGIBLE_YEAR"] == (2001, 2002)
    assert codes["YEARS_EXCLUDED"] == (2002,)
    assert result.years[1].excluded_reasons == ("year_below_90_percent_valid",)
    assert result.status == "partial"


def test_no_eligible_year_is_insufficient_data():
    with pytest.raises(InsufficientData):
        analyze_heatwaves(baseline(), analysis(2001, 2001, missing_spread(2001, 4)))


def events_per_year(counts: dict[int, int]):
    overrides = {}
    for year, count in counts.items():
        for index in range(count):
            overrides.update(run(date(year, 3, 1) + timedelta(days=5 * index), 3))
    return overrides


def test_increasing_trend_uses_actual_year_numbers_and_rolling_gaps():
    counts = {year: year - 2000 for year in range(2001, 2012) if year != 2005}
    overrides = {**events_per_year(counts), **missing_spread(2005, 4)}
    result = analyze_heatwaves(baseline(), analysis(2001, 2011, overrides))
    assert result.trend_year_count == 10
    assert result.frequency_slope_per_year == pytest.approx(1.0)
    assert result.trend_direction == "increasing"
    assert (result.mann_kendall.s, result.mann_kendall.sens_slope) == (45, pytest.approx(1.0))
    rolling = {row.year: row.frequency_rolling_5y for row in result.annual}
    assert [rolling[y] for y in range(2001, 2010)] == [None] * 9
    assert rolling[2010] == pytest.approx(8.0) and rolling[2011] == pytest.approx(9.0)


@pytest.mark.parametrize("counts,direction", [
    ({year: 2011 - year for year in range(2001, 2011)}, "decreasing"),
    ({year: 2 for year in range(2001, 2011)}, "no_significant_trend"),
])
def test_decreasing_and_constant_trends(counts, direction):
    result = analyze_heatwaves(baseline(), analysis(2001, 2010, events_per_year(counts)))
    assert result.trend_direction == direction
    if direction == "no_significant_trend":
        assert result.frequency_slope_per_year == 0.0
        assert result.mann_kendall.p_value == 1


def test_a_small_positive_slope_without_a_significant_test_is_not_called_increasing():
    counts = {year: 1 if year % 2 else 3 for year in range(2001, 2011)}
    result = analyze_heatwaves(baseline(), analysis(2001, 2010, events_per_year(counts)))
    assert result.frequency_slope_per_year > 0
    assert result.trend_direction == "no_significant_trend"
    assert not result.mann_kendall.significant


def test_serial_correlation_warning_only_for_a_significant_autocorrelated_trend():
    steps = [1, 1, 1, 1, 4, 4, 4, 4, 2, 2, 2, 2, 5, 5, 5, 5]
    counts = {2001 + index: value for index, value in enumerate(steps)}
    result = analyze_heatwaves(baseline(), analysis(2001, 2016, events_per_year(counts)))
    assert result.trend_direction == "increasing"
    warning = next(w for w in result.warnings if w.code == "SERIAL_CORRELATION")
    assert "lag-1 r = 0.53" in warning.message

    monotonic = {year: year - 2000 for year in range(2001, 2011)}
    clean = analyze_heatwaves(baseline(), analysis(2001, 2010, events_per_year(monotonic)))
    assert "SERIAL_CORRELATION" not in {w.code for w in clean.warnings}


def test_fewer_than_ten_eligible_years_has_no_trend():
    result = analyze_heatwaves(baseline(), analysis(2001, 2009, events_per_year({2003: 2})))
    assert result.trend_direction == "insufficient_data"
    assert result.frequency_slope_per_year is None
    assert result.mann_kendall is None
    assert result.trend_year_count == 9


def test_summary_duration_is_event_weighted():
    overrides = {**run(date(2001, 5, 1), 3)}
    for index in range(3):
        overrides.update(run(date(2002, 5, 1) + timedelta(days=10 * index), 5))
    result = analyze_heatwaves(baseline(), analysis(2001, 2002, overrides))
    assert result.event_count == 4
    assert result.mean_duration_days == pytest.approx(4.5)
    assert [row.mean_duration_days for row in result.annual] == [3.0, 5.0]


def test_anomaly_and_complete_status():
    result = analyze_heatwaves(baseline(), analysis(2001, 2001))
    row = result.annual[0]
    assert row.mean_tmax_c == pytest.approx(15.0)
    assert row.tmax_anomaly_c == pytest.approx(-5.0)
    assert result.status == "complete"


def test_insights_report_the_trend_test_without_claiming_a_cause():
    counts = {year: year - 2000 for year in range(2001, 2011)}
    result = analyze_heatwaves(baseline(), analysis(2001, 2010, events_per_year(counts)))
    codes = [insight.code for insight in result.insights]
    assert codes[:2] == ["EVENT_TOTAL", "FREQUENCY_TREND"]
    total = result.insights[0]
    assert total.evidence[0].value == result.event_count == 55
    assert all(insight.evidence for insight in result.insights)
    trend = result.insights[1]
    assert trend.text == (
        "Annual heatwave counts show a statistically significant increasing trend across 10 "
        "eligible years (2001–2010): Mann-Kendall p < 0.001, Sen's slope +1.000 events per year. "
        "The test describes this record, not its cause."
    )
    assert [e.metric for e in trend.evidence] == ["mann_kendall_p_value", "sens_slope_per_year"]

    flat = {year: 1 if year % 2 else 3 for year in range(2001, 2011)}
    quiet = analyze_heatwaves(baseline(), analysis(2001, 2010, events_per_year(flat)))
    assert quiet.insights[1].text.startswith(
        "Annual heatwave counts show no statistically significant trend across 10 eligible years "
        "(2001–2010): Mann-Kendall p = 0."
    )


def test_series_must_cover_exact_periods():
    with pytest.raises(ValueError):
        analyze_heatwaves(baseline()[1:], analysis(2001, 2001))
    with pytest.raises(ValueError):
        analyze_heatwaves(baseline(), analysis(2001, 2001)[:-1])
