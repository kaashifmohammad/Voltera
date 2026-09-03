import csv
from datetime import datetime
from pathlib import Path

from observations.observation import Observation


class ObservationRepository:
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