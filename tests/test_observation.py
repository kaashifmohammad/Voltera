from datetime import datetime

from observations.observation import Observation


def test_observation_creation():
    timestamp = datetime.now()

    observation = Observation(
        timestamp=timestamp,
        battery_percentage=75,
        charging_status=True,
        battery_time_left=3600,
        cpu_usage=25,
        ram_usage=50,
        active_application="Code.exe",
    )

    assert observation.timestamp == timestamp
    assert observation.battery_percentage == 75
    assert observation.charging_status is True
    assert observation.battery_time_left == 3600
    assert observation.cpu_usage == 25
    assert observation.ram_usage == 50
    assert observation.active_application == "Code.exe"


def test_observation_to_dict():
    timestamp = datetime.now()

    observation = Observation(
        timestamp=timestamp,
        battery_percentage=75,
        charging_status=True,
        battery_time_left=3600,
        cpu_usage=25,
        ram_usage=50,
        active_application="Code.exe",
    )

    data = observation.to_dict()

    assert data["timestamp"] == timestamp
    assert data["battery_percentage"] == 75
    assert data["charging_status"] is True
    assert data["battery_time_left"] == 3600
    assert data["cpu_usage"] == 25
    assert data["ram_usage"] == 50
    assert data["active_application"] == "Code.exe"