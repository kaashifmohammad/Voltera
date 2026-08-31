from collectors.battery.battery_collector import BatteryCollector
from collectors.system.system_collector import SystemCollector
from observations.observation_factory import ObservationFactory


class CollectorManager:
    """Coordinates device collectors and produces a complete observation."""

    def __init__(self):
        self.battery_collector = BatteryCollector()
        self.system_collector = SystemCollector()

    def collect(self):
        """Collect battery and system data into one Observation."""

        battery_observation = self.battery_collector.collect()
        system_observation = self.system_collector.collect()

        battery_data = {
            "battery_percentage": battery_observation.battery_percentage,
            "charging_status": battery_observation.charging_status,
            "battery_time_left": battery_observation.battery_time_left,
        }

        system_data = {
            "cpu_usage": system_observation.cpu_usage,
            "ram_usage": system_observation.ram_usage,
            "active_application": system_observation.active_application,
        }

        return ObservationFactory.create(
            battery=battery_data,
            system=system_data,
        )