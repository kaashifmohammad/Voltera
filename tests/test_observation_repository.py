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

def test_repository_returns_latest_observation(tmp_path):
    file_path = tmp_path / "observations.csv"

    store = ObservationStore(file_path)

    first = Observation(
        timestamp=datetime(2026, 9, 3, 10, 0, 0),
        battery_percentage=80,
        charging_status=False,
        battery_time_left=3600,
        cpu_usage=20,
        ram_usage=50,
        active_application="App1",
    )

    second = Observation(
        timestamp=datetime(2026, 9, 3, 12, 0, 0),
        battery_percentage=70,
        charging_status=False,
        battery_time_left=3000,
        cpu_usage=30,
        ram_usage=60,
        active_application="App2",
    )

    store.save(first)
    store.save(second)

    repository = ObservationRepository(file_path)

    assert repository.get_latest() == second


def test_repository_returns_recent_observations(tmp_path):
    file_path = tmp_path / "observations.csv"

    store = ObservationStore(file_path)

    for hour in range(4):
        observation = Observation(
            timestamp=datetime(2026, 9, 3, 10 + hour, 0, 0),
            battery_percentage=80 - hour,
            charging_status=False,
            battery_time_left=3600,
            cpu_usage=20,
            ram_usage=50,
            active_application="TestApp",
        )
        store.save(observation)

    repository = ObservationRepository(file_path)

    recent = repository.get_recent(2)

    assert len(recent) == 2
    assert recent[0].timestamp > recent[1].timestamp


def test_repository_filters_by_time_range(tmp_path):
    file_path = tmp_path / "observations.csv"

    store = ObservationStore(file_path)

    for hour in range(4):
        observation = Observation(
            timestamp=datetime(2026, 9, 3, 10 + hour, 0, 0),
            battery_percentage=80,
            charging_status=False,
            battery_time_left=3600,
            cpu_usage=20,
            ram_usage=50,
            active_application="TestApp",
        )
        store.save(observation)

    repository = ObservationRepository(file_path)

    results = repository.get_between(
        datetime(2026, 9, 3, 11, 0, 0),
        datetime(2026, 9, 3, 12, 0, 0),
    )

    assert len(results) == 2


def test_repository_counts_observations(tmp_path):
    file_path = tmp_path / "observations.csv"

    store = ObservationStore(file_path)

    store.save(create_observation())
    store.save(create_observation())
    store.save(create_observation())

    repository = ObservationRepository(file_path)

    assert repository.count() == 3

def test_repository_skips_invalid_battery_value(tmp_path):
    file_path = tmp_path / "observations.csv"

    file_path.write_text(
        "timestamp,battery_percentage,charging_status,battery_time_left,"
        "cpu_usage,ram_usage,active_application\n"
        "2026-09-03T12:00:00,150,False,3600,20,50,TestApp\n",
        encoding="utf-8",
    )

    repository = ObservationRepository(file_path)

    assert repository.get_all() == []


def test_repository_skips_invalid_cpu_value(tmp_path):
    file_path = tmp_path / "observations.csv"

    file_path.write_text(
        "timestamp,battery_percentage,charging_status,battery_time_left,"
        "cpu_usage,ram_usage,active_application\n"
        "2026-09-03T12:00:00,80,False,3600,150,50,TestApp\n",
        encoding="utf-8",
    )

    repository = ObservationRepository(file_path)

    assert repository.get_all() == []


def test_repository_skips_invalid_ram_value(tmp_path):
    file_path = tmp_path / "observations.csv"

    file_path.write_text(
        "timestamp,battery_percentage,charging_status,battery_time_left,"
        "cpu_usage,ram_usage,active_application\n"
        "2026-09-03T12:00:00,80,False,3600,20,150,TestApp\n",
        encoding="utf-8",
    )

    repository = ObservationRepository(file_path)

    assert repository.get_all() == []


def test_repository_keeps_valid_and_skips_invalid_records(tmp_path):
    file_path = tmp_path / "observations.csv"

    file_path.write_text(
        "timestamp,battery_percentage,charging_status,battery_time_left,"
        "cpu_usage,ram_usage,active_application\n"
        "2026-09-03T12:00:00,80,False,3600,20,50,ValidApp\n"
        "2026-09-03T13:00:00,150,False,3600,20,50,InvalidApp\n",
        encoding="utf-8",
    )

    repository = ObservationRepository(file_path)

    observations = repository.get_all()

    assert len(observations) == 1
    assert observations[0].active_application == "ValidApp"