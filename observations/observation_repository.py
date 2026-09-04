import csv
from datetime import datetime
from pathlib import Path

from observations.observation import Observation
from observations.observation_validator import ObservationValidator
from observations.historical_intelligence import HistoricalIntelligence

class ObservationRepository(HistoricalIntelligence):
    """Provides access to persisted historical observations."""

    def __init__(self, file_path="data/observations.csv"):
        self.file_path = Path(file_path)

    def get_all(self):
        """Load all valid observations from the historical data file."""

        if not self.file_path.exists():
            return []

        observations = []

        with self.file_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    observation = Observation(
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        battery_percentage=self._to_float(
                            row["battery_percentage"]
                        ),
                        charging_status=self._to_bool(
                            row["charging_status"]
                        ),
                        battery_time_left=self._to_float(
                            row["battery_time_left"]
                        ),
                        cpu_usage=self._to_float(row["cpu_usage"]),
                        ram_usage=self._to_float(row["ram_usage"]),
                        active_application=row["active_application"] or None,
                    )

                    if ObservationValidator.is_valid(observation):
                        observations.append(observation)

                except (KeyError, TypeError, ValueError):
                    continue

        return observations

    @staticmethod
    def _to_float(value):
        if value in (None, ""):
            return None
        return float(value)

    @staticmethod
    def _to_bool(value):
        if value in (None, ""):
            return None

        if value.lower() == "true":
            return True

        if value.lower() == "false":
            return False

        return None

    def get_latest(self):
        """Return the most recent observation, or None if empty."""

        observations = self.get_all()

        if not observations:
            return None

        return max(observations, key=lambda observation: observation.timestamp)

    def get_recent(self, count=10):
        """Return the most recent observations."""

        if count <= 0:
            return []

        observations = self.get_all()

        observations.sort(
            key=lambda observation: observation.timestamp,
            reverse=True,
        )

        return observations[:count]

    def get_between(self, start, end):
        """Return observations within a time range."""

        observations = self.get_all()

        return [
            observation
            for observation in observations
            if start <= observation.timestamp <= end
        ]

    def count(self):
        """Return the number of valid stored observations."""

        return len(self.get_all())