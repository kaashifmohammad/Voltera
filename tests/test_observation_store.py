from datetime import datetime

from observations.observation import Observation
from observations.observation_store import ObservationStore


def create_observation():
    return Observation(
        timestamp=datetime(2026, 9, 2, 12, 0, 0),
        battery_percentage=75,
        charging_status=False,
        battery_time_left=3600,
        cpu_usage=20.5,
        ram_usage=60.2,
        active_application="TestApp",
    )


def test_observation_store_creates_file(tmp_path):
    file_path = tmp_path / "observations.csv"
    store = ObservationStore(file_path)

    store.save(create_observation())

    assert file_path.exists()


def test_observation_store_writes_headers(tmp_path):
    file_path = tmp_path / "observations.csv"
    store = ObservationStore(file_path)

    store.save(create_observation())

    content = file_path.read_text(encoding="utf-8")

    assert "timestamp" in content
    assert "battery_percentage" in content
    assert "cpu_usage" in content
    assert "ram_usage" in content


def test_observation_store_writes_observation(tmp_path):
    file_path = tmp_path / "observations.csv"
    store = ObservationStore(file_path)

    store.save(create_observation())

    content = file_path.read_text(encoding="utf-8")

    assert "75" in content
    assert "TestApp" in content


def test_observation_store_appends_observations(tmp_path):
    file_path = tmp_path / "observations.csv"
    store = ObservationStore(file_path)

    store.save(create_observation())
    store.save(create_observation())

    lines = file_path.read_text(encoding="utf-8").splitlines()

    # Header + two observations
    assert len(lines) == 3