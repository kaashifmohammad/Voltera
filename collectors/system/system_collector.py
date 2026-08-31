import psutil

from observations.observation_factory import ObservationFactory


class SystemCollector:
    """Collects current system-level device metrics."""

    def collect(self):
        """Collect CPU, RAM, and active application information."""

        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent

        active_application = "Unknown"
        max_cpu = 0

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

        system_data = {
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "active_application": active_application,
        }

        return ObservationFactory.create(system=system_data)