from datetime import datetime, timedelta

from observations.battery_trend import (
    BatteryTrend,
    BatteryTrendResult,
    TrendDirection,
)
from observations.observation import Observation


class FakeHistoricalDataAccess:
    def __init__(self, observations):
        self.observations = observations

    def count(self):
        return len(self.observations)

    def recent(self, count=10):
        return self.observations[:count]


def make_observation(battery, timestamp=None):
        return Observation(
        timestamp=timestamp or datetime.now(),
        battery_percentage=battery,
        charging_status=False,
        battery_time_left=None,
        cpu_usage=20.0,
        ram_usage=40.0,
        active_application="Test",
    )


def test_insufficient_data_when_history_is_empty():
    access = FakeHistoricalDataAccess([])
    trend = BatteryTrend(access)

    result = trend.calculate()

    assert result.trend == TrendDirection.INSUFFICIENT_DATA


def test_insufficient_data_when_fewer_than_three_valid_values_exist():
    observations = [
        make_observation(80),
        make_observation(75),
    ]

    access = FakeHistoricalDataAccess(observations)
    trend = BatteryTrend(access)

    result = trend.calculate()

    assert result.trend == TrendDirection.INSUFFICIENT_DATA


def test_detects_rising_battery_trend():
    observations = [
        make_observation(40),
        make_observation(50),
        make_observation(60),
    ]

    access = FakeHistoricalDataAccess(observations)
    trend = BatteryTrend(access)

    result = trend.calculate()

    assert result.trend == TrendDirection.RISING


def test_detects_declining_battery_trend():
    observations = [
        make_observation(80),
        make_observation(70),
        make_observation(60),
    ]

    access = FakeHistoricalDataAccess(observations)
    trend = BatteryTrend(access)

    result = trend.calculate()

    assert result.trend == TrendDirection.DECLINING


def test_detects_stable_battery_trend():
    observations = [
        make_observation(50),
        make_observation(51),
        make_observation(50),
    ]

    access = FakeHistoricalDataAccess(observations)
    trend = BatteryTrend(access)

    result = trend.calculate()

    assert result.trend == TrendDirection.STABLE


def test_ignores_missing_battery_values():
    observations = [
        make_observation(80),
        make_observation(None),
        make_observation(70),
        make_observation(60),
    ]

    access = FakeHistoricalDataAccess(observations)
    trend = BatteryTrend(access)

    result = trend.calculate()

    assert result.trend == TrendDirection.DECLINING


def test_returns_battery_values_used_for_calculation():
    observations = [
        make_observation(80),
        make_observation(70),
        make_observation(60),
    ]

    access = FakeHistoricalDataAccess(observations)
    trend = BatteryTrend(access)

    result = trend.calculate()

    assert result.observation_count == 3
    assert result.first_battery == 80
    assert result.last_battery == 60
    assert result.change == -20


def test_result_is_immutable_dataclass():
    result = BatteryTrendResult(
        trend=TrendDirection.RISING,
        observation_count=3,
        first_battery=40,
        last_battery=60,
        change=20,
    )

    assert result.trend == TrendDirection.RISING

    try:
        result.change = 30
        assert False
    except AttributeError:
        pass

def test_orders_observations_chronologically_before_calculation():
    now = datetime.now()

    observations = [
        make_observation(60, now + timedelta(minutes=2)),
        make_observation(40, now),
        make_observation(50, now + timedelta(minutes=1)),
    ]

    access = FakeHistoricalDataAccess(observations)
    trend = BatteryTrend(access)

    result = trend.calculate()

    assert result.trend == TrendDirection.RISING
    assert result.first_battery == 40
    assert result.last_battery == 60
    assert result.change == 20