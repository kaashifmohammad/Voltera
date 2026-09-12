from datetime import datetime, timedelta

import pytest

from observations.battery_discharge import DischargeSession
from observations.historical_usage_patterns import (
    HistoricalUsagePatternResult,
    HistoricalUsagePatterns,
)
from tests.test_context_classifier import result


class FakeAccess:
    def __init__(self, observations):
        self.observations = observations

    def count(self):
        return len(self.observations)

    def recent(self, limit):
        return list(self.observations)


def make_observation(
    timestamp,
    battery,
    charging=False,
):
    from observations.observation import Observation

    return Observation(
        timestamp=timestamp,
        battery_percentage=battery,
        charging_status=charging,
        battery_time_left=None,
        cpu_usage=None,
        ram_usage=None,
        active_application=None,
    )


def test_returns_empty_result_when_no_sessions_exist():
    access = FakeAccess([])

    result = HistoricalUsagePatterns(access).calculate()

    assert result.session_count == 0
    assert result.average_duration_hours is None
    assert result.average_battery_drop is None
    assert result.average_drain_rate is None
    assert result.maximum_drain_rate is None
    assert result.average_observation_count is None


def test_aggregates_multiple_discharge_sessions():
    start = datetime(2026, 9, 1, 10, 0)

    observations = [
        make_observation(start, 90),
        make_observation(start + timedelta(hours=1), 80),
        make_observation(start + timedelta(hours=1, minutes=30), 80, True),
        make_observation(start + timedelta(hours=2), 70),
        make_observation(start + timedelta(hours=3), 60),
    ]

    access = FakeAccess(observations)

    result = HistoricalUsagePatterns(access).calculate()

    assert result.session_count == 2
    assert result.average_duration_hours == pytest.approx(1.0)
    assert result.average_battery_drop == pytest.approx(10.0)
    assert result.average_drain_rate == pytest.approx(10.0)
    assert result.maximum_drain_rate == pytest.approx(10.0)
    assert result.average_observation_count == pytest.approx(2.0)


def test_calculates_different_drain_rates():
    start = datetime(2026, 9, 1, 10, 0)

    observations = [
        make_observation(start, 90),
        make_observation(start + timedelta(hours=1), 80),
        make_observation(start + timedelta(hours=1, minutes=1), 80, True),
        make_observation(start + timedelta(hours=2), 60),
        make_observation(start + timedelta(hours=4), 50),
    ]

    access = FakeAccess(observations)

    result = HistoricalUsagePatterns(access).calculate()

    assert result.session_count == 2
    assert result.average_battery_drop == pytest.approx(10.0)
    assert result.average_drain_rate == pytest.approx(7.5)
    assert result.maximum_drain_rate == pytest.approx(10.0)


def test_average_observation_count_is_calculated():
    start = datetime(2026, 9, 1, 10, 0)

    observations = [
        make_observation(start, 90),
        make_observation(start + timedelta(minutes=30), 85),
        make_observation(start + timedelta(minutes=60), 80),
        make_observation(start + timedelta(minutes=61), 80, True),
        make_observation(start + timedelta(minutes=90), 70),
        make_observation(start + timedelta(minutes=120), 65),
        make_observation(start + timedelta(minutes=150), 60),
    ]

    access = FakeAccess(observations)

    result = HistoricalUsagePatterns(access).calculate()

    assert result.session_count == 2
    assert result.average_observation_count == pytest.approx(3.0)


def test_result_is_immutable():
    access = FakeAccess([])

    result = HistoricalUsagePatterns(access).calculate()

    with pytest.raises(AttributeError):
        result.session_count = 10


def test_result_is_dataclass():
    assert HistoricalUsagePatternResult.__dataclass_params__.frozen is True


def test_average_helper_returns_none_for_empty_values():
    assert HistoricalUsagePatterns._average([]) is None


def test_average_helper_calculates_mean():
    assert HistoricalUsagePatterns._average([2, 4, 6]) == pytest.approx(4.0)