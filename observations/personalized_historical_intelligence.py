from dataclasses import dataclass

from observations.battery_trend import (
    BatteryTrend,
    TrendDirection,
)
from observations.historical_data_access import HistoricalDataAccess
from observations.historical_statistics import HistoricalStatistics
from observations.historical_usage_patterns import (
    HistoricalUsagePatterns,
)
from observations.application_battery_patterns import (
    ApplicationBatteryPattern,
    ApplicationBatteryPatterns,
)
from observations.heavy_usage import HeavyUsageDetection
from observations.time_of_day_behavior import (
    TimeOfDay,
    TimeOfDayBatteryBehavior,
)


@dataclass(frozen=True)
class PersonalizedHistoricalIntelligenceResult:
    """Aggregated personalized historical battery intelligence."""

    observation_count: int

    average_battery: float | None
    minimum_battery: float | None
    maximum_battery: float | None

    battery_trend: TrendDirection

    average_discharge_duration_hours: float | None
    average_battery_drop: float | None
    average_drain_rate: float | None

    strongest_usage_period: TimeOfDay | None

    application_patterns: tuple[ApplicationBatteryPattern, ...]

    heavy_usage_session_count: int
    average_historical_drain_rate: float | None


class PersonalizedHistoricalIntelligence:
    """Aggregates existing historical intelligence into a user profile."""

    def __init__(self, access: HistoricalDataAccess):
        self.access = access

    def calculate(self) -> PersonalizedHistoricalIntelligenceResult:
        """Calculate the user's personalized historical battery profile."""

        statistics = HistoricalStatistics(self.access).calculate()
        trend = BatteryTrend(self.access).calculate()
        usage_patterns = HistoricalUsagePatterns(
            self.access
        ).calculate()
        time_of_day = TimeOfDayBatteryBehavior(
            self.access
        ).calculate()
        application_patterns = ApplicationBatteryPatterns(
            self.access
        ).calculate()
        heavy_usage = HeavyUsageDetection(
            self.access
        ).calculate()

        strongest_usage_period = self._strongest_usage_period(
            time_of_day
        )

        return PersonalizedHistoricalIntelligenceResult(
            observation_count=statistics.observation_count,
            average_battery=statistics.average_battery,
            minimum_battery=statistics.minimum_battery,
            maximum_battery=statistics.maximum_battery,
            battery_trend=trend.trend,
            average_discharge_duration_hours=(
                usage_patterns.average_duration_hours
            ),
            average_battery_drop=(
                usage_patterns.average_battery_drop
            ),
            average_drain_rate=(
                usage_patterns.average_drain_rate
            ),
            strongest_usage_period=strongest_usage_period,
            application_patterns=(
                application_patterns.patterns
            ),
            heavy_usage_session_count=(
                len(heavy_usage.heavy_sessions)
            ),
            average_historical_drain_rate=(
                heavy_usage.average_drain_rate
            ),
        )

    @staticmethod
    def _strongest_usage_period(
        time_of_day,
    ) -> TimeOfDay | None:
        """Return the period with the highest average drain rate."""

        period_stats = {
            TimeOfDay.MORNING: time_of_day.morning,
            TimeOfDay.AFTERNOON: time_of_day.afternoon,
            TimeOfDay.EVENING: time_of_day.evening,
            TimeOfDay.NIGHT: time_of_day.night,
        }

        valid_periods = [
            (period, stats)
            for period, stats in period_stats.items()
            if stats.average_drain_rate is not None
        ]

        if not valid_periods:
            return None

        return max(
            valid_periods,
            key=lambda item: item[1].average_drain_rate,
        )[0]