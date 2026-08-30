from datetime import datetime

from observations.observation import Observation
from observations.observation_factory import ObservationFactory


def test_factory_creates_observation():
    timestamp = datetime.now()

    battery = {
        "battery_percentage": 75,
        "charging_status": True,
        "battery_time_left": 3600,
    }

    system = {
        "cpu_usage": 25,
        "ram_usage": 50,
        "active_application": "Code.exe",
    }

    observation = ObservationFactory.create(
        timestamp=timestamp,
        battery=battery,
        system=system,
    )

    assert isinstance(observation, Observation)
    assert observation.timestamp == timestamp
    assert observation.battery_percentage == 75
    assert observation.charging_status is True
    assert observation.battery_time_left == 3600
    assert observation.cpu_usage == 25
    assert observation.ram_usage == 50
    assert observation.active_application == "Code.exe"


def test_factory_uses_current_time_when_timestamp_missing():
    battery = {
        "battery_percentage": 60,
        "charging_status": False,
        "battery_time_left": 1800,
    }

    system = {
        "cpu_usage": 30,
        "ram_usage": 55,
        "active_application": "python.exe",
    }

    before = datetime.now()

    observation = ObservationFactory.create(
        battery=battery,
        system=system,
    )

    after = datetime.now()

    assert before <= observation.timestamp <= after