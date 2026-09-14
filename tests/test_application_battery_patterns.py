from datetime import datetime, timedelta

import pytest

from observations.application_battery_patterns import (
    ApplicationBatteryPattern,
    ApplicationBatteryPatternResult,
    ApplicationBatteryPatterns,
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


def test_empty_history_returns_empty_result():
    result = ApplicationBatteryPatterns(
        FakeAccess([])
    ).calculate()

    assert isinstance(result, ApplicationBatteryPatternResult)
    assert result.patterns == ()


def test_single_application_is_analyzed():
    start = datetime(2026, 1, 1, 10, 0)

    observations = [
        make_observation(
            start,
            80,
            application="Chrome",
        ),
        make_observation(
            start + timedelta(minutes=30),
            75,
            application="Chrome",
        ),
    ]

    result = ApplicationBatteryPatterns(
        FakeAccess(observations)
    ).calculate()

    assert len(result.patterns) == 1

    pattern = result.patterns[0]

    assert pattern.application == "Chrome"
    assert pattern.observation_count == 2
    assert pattern.battery_drop == pytest.approx(5.0)
    assert pattern.average_drain_rate == pytest.approx(10.0)


def test_multiple_applications_are_kept_separate():
    start = datetime(2026, 1, 1, 10, 0)

    observations = [
        make_observation(start, 90, application="Chrome"),
        make_observation(
            start + timedelta(minutes=30),
            85,
            application="Chrome",
        ),
        make_observation(
            start + timedelta(hours=1),
            80,
            application="VS Code",
        ),
        make_observation(
            start + timedelta(hours=1, minutes=30),
            70,
            application="VS Code",
        ),
    ]

    result = ApplicationBatteryPatterns(
        FakeAccess(observations)
    ).calculate()

    patterns = {
        pattern.application: pattern
        for pattern in result.patterns
    }

    assert patterns["Chrome"].battery_drop == pytest.approx(5.0)
    assert patterns["VS Code"].battery_drop == pytest.approx(10.0)


def test_application_switch_does_not_assign_cross_application_drop():
    start = datetime(2026, 1, 1, 10, 0)

    observations = [
        make_observation(start, 80, application="Chrome"),
        make_observation(
            start + timedelta(minutes=10),
            75,
            application="VS Code",
        ),
    ]

    result = ApplicationBatteryPatterns(
        FakeAccess(observations)
    ).calculate()

    assert result.patterns == ()


def test_charging_breaks_application_measurement_chain():
    start = datetime(2026, 1, 1, 10, 0)

    observations = [
        make_observation(start, 80, application="Chrome"),
        make_observation(
            start + timedelta(minutes=10),
            75,
            charging=True,
            application="Chrome",
        ),
        make_observation(
            start + timedelta(minutes=20),
            70,
            application="Chrome",
        ),
    ]

    result = ApplicationBatteryPatterns(
        FakeAccess(observations)
    ).calculate()

    assert result.patterns == ()


def test_missing_application_is_ignored():
    start = datetime(2026, 1, 1, 10, 0)

    observations = [
        make_observation(start, 80, application=None),
        make_observation(
            start + timedelta(minutes=30),
            70,
            application=None,
        ),
    ]

    result = ApplicationBatteryPatterns(
        FakeAccess(observations)
    ).calculate()

    assert result.patterns == ()


def test_missing_battery_breaks_measurement_chain():
    start = datetime(2026, 1, 1, 10, 0)

    observations = [
        make_observation(start, 80, application="Chrome"),
        make_observation(
            start + timedelta(minutes=10),
            None,
            application="Chrome",
        ),
        make_observation(
            start + timedelta(minutes=20),
            70,
            application="Chrome",
        ),
    ]

    result = ApplicationBatteryPatterns(
        FakeAccess(observations)
    ).calculate()

    assert result.patterns == ()


def test_result_is_immutable():
    result = ApplicationBatteryPatternResult(
        patterns=()
    )

    with pytest.raises(AttributeError):
        result.patterns = ()


def test_pattern_is_immutable():
    pattern = ApplicationBatteryPattern(
        application="Chrome",
        observation_count=2,
        battery_drop=5.0,
        average_drain_rate=10.0,
    )

    with pytest.raises(AttributeError):
        pattern.application = "VS Code"