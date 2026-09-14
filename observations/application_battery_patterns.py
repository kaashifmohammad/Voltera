from dataclasses import dataclass
from typing import Optional

from observations.historical_data_access import HistoricalDataAccess


@dataclass(frozen=True)
class ApplicationBatteryPattern:
    """Aggregated battery behavior associated with one application."""

    application: str
    observation_count: int
    battery_drop: float
    average_drain_rate: Optional[float]


@dataclass(frozen=True)
class ApplicationBatteryPatternResult:
    """Historical battery behavior grouped by application."""

    patterns: tuple[ApplicationBatteryPattern, ...]


class ApplicationBatteryPatterns:
    """Analyzes historical battery behavior associated with applications."""

    def __init__(self, access: HistoricalDataAccess):
        self.access = access

    def calculate(self) -> ApplicationBatteryPatternResult:
        """Calculate historical battery patterns for applications."""

        observations = self.access.recent(self.access.count())

        observations = sorted(
            observations,
            key=lambda observation: observation.timestamp,
        )

        application_data: dict[str, dict] = {}

        previous_observation = None

        for observation in observations:
            if observation.charging_status is True:
                previous_observation = None
                continue

            if observation.battery_percentage is None:
                previous_observation = None
                continue

            application = observation.active_application

            if application is None or not application.strip():
                previous_observation = None
                continue

            if previous_observation is None:
                previous_observation = observation
                continue

            previous_application = previous_observation.active_application

            if previous_application != application:
                previous_observation = observation
                continue

            elapsed_seconds = (
                observation.timestamp
                - previous_observation.timestamp
            ).total_seconds()

            if elapsed_seconds <= 0:
                previous_observation = observation
                continue

            battery_drop = (
                previous_observation.battery_percentage
                - observation.battery_percentage
            )

            if battery_drop < 0:
                previous_observation = observation
                continue

            elapsed_hours = elapsed_seconds / 3600

            drain_rate = battery_drop / elapsed_hours

            if application not in application_data:
                application_data[application] = {
                    "battery_drop": 0.0,
                    "drain_rates": [],
                    "observations": set(),
                }

            application_data[application]["observations"].add(
                previous_observation.timestamp
            )
            application_data[application]["observations"].add(
                observation.timestamp
            )

            application_data[application]["battery_drop"] += battery_drop

            application_data[application]["drain_rates"].append(
                drain_rate
            )

            previous_observation = observation

        patterns = []

        for application, data in application_data.items():
            drain_rates = data["drain_rates"]

            average_drain_rate = (
                sum(drain_rates) / len(drain_rates)
                if drain_rates
                else None
            )

            patterns.append(
                ApplicationBatteryPattern(
                    application=application,
                    observation_count=len(data["observations"]),
                    battery_drop=data["battery_drop"],
                    average_drain_rate=average_drain_rate,
                )
            )

        patterns.sort(
            key=lambda pattern: pattern.battery_drop,
            reverse=True,
        )

        return ApplicationBatteryPatternResult(
            patterns=tuple(patterns)
        )