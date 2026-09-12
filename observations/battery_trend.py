from dataclasses import dataclass
from enum import Enum

from observations.historical_data_access import HistoricalDataAccess


class TrendDirection(Enum):
    """Possible historical battery trend directions."""

    RISING = "RISING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True)
class BatteryTrendResult:
    """Result of historical battery trend analysis."""

    trend: TrendDirection
    observation_count: int
    first_battery: float | None
    last_battery: float | None
    change: float | None


class BatteryTrend:
    """Determines the historical direction of battery percentage."""

    MINIMUM_OBSERVATIONS = 3
    STABILITY_TOLERANCE = 2.0

    def __init__(self, access: HistoricalDataAccess):
        self.access = access

    def calculate(self) -> BatteryTrendResult:
        """Calculate the battery trend from historical observations."""

        observations = self.access.recent(self.access.count())

        observations = sorted(
            observations,
            key=lambda observation: observation.timestamp,
        )

        battery_values = [
            observation.battery_percentage
            for observation in observations
            if observation.battery_percentage is not None
        ]

        if len(battery_values) < self.MINIMUM_OBSERVATIONS:
            return BatteryTrendResult(
                trend=TrendDirection.INSUFFICIENT_DATA,
                observation_count=len(battery_values),
                first_battery=battery_values[0]
                if battery_values
                else None,
                last_battery=battery_values[-1]
                if battery_values
                else None,
                change=None,
            )

        first_battery = battery_values[0]
        last_battery = battery_values[-1]
        change = last_battery - first_battery

        if abs(change) <= self.STABILITY_TOLERANCE:
            trend = TrendDirection.STABLE
        elif change > 0:
            trend = TrendDirection.RISING
        else:
            trend = TrendDirection.DECLINING

        return BatteryTrendResult(
            trend=trend,
            observation_count=len(battery_values),
            first_battery=first_battery,
            last_battery=last_battery,
            change=change,
        )