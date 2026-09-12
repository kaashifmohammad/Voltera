from dataclasses import dataclass
from datetime import datetime

from observations.historical_data_access import HistoricalDataAccess


@dataclass(frozen=True)
class DischargeSession:
    """Represents one continuous battery discharge session."""

    start_time: datetime
    end_time: datetime
    start_battery: float
    end_battery: float
    battery_change: float
    duration_hours: float
    drain_rate: float
    observation_count: int


class BatteryDischarge:
    """Identifies and analyzes historical battery discharge sessions."""

    def __init__(self, access: HistoricalDataAccess):
        self.access = access

    def calculate(self) -> list[DischargeSession]:
        """Calculate individual battery discharge sessions."""

        observations = self.access.recent(self.access.count())

        observations = sorted(
            observations,
            key=lambda observation: observation.timestamp,
        )

        sessions: list[DischargeSession] = []
        current_observations = []

        for observation in observations:
            if observation.charging_status is not False:
                self._finalize_session(
                    current_observations,
                    sessions,
                )
                current_observations = []
                continue

            if observation.battery_percentage is None:
                continue

            if not current_observations:
                current_observations.append(observation)
                continue

            previous = current_observations[-1]

            if observation.battery_percentage > previous.battery_percentage:
                self._finalize_session(
                    current_observations,
                    sessions,
                )
                current_observations = [observation]
                continue

            current_observations.append(observation)

        self._finalize_session(
            current_observations,
            sessions,
        )

        return sessions

    @staticmethod
    def _finalize_session(
        observations,
        sessions: list[DischargeSession],
    ) -> None:
        """Convert a valid observation sequence into a discharge session."""

        if len(observations) < 2:
            return

        start = observations[0]
        end = observations[-1]

        battery_change = end.battery_percentage - start.battery_percentage

        if battery_change >= 0:
            return

        duration_seconds = (
            end.timestamp - start.timestamp
        ).total_seconds()

        if duration_seconds <= 0:
            return

        duration_hours = duration_seconds / 3600

        drain_rate = abs(battery_change) / duration_hours

        sessions.append(
            DischargeSession(
                start_time=start.timestamp,
                end_time=end.timestamp,
                start_battery=start.battery_percentage,
                end_battery=end.battery_percentage,
                battery_change=battery_change,
                duration_hours=duration_hours,
                drain_rate=drain_rate,
                observation_count=len(observations),
            )
        )