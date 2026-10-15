import math
from statistics import NormalDist

import pytest

from app.trend import lag1_autocorrelation, mann_kendall, serial_correlation_bound


def two_sided(z: float) -> float:
    return 2 * (1 - NormalDist().cdf(abs(z)))


def series(values, start=2001):
    return [(start + index, value) for index, value in enumerate(values)]


def test_strict_increase_matches_hand_calculation():
    result = mann_kendall(series(range(10)))
    # S = 45, Var = 10 * 9 * 25 / 18 = 125, Z = (45 - 1) / sqrt(125)
    assert result.s == 45
    assert result.variance == pytest.approx(125)
    assert result.z == pytest.approx(44 / math.sqrt(125))
    assert result.p_value == pytest.approx(two_sided(44 / math.sqrt(125)), rel=1e-6)
    assert result.tau == pytest.approx(1.0)
    assert result.sens_slope == pytest.approx(1.0)
    assert result.significant


def test_strict_decrease_is_symmetric():
    result = mann_kendall(series(range(9, -1, -1)))
    assert result.s == -45
    assert (result.tau, result.sens_slope) == (pytest.approx(-1.0), pytest.approx(-1.0))
    assert result.z == pytest.approx(-44 / math.sqrt(125))
    assert result.significant


def test_ties_reduce_the_variance_and_sens_slope_uses_the_median():
    result = mann_kendall(series([1] * 5 + [2] * 5))
    # Two tie groups of 5: Var = (2250 - 2 * 5 * 4 * 15) / 18; S counts the 25 cross pairs.
    assert result.s == 25
    assert result.variance == pytest.approx(1650 / 18)
    assert result.z == pytest.approx(24 / math.sqrt(1650 / 18))
    assert result.p_value == pytest.approx(two_sided(24 / math.sqrt(1650 / 18)), rel=1e-6)
    assert result.tau == pytest.approx(25 / 45)
    # 20 zero slopes then 1/9, 1/8, 1/8, ...: the 23rd of 45 sorted slopes is 1/8.
    assert result.sens_slope == pytest.approx(0.125)
    assert result.significant


def test_constant_counts_have_no_trend_and_no_variance():
    result = mann_kendall(series([3] * 10))
    assert (result.s, result.variance, result.z, result.p_value) == (0, 0, 0, 1)
    assert result.sens_slope == 0 and not result.significant


def test_alternating_counts_are_not_significant():
    result = mann_kendall(series([1, 3] * 5))
    assert result.s == 5
    assert result.p_value == pytest.approx(two_sided(4 / math.sqrt(1650 / 18)), rel=1e-6)
    assert not result.significant


def test_sens_slope_uses_actual_years_across_gaps_and_averages_even_medians():
    assert mann_kendall([(2000, 0), (2001, 1), (2003, 3)]).sens_slope == pytest.approx(1.0)
    # Slopes -1, 0.5, 0.5, 1, 2, 2: the median of an even count averages the middle two.
    assert mann_kendall(series([0, 2, 1, 3])).sens_slope == pytest.approx(0.75)


def test_lag1_autocorrelation_and_anderson_bound():
    assert lag1_autocorrelation([1, 2, 3, 4]) == pytest.approx(0.25)
    assert lag1_autocorrelation([1, -1, 1, -1]) == pytest.approx(-0.75)
    assert lag1_autocorrelation([2, 2, 2]) is None
    assert serial_correlation_bound(10) == pytest.approx((-1 + 1.96 * math.sqrt(8)) / 9)


def test_a_p_value_between_five_and_ten_percent_is_not_significant():
    result = mann_kendall(series([2, 0, 0, 1, 3, 1, 2, 3, 2, 3]))
    # Tie groups of 2, 2, 3 and 3: Var = (2250 - 2 * 18 - 2 * 66) / 18.
    assert result.s == 21
    assert result.variance == pytest.approx(2082 / 18)
    assert 0.05 < result.p_value < 0.10
    assert not result.significant
