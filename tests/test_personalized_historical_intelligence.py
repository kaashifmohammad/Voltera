from datetime import datetime, timedelta

import pytest

from observations.battery_trend import TrendDirection
from observations.observation import Observation
from observations.personalized_historical_intelligence import (
    PersonalizedHistoricalIntelligence,
    PersonalizedHistoricalIntelligenceResult,
)
from observations.time_of_day_behavior import TimeOfDay
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
    application=None,
):
    return Observation(
        timestamp=timestamp,
        battery_percentage=battery,
        charging_status=charging,
        battery_time_left=None,
        cpu_usage=None,
        ram_usage=None,
        active_application=application,
    )


def make_session(
    start_time,
    start_battery,
    end_battery,
    duration_hours,
    application=None,
):
    end_time = start_time + timedelta(hours=duration_hours)

    return [
        make_observation(
            start_time,
            start_battery,
            application=application,
        ),
        make_observation(
            end_time,
            end_battery,
            application=application,
        ),
        make_observation(
            end_time + timedelta(minutes=1),
            end_battery,
            charging=True,
        ),
    ]


def test_empty_data_returns_empty_personalized_result():
    result = PersonalizedHistoricalIntelligence(
        FakeAccess([])
    ).calculate()

    assert result.observation_count == 0
    assert result.average_battery is None
    assert result.minimum_battery is None
    assert result.maximum_battery is None
    assert result.battery_trend == TrendDirection.INSUFFICIENT_DATA
    assert result.average_discharge_duration_hours is None
    assert result.average_battery_drop is None
    assert result.average_drain_rate is None
    assert result.strongest_usage_period is None
    assert result.application_patterns == ()
    assert result.heavy_usage_session_count == 0
    assert result.average_historical_drain_rate is None


def test_statistics_are_aggregated():
    base = datetime(2026, 1, 1, 10, 0)

    observations = [
        make_observation(base, 90),
        make_observation(base + timedelta(minutes=10), 80),
        make_observation(base + timedelta(minutes=20), 70),
    ]

    result = PersonalizedHistoricalIntelligence(
        FakeAccess(observations)
    ).calculate()

    assert result.observation_count == 3
    assert result.average_battery == pytest.approx(80)
    assert result.minimum_battery == 70
    assert result.maximum_battery == 90


def test_battery_trend_is_aggregated():
    base = datetime(2026, 1, 1, 10, 0)

    observations = [
        make_observation(base, 90),
        make_observation(base + timedelta(minutes=10), 80),
        make_observation(base + timedelta(minutes=20), 70),
    ]

    result = PersonalizedHistoricalIntelligence(
        FakeAccess(observations)
    ).calculate()

    assert result.battery_trend == TrendDirection.DECLINING


def test_usage_patterns_are_aggregated():
    observations = make_session(
        datetime(2026, 1, 1, 10, 0),
        90,
        80,
        2,
    ) + make_session(
        datetime(2026, 1, 1, 14, 0),
        80,
        70,
        1,
    )

    result = PersonalizedHistoricalIntelligence(
        FakeAccess(observations)
    ).calculate()

    assert result.average_discharge_duration_hours == pytest.approx(1.5)
    assert result.average_battery_drop == pytest.approx(10)
    assert result.average_drain_rate == pytest.approx(7.5)


def test_strongest_usage_period_is_identified():
    observations = make_session(
        datetime(2026, 1, 1, 10, 0),
        90,
        80,
        2,
    ) + make_session(
        datetime(2026, 1, 1, 18, 0),
        80,
        60,
        1,
    )

    result = PersonalizedHistoricalIntelligence(
        FakeAccess(observations)
    ).calculate()

    assert result.strongest_usage_period == TimeOfDay.EVENING


def test_application_patterns_are_preserved():
    observations = [
        make_observation(
            datetime(2026, 1, 1, 10, 0),
            90,
            application="Chrome",
        ),
        make_observation(
            datetime(2026, 1, 1, 11, 0),
            80,
            application="Chrome",
        ),
        make_observation(
            datetime(2026, 1, 1, 12, 0),
            80,
            application="VS Code",
        ),
    ]

    result = PersonalizedHistoricalIntelligence(
        FakeAccess(observations)
    ).calculate()

    assert len(result.application_patterns) == 1
    assert result.application_patterns[0].application == "Chrome"


def test_heavy_usage_information_is_aggregated():
    observations = (
        make_session(
            datetime(2026, 1, 1, 10, 0),
            90,
            80,
            2,
        )
        + make_session(
            datetime(2026, 1, 1, 14, 0),
            80,
            70,
            1,
        )
        + make_session(
            datetime(2026, 1, 1, 18, 0),
            70,
            50,
            1,
        )
    )

    result = PersonalizedHistoricalIntelligence(
        FakeAccess(observations)
    ).calculate()

    assert result.heavy_usage_session_count == 1
    assert result.average_historical_drain_rate == pytest.approx(
        11.6666667
    )


def test_no_valid_usage_period_returns_none():
    observations = [
        make_observation(
            datetime(2026, 1, 1, 10, 0),
            90,
        ),
    ]

    result = PersonalizedHistoricalIntelligence(
        FakeAccess(observations)
    ).calculate()

    assert result.strongest_usage_period is None


def test_result_is_immutable():
    result = PersonalizedHistoricalIntelligenceResult(
        observation_count=10,
        average_battery=70,
        minimum_battery=40,
        maximum_battery=90,
        battery_trend=TrendDirection.DECLINING,
        average_discharge_duration_hours=2,
        average_battery_drop=10,
        average_drain_rate=5,
        strongest_usage_period=TimeOfDay.EVENING,
        application_patterns=(),
        heavy_usage_session_count=1,
        average_historical_drain_rate=5,
    )

    with pytest.raises(AttributeError):
        result.observation_count = 20