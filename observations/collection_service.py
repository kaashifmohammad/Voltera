from collectors.collector_manager import CollectorManager
from observations.observation_pipeline import ObservationPipeline


class CollectionService:
    """Runs the real-data collection and persistence workflow."""

    def __init__(self, collector_manager=None, pipeline=None):
        self.collector_manager = collector_manager or CollectorManager()
        self.pipeline = pipeline or ObservationPipeline()

    def collect_and_store(self):
        """Collect a live observation, validate it, and persist it."""

        observation = self.collector_manager.collect()

        return self.pipeline.process(observation)