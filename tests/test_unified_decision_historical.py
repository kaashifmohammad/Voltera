from orchestration.unified_decision import (
    UnifiedDecisionCoordinator,
    UnifiedDecisionResult,
)


def context_prediction():
    return {
        "combined_risk": "Medium",
        "signals": [
            "Context intelligence available",
        ],
    }


def learning_adaptive():
    return {
        "user_alignment": "Aligned",
        "adaptation_strength": "Medium",
        "signals": [
            "Learning intelligence available",
        ],
    }


def historical():
    return {
        "observation_count": 120,
        "average_battery": 54.5,
        "battery_trend": "DECLINING",
        "average_drain_rate": 8.2,
        "heavy_usage_session_count": 3,
    }


def test_historical_input_is_preserved():
    coordinator = UnifiedDecisionCoordinator()

    result = coordinator.coordinate(
        context_prediction(),
        learning_adaptive(),
        historical(),
    )

    assert isinstance(
        result,
        UnifiedDecisionResult,
    )

    assert result.historical["observation_count"] == 120
    assert result.historical["average_battery"] == 54.5


def test_historical_input_appears_in_serialization():
    coordinator = UnifiedDecisionCoordinator()

    result = coordinator.coordinate(
        context_prediction(),
        learning_adaptive(),
        historical(),
    )

    data = result.to_dict()

    assert data["historical"]["observation_count"] == 120
    assert data["historical"]["battery_trend"] == "DECLINING"


def test_historical_input_adds_supporting_signal():
    coordinator = UnifiedDecisionCoordinator()

    result = coordinator.coordinate(
        context_prediction(),
        learning_adaptive(),
        historical(),
    )

    assert any(
        signal == "Historical intelligence available"
        for signal in result.signals
    )


def test_missing_historical_input_is_backward_compatible():
    coordinator = UnifiedDecisionCoordinator()

    result = coordinator.coordinate(
        context_prediction(),
        learning_adaptive(),
    )

    assert result.historical == {}

    assert not any(
        signal == "Historical intelligence available"
        for signal in result.signals
    )


def test_historical_input_does_not_change_existing_decision_policy():
    coordinator = UnifiedDecisionCoordinator()

    without_history = coordinator.coordinate(
        context_prediction(),
        learning_adaptive(),
    )

    with_history = coordinator.coordinate(
        context_prediction(),
        learning_adaptive(),
        historical(),
    )

    assert (
        with_history.risk_level
        == without_history.risk_level
    )

    assert (
        with_history.priority
        == without_history.priority
    )

    assert (
        with_history.confidence
        == without_history.confidence
    )

    assert (
        with_history.user_relevance
        == without_history.user_relevance
    )

    assert (
        with_history.adaptation_strength
        == without_history.adaptation_strength
    )

    assert (
        with_history.decision
        == without_history.decision
    )


def test_invalid_historical_input_is_rejected():
    coordinator = UnifiedDecisionCoordinator()

    try:
        coordinator.coordinate(
            context_prediction(),
            learning_adaptive(),
            "invalid",
        )
        assert False
    except TypeError:
        assert True