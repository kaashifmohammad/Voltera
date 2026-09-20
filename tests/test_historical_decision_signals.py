from orchestration.unified_decision import UnifiedDecisionCoordinator


def create_coordinator():
    return UnifiedDecisionCoordinator()


def test_declining_historical_trend_creates_signal():
    coordinator = create_coordinator()

    signals = coordinator._build_historical_signals(
        {
            "observation_count": 20,
            "battery_trend": "DECLINING",
        }
    )

    assert "Historical observations available: 20" in signals
    assert "Historical battery trend is declining" in signals


def test_rising_historical_trend_creates_signal():
    coordinator = create_coordinator()

    signals = coordinator._build_historical_signals(
        {
            "battery_trend": "RISING",
        }
    )

    assert "Historical battery trend is rising" in signals


def test_stable_historical_trend_creates_signal():
    coordinator = create_coordinator()

    signals = coordinator._build_historical_signals(
        {
            "battery_trend": "STABLE",
        }
    )

    assert "Historical battery trend is stable" in signals


def test_average_battery_and_drain_rate_create_signals():
    coordinator = create_coordinator()

    signals = coordinator._build_historical_signals(
        {
            "average_battery": 37.456,
            "average_drain_rate": 12.3456,
        }
    )

    assert "Historical average battery: 37.5%" in signals
    assert "Historical average drain rate: 12.35%/hour" in signals


def test_heavy_usage_creates_signal():
    coordinator = create_coordinator()

    signals = coordinator._build_historical_signals(
        {
            "heavy_usage_session_count": 3,
        }
    )

    assert "Historical heavy usage detected: 3 session(s)" in signals


def test_no_heavy_usage_creates_signal():
    coordinator = create_coordinator()

    signals = coordinator._build_historical_signals(
        {
            "heavy_usage_session_count": 0,
        }
    )

    assert "No historical heavy usage sessions detected" in signals


def test_strongest_usage_period_creates_signal():
    coordinator = create_coordinator()

    signals = coordinator._build_historical_signals(
        {
            "strongest_usage_period": "EVENING",
        }
    )

    assert (
        "Historical strongest usage period: Evening"
        in signals
    )


def test_application_patterns_create_signal():
    coordinator = create_coordinator()

    signals = coordinator._build_historical_signals(
        {
            "application_patterns": [
                {"application": "Chrome"},
                {"application": "VS Code"},
            ],
        }
    )

    assert (
        "Historical application battery patterns: 2"
        in signals
    )


def test_empty_historical_data_creates_no_signals():
    coordinator = create_coordinator()

    signals = coordinator._build_historical_signals({})

    assert signals == []


def test_historical_signals_do_not_change_decision_policy():
    coordinator = create_coordinator()

    context_prediction = {
        "combined_risk": "Low",
    }

    learning_adaptive = {
        "adaptation_strength": "Low",
    }

    without_history = coordinator.coordinate(
        context_prediction,
        learning_adaptive,
    )

    with_history = coordinator.coordinate(
        context_prediction,
        learning_adaptive,
        {
            "battery_trend": "DECLINING",
            "average_battery": 20,
            "average_drain_rate": 15,
            "heavy_usage_session_count": 4,
        },
    )

    assert (
        with_history.decision
        == without_history.decision
    )

    assert (
        with_history.priority
        == without_history.priority
    )

    assert (
        with_history.risk_level
        == without_history.risk_level
    )

    assert (
        "Historical battery trend is declining"
        in with_history.signals
    )