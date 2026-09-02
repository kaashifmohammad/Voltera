from observations.observation_validator import ObservationValidator
from observations.observation_store import ObservationStore


class ObservationPipeline:
    """Validates and persists collected observations."""

    def __init__(self, store=None):
        self.store = store or ObservationStore()

    def process(self, observation):
        """Validate an observation and persist it if valid."""

        if not ObservationValidator.is_valid(observation):
            raise ValueError("Invalid observation")

        self.store.save(observation)

        return observation