"""
Historical statistical intelligence for VOLTERA observations.

Provides aggregate battery, CPU, RAM, and charging statistics
from persisted historical observations.
"""
from dataclasses import dataclass
from typing import Optional

from observations.historical_data_access import HistoricalDataAccess


@dataclass(frozen=True)
class HistoricalStatisticsResult:
    """Calculated statistics from historical observations."""

    observation_count: int
    average_battery: Optional[float]
    minimum_battery: Optional[float]
    maximum_battery: Optional[float]
    average_cpu: Optional[float]
    average_ram: Optional[float]
    charging_ratio: Optional[float]


class HistoricalStatistics:
    """Calculates statistical summaries from historical observations."""

    def __init__(self, access: HistoricalDataAccess):
        self.access = access

    def calculate(self) -> HistoricalStatisticsResult:
        """Calculate statistics from all available historical observations."""

        observations = self.access.recent(self.access.count())

        if not observations:
            return HistoricalStatisticsResult(
                observation_count=0,
                average_battery=None,
                minimum_battery=None,
                maximum_battery=None,
                average_cpu=None,
                average_ram=None,
                charging_ratio=None,
            )

        battery_values = [
            observation.battery_percentage
            for observation in observations
            if observation.battery_percentage is not None
        ]

        cpu_values = [
            observation.cpu_usage
            for observation in observations
            if observation.cpu_usage is not None
        ]

        ram_values = [
            observation.ram_usage
            for observation in observations
            if observation.ram_usage is not None
        ]

        charging_values = [
            observation.charging_status
            for observation in observations
            if observation.charging_status is not None
        ]

        return HistoricalStatisticsResult(
            observation_count=len(observations),
            average_battery=self._average(battery_values),
            minimum_battery=min(battery_values)
            if battery_values
            else None,
            maximum_battery=max(battery_values)
            if battery_values
            else None,
            average_cpu=self._average(cpu_values),
            average_ram=self._average(ram_values),
            charging_ratio=self._charging_ratio(charging_values),
        )

    @staticmethod
    def _average(values: list[float]) -> Optional[float]:
        """Return the average of values, or None when no values exist."""

        if not values:
            return None

        return sum(values) / len(values)

    @staticmethod
    def _charging_ratio(values: list[bool]) -> Optional[float]:
        """Return the fraction of known observations that were charging."""

        if not values:
            return None

        return sum(values) / len(values)