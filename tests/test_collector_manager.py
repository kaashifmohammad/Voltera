from collectors.collector_manager import CollectorManager
from observations.observation import Observation


def test_collector_manager_returns_observation():
    manager = CollectorManager()

    observation = manager.collect()

    assert isinstance(observation, Observation)


def test_collector_manager_collects_system_data():
    manager = CollectorManager()

    observation = manager.collect()

    assert observation.cpu_usage is not None
    assert observation.ram_usage is not None


def test_collector_manager_collects_battery_data():
    manager = CollectorManager()

    observation = manager.collect()

    # Battery information may legitimately be unavailable.
    if observation.battery_percentage is not None:
        assert 0 <= observation.battery_percentage <= 100