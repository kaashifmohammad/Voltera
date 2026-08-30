from observations.observation import Observation


class ObservationValidator:
    """Validates Observation objects before they enter the data pipeline."""

    @staticmethod
    def is_valid(observation: Observation) -> bool:
        """Return True when the observation contains valid values."""

        if not isinstance(observation, Observation):
            return False

        if observation.timestamp is None:
            return False

        if not ObservationValidator._valid_percentage(
            observation.battery_percentage
        ):
            return False

        if not ObservationValidator._valid_percentage(
            observation.cpu_usage
        ):
            return False

        if not ObservationValidator._valid_percentage(
            observation.ram_usage
        ):
            return False

        return True

    @staticmethod
    def _valid_percentage(value) -> bool:
        """Validate an optional percentage value between 0 and 100."""

        if value is None:
            return True

        if not isinstance(value, (int, float)):
            return False

        return 0 <= value <= 100