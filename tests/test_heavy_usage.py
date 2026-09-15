from datetime import datetime, timedelta

import pytest

from observations.battery_discharge import DischargeSession
from observations.heavy_usage import (
    HeavyUsageDetection,
    HeavyUsageDetectionResult,
    HeavyUsageResult,
)
from observations.observation import Observation


class FakeAccess:
    def __init__(self, observations):
        self.observations = observations

    def count(self):
        return len(self.observations)

    def recent(self, limit):
        return self.observations


def make_observation(
    timestamp,
    battery,
    charging=False,
):
    return Observation(
        timestamp=timestamp,
        battery_percentage=battery,
        charging_status=charging,
        battery_time_left=None,
        cpu_usage=None,
        ram_usage=None,
        active_application=None,
    )


def make_session_observations(
    start_hour,
    start_battery,
    end_battery,
    duration_hours,
):
    start_time = datetime(2026, 1, 1, start_hour, 0)
    end_time = start_time + timedelta(hours=duration_hours)

    return [
        make_observation(
            start_time,
            start_battery,
        ),
        make_observation(
            end_time,
            end_battery,
        ),
        make_observation(
            end_time + timedelta(minutes=1),
            end_battery,
            charging=True,
        ),
    ]


def test_no_sessions_returns_empty_result():
    result = HeavyUsageDetection(
        FakeAccess([])
    ).calculate()

    assert result.session_count == 0
    assert result.average_drain_rate is None
    assert result.heavy_sessions == ()


def test_single_session_is_not_classified_as_heavy():
    observations = make_session_observations(
        start_hour=10,
        start_battery=90,
        end_battery=80,
        duration_hours=1,
    )

    result = HeavyUsageDetection(
        FakeAccess(observations)
    ).calculate()

    assert result.session_count == 1
    assert result.average_drain_rate is None
    assert result.heavy_sessions == ()


def test_average_drain_rate_is_calculated():
    observations = (
        make_session_observations(
            10,
            90,
            80,
            2,
        )
        + make_session_observations(
            14,
            80,
            70,
            1,
        )
    )

    result = HeavyUsageDetection(
        FakeAccess(observations)
    ).calculate()

    assert result.average_drain_rate == pytest.approx(7.5)


def test_heavy_session_is_detected():
    observations = (
        make_session_observations(
            10,
            90,
            80,
            2,
        )
        + make_session_observations(
            14,
            80,
            70,
            1,
        )
        + make_session_observations(
            18,
            70,
            50,
            1,
        )
    )

    result = HeavyUsageDetection(
        FakeAccess(observations)
    ).calculate()

    assert len(result.heavy_sessions) == 1

    heavy = result.heavy_sessions[0]

    assert heavy.drain_rate == pytest.approx(20.0)
    assert heavy.excess_drain_rate == pytest.approx(
    8.3333333
    )


def test_normal_sessions_are_not_classified_as_heavy():
    observations = (
        make_session_observations(
            10,
            90,
            80,
            1,
        )
        + make_session_observations(
            14,
            80,
            70,
            1,
        )
        + make_session_observations(
            18,
            70,
            60,
            1,
        )
    )

    result = HeavyUsageDetection(
        FakeAccess(observations)
    ).calculate()

    assert result.heavy_sessions == ()


def test_heavy_sessions_are_sorted_by_drain_rate():
    observations = (
        make_session_observations(
            10,
            90,
            80,
            2,
        )
        + make_session_observations(
            14,
            80,
            60,
            1,
        )
        + make_session_observations(
            18,
            60,
            30,
            1,
        )
        + make_session_observations(
            22,
            30,
            10,
            1,
        )
    )

    result = HeavyUsageDetection(
        FakeAccess(observations)
    ).calculate()

    rates = [
        heavy.drain_rate
        for heavy in result.heavy_sessions
    ]

    assert rates == sorted(
        rates,
        reverse=True,
    )


def test_original_sessions_are_preserved():
    observations = (
        make_session_observations(
            10,
            90,
            80,
            2,
        )
        + make_session_observations(
            14,
            80,
            60,
            1,
        )
        + make_session_observations(
            18,
            60,
            30,
            1,
        )
    )

    result = HeavyUsageDetection(
        FakeAccess(observations)
    ).calculate()

    assert all(
        isinstance(
            heavy.session,
            DischargeSession,
        )
        for heavy in result.heavy_sessions
    )


def test_result_is_immutable():
    result = HeavyUsageDetectionResult(
        session_count=2,
        average_drain_rate=10.0,
        heavy_sessions=(),
    )

    with pytest.raises(AttributeError):
        result.session_count = 5


def test_heavy_usage_result_is_immutable():
    session = DischargeSession(
        start_time=datetime(2026, 1, 1, 10, 0),
        end_time=datetime(2026, 1, 1, 11, 0),
        start_battery=90,
        end_battery=60,
        battery_change=-30,
        duration_hours=1,
        drain_rate=30.0,
        observation_count=2,
    )

    result = HeavyUsageResult(
        session=session,
        drain_rate=30.0,
        excess_drain_rate=20.0,
    )

    with pytest.raises(AttributeError):
        result.drain_rate = 50.0