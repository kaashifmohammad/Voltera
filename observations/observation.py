from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Observation:
    """
    Immutable snapshot of the device state at a specific point in time.
    """

    timestamp: datetime
    battery_percentage: Optional[float]
    charging_status: Optional[bool]
    battery_time_left: Optional[float]
    cpu_usage: Optional[float]
    ram_usage: Optional[float]
    active_application: Optional[str]

    def to_dict(self) -> dict:
        """Return the observation as a dictionary."""
        return asdict(self)