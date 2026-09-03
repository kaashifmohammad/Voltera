from datetime import datetime

from observations.observation import Observation
from observations.observation_repository import ObservationRepository
from observations.observation_store import ObservationStore


def create_observation():
    return Observation(
        timestamp=datetime(2026, 9, 3, 12, 0, 0),
        battery_percentage=80,
        charging_status=False,
        battery_time_left=3600,
        cpu_usage=25.5,
        ram_usage=55.2,
        active_application="TestApp",
    )


def test_repository_returns_empty_list_when_file_missing(tmp_path):
    repository = ObservationRepository(tmp_path / "missing.csv")

    assert repository.get_all() == []


def test_repository_loads_saved_observation(tmp_path):
    file_path = tmp_path / "observations.csv"

    store = ObservationStore(file_path)
    observation = create_observation()
    store.save(observation)

    repository = ObservationRepository(file_path)
    observations = repository.get_all()

    assert len(observations) == 1
    assert observations[0] == observation


def test_repository_loads_multiple_observations(tmp_path):
    file_path = tmp_path / "observations.csv"

    store = ObservationStore(file_path)

    store.save(create_observation())
    store.save(create_observation())

    repository = ObservationRepository(file_path)

    assert len(repository.get_all()) == 2


def test_repository_skips_invalid_rows(tmp_path):
    file_path = tmp_path / "observations.csv"

    file_path.write_text(
        "timestamp,battery_percentage,charging_status,battery_time_left,"
        "cpu_usage,ram_usage,active_application\n"
        "invalid,row,data\n",
        encoding="utf-8",
    )

    repository = ObservationRepository(file_path)

    assert repository.get_all() == []