from datetime import datetime

from observations.observation import Observation
from observations.observation_validator import ObservationValidator


def make_observation(**overrides):
    data = {
        "timestamp": datetime.now(),
        "battery_percentage": 75,
        "charging_status": True,
        "battery_time_left": 3600,
        "cpu_usage": 25,
        "ram_usage": 50,
        "active_application": "Code.exe",
    }

    data.update(overrides)

    return Observation(**data)


def test_valid_observation():
    observation = make_observation()

    assert ObservationValidator.is_valid(observation) is True


def test_missing_battery_is_valid():
    observation = make_observation(
        battery_percentage=None,
        charging_status=None,
        battery_time_left=None,
    )

    assert ObservationValidator.is_valid(observation) is True


def test_invalid_battery_percentage():
    observation = make_observation(battery_percentage=150)

    assert ObservationValidator.is_valid(observation) is False


def test_invalid_cpu_usage():
    observation = make_observation(cpu_usage=-1)

    assert ObservationValidator.is_valid(observation) is False


def test_invalid_ram_usage():
    observation = make_observation(ram_usage=101)

    assert ObservationValidator.is_valid(observation) is False


def test_invalid_timestamp():
    observation = make_observation(timestamp=None)

    assert ObservationValidator.is_valid(observation) is False