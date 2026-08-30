from datetime import datetime
from typing import Optional

from observations.observation import Observation


class ObservationFactory:
    """Creates standardized Observation objects from collector data."""

    @staticmethod
    def create(
        battery: Optional[dict] = None,
        system: Optional[dict] = None,
        timestamp: Optional[datetime] = None,
    ) -> Observation:
        """
        Create an Observation from battery and system collector data.
        """

        battery = battery or {}
        system = system or {}

        return Observation(
            timestamp=timestamp or datetime.now(),
            battery_percentage=battery.get("battery_percentage"),
            charging_status=battery.get("charging_status"),
            battery_time_left=battery.get("battery_time_left"),
            cpu_usage=system.get("cpu_usage"),
            ram_usage=system.get("ram_usage"),
            active_application=system.get("active_application"),
        )