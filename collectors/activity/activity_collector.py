import psutil

from observations.observation_factory import ObservationFactory


class ActivityCollector:
    """Collects current system activity information."""

    def collect(self):
        """Collect active application and process activity."""

        active_application = "Unknown"
        max_cpu = 0.0

        for process in psutil.process_iter(["name", "cpu_percent"]):
            try:
                cpu = process.info["cpu_percent"]

                if cpu is not None and cpu > max_cpu:
                    max_cpu = cpu
                    active_application = process.info["name"] or "Unknown"

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

        return ObservationFactory.create(
            system={
                "active_application": active_application,
            }
        )