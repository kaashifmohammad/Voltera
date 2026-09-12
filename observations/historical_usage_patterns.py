from dataclasses import dataclass
from typing import Optional

from observations.battery_discharge import BatteryDischarge, DischargeSession


@dataclass(frozen=True)
class HistoricalUsagePatternResult:
    """Aggregated historical battery usage patterns."""

    session_count: int
    average_duration_hours: Optional[float]
    average_battery_drop: Optional[float]
    average_drain_rate: Optional[float]
    maximum_drain_rate: Optional[float]
    average_observation_count: Optional[float]


class HistoricalUsagePatterns:
    """Aggregates historical battery discharge session behavior."""

    def __init__(self, access):
        self.access = access

    def calculate(self) -> HistoricalUsagePatternResult:
        """Calculate aggregate statistics from historical discharge sessions."""

        sessions = BatteryDischarge(self.access).calculate()

        if not sessions:
            return HistoricalUsagePatternResult(
                session_count=0,
                average_duration_hours=None,
                average_battery_drop=None,
                average_drain_rate=None,
                maximum_drain_rate=None,
                average_observation_count=None,
            )

        return HistoricalUsagePatternResult(
            session_count=len(sessions),
            average_duration_hours=self._average(
                session.duration_hours
                for session in sessions
            ),
            average_battery_drop=self._average(
                abs(session.battery_change)
                for session in sessions
            ),
            average_drain_rate=self._average(
                session.drain_rate
                for session in sessions
            ),
            maximum_drain_rate=max(
                session.drain_rate
                for session in sessions
            ),
            average_observation_count=self._average(
                session.observation_count
                for session in sessions
            ),
        )

    @staticmethod
    def _average(values) -> Optional[float]:
        """Return the arithmetic mean of a collection of values."""

        values = list(values)

        if not values:
            return None

        return sum(values) / len(values)