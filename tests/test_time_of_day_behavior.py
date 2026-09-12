from datetime import datetime, timedelta

import pytest

from observations.observation import Observation
from observations.time_of_day_behavior import (
    TimeOfDay,
    TimeOfDayBatteryBehavior,
    TimeOfDayBehaviorResult,
    TimeOfDayStats,
)


class FakeAccess:
    def __init__(self, observations):
        self.observations = observations

    def count(self):
        return len(self.observations)

    def recent(self, limit):
        return self.observations


def make_observation(timestamp, battery, charging=False):
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
    timestamp,
    start_battery,
    end_battery,
    duration_hours=1,
):
    return [
        make_observation(
            timestamp,
            start_battery,
            charging=False,
        ),
        make_observation(
            timestamp + timedelta(hours=duration_hours),
            end_battery,
            charging=False,
        ),
        make_observation(
            timestamp + timedelta(hours=duration_hours, minutes=1),
            end_battery,
            charging=True,
        ),
    ]


def make_access_for_sessions(sessions):
    observations = []

    for session in sessions:
        observations.extend(
            make_session_observations(
                session["timestamp"],
                session["start_battery"],
                session["end_battery"],
                session["duration_hours"],
            )
        )

    return FakeAccess(observations)


def test_empty_history_returns_empty_stats():
    result = TimeOfDayBatteryBehavior(
        FakeAccess([])
    ).calculate()

    assert isinstance(result, TimeOfDayBehaviorResult)

    for stats in (
        result.morning,
        result.afternoon,
        result.evening,
        result.night,
    ):
        assert stats.session_count == 0
        assert stats.average_battery_drop is None
        assert stats.average_drain_rate is None


def test_time_classification():
    analyzer = TimeOfDayBatteryBehavior(FakeAccess([]))

    assert analyzer._classify(
        datetime(2026, 1, 1, 7).time()
    ) == TimeOfDay.MORNING

    assert analyzer._classify(
        datetime(2026, 1, 1, 12).time()
    ) == TimeOfDay.AFTERNOON

    assert analyzer._classify(
        datetime(2026, 1, 1, 17).time()
    ) == TimeOfDay.EVENING

    assert analyzer._classify(
        datetime(2026, 1, 1, 22).time()
    ) == TimeOfDay.NIGHT

    assert analyzer._classify(
        datetime(2026, 1, 1, 3).time()
    ) == TimeOfDay.NIGHT


def test_sessions_are_grouped_by_start_time():
    sessions = [
        {
            "timestamp": datetime(2026, 1, 1, 7),
            "start_battery": 90,
            "end_battery": 80,
            "duration_hours": 1,
        },
        {
            "timestamp": datetime(2026, 1, 1, 13),
            "start_battery": 80,
            "end_battery": 70,
            "duration_hours": 1,
        },
        {
            "timestamp": datetime(2026, 1, 1, 18),
            "start_battery": 70,
            "end_battery": 55,
            "duration_hours": 1,
        },
        {
            "timestamp": datetime(2026, 1, 1, 23),
            "start_battery": 55,
            "end_battery": 45,
            "duration_hours": 1,
        },
    ]

    result = TimeOfDayBatteryBehavior(
        make_access_for_sessions(sessions)
    ).calculate()

    assert result.morning.session_count == 1
    assert result.afternoon.session_count == 1
    assert result.evening.session_count == 1
    assert result.night.session_count == 1


def test_average_battery_drop_is_calculated():
    sessions = [
        {
            "timestamp": datetime(2026, 1, 1, 18),
            "start_battery": 90,
            "end_battery": 80,
            "duration_hours": 1,
        },
        {
            "timestamp": datetime(2026, 1, 2, 19),
            "start_battery": 80,
            "end_battery": 60,
            "duration_hours": 2,
        },
    ]

    result = TimeOfDayBatteryBehavior(
        make_access_for_sessions(sessions)
    ).calculate()

    assert result.evening.average_battery_drop == pytest.approx(15.0)


def test_average_drain_rate_is_calculated():
    sessions = [
        {
            "timestamp": datetime(2026, 1, 1, 18),
            "start_battery": 90,
            "end_battery": 80,
            "duration_hours": 1,
        },
        {
            "timestamp": datetime(2026, 1, 2, 19),
            "start_battery": 80,
            "end_battery": 60,
            "duration_hours": 2,
        },
    ]

    result = TimeOfDayBatteryBehavior(
        make_access_for_sessions(sessions)
    ).calculate()

    assert result.evening.average_drain_rate == pytest.approx(10.0)


def test_session_crossing_time_boundary_uses_start_time():
    sessions = [
        {
            "timestamp": datetime(2026, 1, 1, 21, 30),
            "start_battery": 90,
            "end_battery": 80,
            "duration_hours": 2,
        },
    ]

    result = TimeOfDayBatteryBehavior(
        make_access_for_sessions(sessions)
    ).calculate()

    assert result.evening.session_count == 1
    assert result.night.session_count == 0


def test_stats_are_immutable():
    stats = TimeOfDayStats(
        session_count=1,
        average_battery_drop=10.0,
        average_drain_rate=10.0,
    )

    with pytest.raises(AttributeError):
        stats.session_count = 2


def test_result_is_immutable():
    result = TimeOfDayBehaviorResult(
        morning=TimeOfDayStats(0, None, None),
        afternoon=TimeOfDayStats(0, None, None),
        evening=TimeOfDayStats(0, None, None),
        night=TimeOfDayStats(0, None, None),
    )

    with pytest.raises(AttributeError):
        result.morning = TimeOfDayStats(1, 5.0, 5.0)