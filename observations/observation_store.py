import csv
from pathlib import Path

from observations.observation import Observation


class ObservationStore:
    """Persists validated observations as historical CSV records."""

    HEADERS = [
        "timestamp",
        "battery_percentage",
        "charging_status",
        "battery_time_left",
        "cpu_usage",
        "ram_usage",
        "active_application",
    ]

    def __init__(self, file_path="data/observations.csv"):
        self.file_path = Path(file_path)

    def save(self, observation: Observation):
        """Append an observation to the historical data file."""

        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        file_exists = self.file_path.exists()

        with self.file_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.HEADERS)

            if not file_exists or self.file_path.stat().st_size == 0:
                writer.writeheader()

            writer.writerow(
                {
                    "timestamp": observation.timestamp.isoformat(),
                    "battery_percentage": observation.battery_percentage,
                    "charging_status": observation.charging_status,
                    "battery_time_left": observation.battery_time_left,
                    "cpu_usage": observation.cpu_usage,
                    "ram_usage": observation.ram_usage,
                    "active_application": observation.active_application,
                }
            )