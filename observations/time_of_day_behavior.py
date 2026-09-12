from dataclasses import dataclass
from datetime import time
from enum import Enum

from observations.battery_discharge import BatteryDischarge
from observations.historical_data_access import HistoricalDataAccess


class TimeOfDay(Enum):
    """Time periods used for historical battery behavior analysis."""

    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    NIGHT = "NIGHT"


@dataclass(frozen=True)
class TimeOfDayStats:
    """Aggregated battery behavior for one time-of-day period."""

    session_count: int
    average_battery_drop: float | None
    average_drain_rate: float | None


@dataclass(frozen=True)
class TimeOfDayBehaviorResult:
    """Historical battery behavior grouped by time of day."""

    morning: TimeOfDayStats
    afternoon: TimeOfDayStats
    evening: TimeOfDayStats
    night: TimeOfDayStats


class TimeOfDayBatteryBehavior:
    """Analyzes historical battery discharge behavior by time of day."""

    def __init__(self, access: HistoricalDataAccess):
        self.access = access

    def calculate(self) -> TimeOfDayBehaviorResult:
        """Calculate historical battery behavior for each time period."""

        sessions = BatteryDischarge(self.access).calculate()

        grouped: dict[TimeOfDay, list] = {
            period: []
            for period in TimeOfDay
        }

        for session in sessions:
            period = self._classify(session.start_time.time())
            grouped[period].append(session)

        return TimeOfDayBehaviorResult(
            morning=self._calculate_stats(grouped[TimeOfDay.MORNING]),
            afternoon=self._calculate_stats(grouped[TimeOfDay.AFTERNOON]),
            evening=self._calculate_stats(grouped[TimeOfDay.EVENING]),
            night=self._calculate_stats(grouped[TimeOfDay.NIGHT]),
        )

    @staticmethod
    def _classify(timestamp: time) -> TimeOfDay:
        """Classify a timestamp into a time-of-day period."""

        if time(6, 0) <= timestamp < time(12, 0):
            return TimeOfDay.MORNING

        if time(12, 0) <= timestamp < time(17, 0):
            return TimeOfDay.AFTERNOON

        if time(17, 0) <= timestamp < time(22, 0):
            return TimeOfDay.EVENING

        return TimeOfDay.NIGHT

    @staticmethod
    def _calculate_stats(sessions) -> TimeOfDayStats:
        """Calculate aggregate statistics for a group of sessions."""

        if not sessions:
            return TimeOfDayStats(
                session_count=0,
                average_battery_drop=None,
                average_drain_rate=None,
            )

        battery_drops = [
            abs(session.battery_change)
            for session in sessions
        ]

        drain_rates = [
            session.drain_rate
            for session in sessions
        ]

        return TimeOfDayStats(
            session_count=len(sessions),
            average_battery_drop=(
                sum(battery_drops) / len(battery_drops)
            ),
            average_drain_rate=(
                sum(drain_rates) / len(drain_rates)
            ),
        )