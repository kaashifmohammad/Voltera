from datetime import datetime, timedelta

from observations.battery_discharge import (
    BatteryDischarge,
    DischargeSession,
)
from observations.observation import Observation


class FakeHistoricalDataAccess:
    def __init__(self, observations):
        self.observations = observations

    def count(self):
        return len(self.observations)

    def recent(self, count=10):
        return self.observations[:count]


def make_observation(
    battery,
    charging,
    minutes,
):
    return Observation(
        timestamp=datetime(2026, 9, 12, 10, 0, 0)
        + timedelta(minutes=minutes),
        battery_percentage=battery,
        charging_status=charging,
        battery_time_left=None,
        cpu_usage=20.0,
        ram_usage=40.0,
        active_application="TestApp",
    )


def test_returns_no_sessions_when_history_is_empty():
    access = FakeHistoricalDataAccess([])
    discharge = BatteryDischarge(access)

    result = discharge.calculate()

    assert result == []


def test_creates_one_discharge_session():
    observations = [
        make_observation(90, False, 0),
        make_observation(85, False, 10),
        make_observation(80, False, 20),
    ]

    access = FakeHistoricalDataAccess(observations)
    discharge = BatteryDischarge(access)

    result = discharge.calculate()

    assert len(result) == 1


def test_calculates_session_values():
    observations = [
        make_observation(90, False, 0),
        make_observation(85, False, 30),
    ]

    access = FakeHistoricalDataAccess(observations)
    discharge = BatteryDischarge(access)

    result = discharge.calculate()

    session = result[0]

    assert session.start_battery == 90
    assert session.end_battery == 85
    assert session.battery_change == -5
    assert session.duration_hours == 0.5
    assert session.drain_rate == 10.0
    assert session.observation_count == 2


def test_charging_breaks_discharge_sessions():
    observations = [
        make_observation(90, False, 0),
        make_observation(85, False, 10),
        make_observation(90, True, 20),
        make_observation(85, False, 30),
        make_observation(80, False, 40),
    ]

    access = FakeHistoricalDataAccess(observations)
    discharge = BatteryDischarge(access)

    result = discharge.calculate()

    assert len(result) == 2


def test_ignores_non_discharging_increases():
    observations = [
        make_observation(70, False, 0),
        make_observation(75, False, 10),
        make_observation(65, False, 20),
    ]

    access = FakeHistoricalDataAccess(observations)
    discharge = BatteryDischarge(access)

    result = discharge.calculate()

    assert len(result) == 1
    assert result[0].start_battery == 75
    assert result[0].end_battery == 65


def test_ignores_missing_values():
    observations = [
        make_observation(90, False, 0),
        make_observation(None, False, 10),
        make_observation(80, False, 20),
    ]

    access = FakeHistoricalDataAccess(observations)
    discharge = BatteryDischarge(access)

    result = discharge.calculate()

    assert len(result) == 1
    assert result[0].start_battery == 90
    assert result[0].end_battery == 80


def test_orders_observations_chronologically():
    observations = [
        make_observation(80, False, 20),
        make_observation(90, False, 0),
        make_observation(85, False, 10),
    ]

    access = FakeHistoricalDataAccess(observations)
    discharge = BatteryDischarge(access)

    result = discharge.calculate()

    assert len(result) == 1
    assert result[0].start_battery == 90
    assert result[0].end_battery == 80


def test_session_result_is_immutable():
    session = DischargeSession(
        start_time=datetime(2026, 9, 12, 10, 0),
        end_time=datetime(2026, 9, 12, 10, 30),
        start_battery=90,
        end_battery=85,
        battery_change=-5,
        duration_hours=0.5,
        drain_rate=10.0,
        observation_count=2,
    )

    try:
        session.drain_rate = 20.0
        assert False
    except AttributeError:
        pass