import psutil

from observations.observation_factory import ObservationFactory


class BatteryCollector:
    """Collects current battery and charging information."""

    def collect(self):
        """Collect battery state and return a standardized Observation."""

        battery = psutil.sensors_battery()

        if battery is None:
            battery_data = {
                "battery_percentage": None,
                "charging_status": None,
                "battery_time_left": None,
            }
        else:
            battery_data = {
                "battery_percentage": battery.percent,
                "charging_status": battery.power_plugged,
                "battery_time_left": battery.secsleft,
            }

        return ObservationFactory.create(
            battery=battery_data
        )