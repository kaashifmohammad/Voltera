from datetime import datetime
from dataclasses import asdict

from observations.historical_data_access import HistoricalDataAccess
from observations.historical_data_service import HistoricalDataService
from observations.historical_intelligence_adapter import (
    HistoricalIntelligenceAdapter,
)
from observations.historical_statistics import (
    HistoricalStatistics,
    HistoricalStatisticsResult,
)
from observations.observation import Observation
from observations.observation_repository import ObservationRepository
from observations.observation_store import ObservationStore


def build_access(tmp_path, observations):
    file_path = tmp_path / "observations.csv"

    store = ObservationStore(file_path)

    for observation in observations:
        store.save(observation)

    repository = ObservationRepository(file_path)
    adapter = HistoricalIntelligenceAdapter(repository)
    service = HistoricalDataService(adapter)

    return HistoricalDataAccess(service)


def test_historical_statistics_calculates_core_statistics(tmp_path):
    observations = [
        Observation(
            timestamp=datetime(2026, 9, 1, 10, 0),
            battery_percentage=80,
            charging_status=False,
            battery_time_left=3600,
            cpu_usage=20,
            ram_usage=40,
            active_application="App1",
        ),
        Observation(
            timestamp=datetime(2026, 9, 1, 11, 0),
            battery_percentage=60,
            charging_status=True,
            battery_time_left=7200,
            cpu_usage=40,
            ram_usage=60,
            active_application="App2",
        ),
        Observation(
            timestamp=datetime(2026, 9, 1, 12, 0),
            battery_percentage=70,
            charging_status=False,
            battery_time_left=5400,
            cpu_usage=30,
            ram_usage=50,
            active_application="App3",
        ),
    ]

    access = build_access(tmp_path, observations)
    statistics = HistoricalStatistics(access)

    result = statistics.calculate()

    assert isinstance(result, HistoricalStatisticsResult)

    assert result.observation_count == 3
    assert result.average_battery == 70
    assert result.minimum_battery == 60
    assert result.maximum_battery == 80

    assert result.average_cpu == 30
    assert result.average_ram == 50

    assert result.charging_ratio == 1 / 3


def test_statistics_ignore_missing_values(tmp_path):
    observations = [
        Observation(
            timestamp=datetime(2026, 9, 1, 10, 0),
            battery_percentage=80,
            charging_status=True,
            battery_time_left=3600,
            cpu_usage=20,
            ram_usage=40,
            active_application="App1",
        ),
        Observation(
            timestamp=datetime(2026, 9, 1, 11, 0),
            battery_percentage=None,
            charging_status=None,
            battery_time_left=None,
            cpu_usage=None,
            ram_usage=60,
            active_application=None,
        ),
        Observation(
            timestamp=datetime(2026, 9, 1, 12, 0),
            battery_percentage=60,
            charging_status=False,
            battery_time_left=5400,
            cpu_usage=40,
            ram_usage=None,
            active_application="App3",
        ),
    ]

    access = build_access(tmp_path, observations)
    statistics = HistoricalStatistics(access)

    result = statistics.calculate()

    assert result.observation_count == 3

    assert result.average_battery == 70
    assert result.minimum_battery == 60
    assert result.maximum_battery == 80

    assert result.average_cpu == 30
    assert result.average_ram == 50

    assert result.charging_ratio == 0.5


def test_empty_history_returns_empty_statistics(tmp_path):
    access = build_access(tmp_path, [])
    statistics = HistoricalStatistics(access)

    result = statistics.calculate()

    assert result.observation_count == 0
    assert result.average_battery is None
    assert result.minimum_battery is None
    assert result.maximum_battery is None
    assert result.average_cpu is None
    assert result.average_ram is None
    assert result.charging_ratio is None


def test_statistics_result_can_be_converted_to_dict(tmp_path):
    observations = [
        Observation(
            timestamp=datetime(2026, 9, 1, 10, 0),
            battery_percentage=80,
            charging_status=False,
            battery_time_left=3600,
            cpu_usage=20,
            ram_usage=40,
            active_application="App1",
        ),
    ]

    access = build_access(tmp_path, observations)
    statistics = HistoricalStatistics(access)

    result = statistics.calculate()

    data = asdict(result)

    assert data["observation_count"] == 1
    assert data["average_battery"] == 80
    assert data["minimum_battery"] == 80
    assert data["maximum_battery"] == 80
    assert data["average_cpu"] == 20
    assert data["average_ram"] == 40
    assert data["charging_ratio"] == 0