from collectors.collector_manager import CollectorManager
from observations.observation import Observation
from observations.observation_validator import ObservationValidator


def test_collector_pipeline_produces_valid_observation():
    manager = CollectorManager()

    observation = manager.collect()

    assert isinstance(observation, Observation)
    assert ObservationValidator.is_valid(observation)


def test_collector_pipeline_contains_timestamp():
    manager = CollectorManager()

    observation = manager.collect()

    assert observation.timestamp is not None


def test_collector_pipeline_contains_system_metrics():
    manager = CollectorManager()

    observation = manager.collect()

    assert observation.cpu_usage is not None
    assert observation.ram_usage is not None