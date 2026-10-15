"""Mann-Kendall trend test with Sen's slope (ADR-025); pure functions using the standard library."""

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import median

SIGNIFICANCE_LEVEL = 0.05


@dataclass(frozen=True)
class MannKendall:
    s: int
    variance: float
    z: float
    p_value: float
    tau: float
    sens_slope: float
    significant: bool


def mann_kendall(points: Sequence[tuple[int, float]]) -> MannKendall:
    ordered = sorted(points)
    years = [year for year, _ in ordered]
    values = [value for _, value in ordered]
    n = len(values)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    s = sum((values[j] > values[i]) - (values[j] < values[i]) for i, j in pairs)
    ties = sum(t * (t - 1) * (2 * t + 5) for t in Counter(values).values())
    variance = (n * (n - 1) * (2 * n + 5) - ties) / 18
    # Continuity correction moves S one step toward zero before the normal approximation.
    z = 0.0 if s == 0 or variance == 0 else (s - math.copysign(1, s)) / math.sqrt(variance)
    p_value = math.erfc(abs(z) / math.sqrt(2))
    # Actual years, not positions, so excluded years remain gaps in every pairwise slope.
    sens_slope = median((values[j] - values[i]) / (years[j] - years[i]) for i, j in pairs)
    return MannKendall(
        s, variance, z, p_value, s / len(pairs), sens_slope, p_value < SIGNIFICANCE_LEVEL
    )


def lag1_autocorrelation(values: Sequence[float]) -> float | None:
    mean = math.fsum(values) / len(values)
    deviations = [value - mean for value in values]
    denominator = math.fsum(d * d for d in deviations)
    if denominator == 0:
        return None
    pairs = zip(deviations[:-1], deviations[1:], strict=True)
    return math.fsum(a * b for a, b in pairs) / denominator


# Anderson's one-sided 95% bound for a lag-1 autocorrelation of n independent values.
def serial_correlation_bound(n: int) -> float:
    return (-1 + 1.96 * math.sqrt(n - 2)) / (n - 1)
