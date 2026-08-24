from orchestration.exceptions import (
    InputValidationError,
    NotificationError,
    RecommendationError,
    UnifiedDecisionError,
    VolteraError,
)


def test_voltera_error_is_base_exception():
    error = VolteraError(
        "Test error"
    )

    assert isinstance(
        error,
        Exception,
    )

    assert error.message == "Test error"
    assert error.stage is None


def test_voltera_error_supports_stage():
    error = VolteraError(
        "Failure",
        stage="test_stage",
    )

    assert str(error) == "[test_stage] Failure"
    assert error.stage == "test_stage"


def test_input_validation_error():
    error = InputValidationError(
        "Invalid input",
        stage="input_validation",
    )

    assert isinstance(
        error,
        VolteraError,
    )

    assert error.stage == "input_validation"


def test_unified_decision_error():
    cause = RuntimeError(
        "Underlying failure"
    )

    error = UnifiedDecisionError(
        "Decision failed",
        cause=cause,
    )

    assert isinstance(
        error,
        VolteraError,
    )

    assert error.module == "unified_decision"
    assert error.cause is cause
    assert error.stage == "unified_decision"


def test_recommendation_error():
    error = RecommendationError(
        "Recommendation failed"
    )

    assert isinstance(
        error,
        VolteraError,
    )

    assert error.module == "recommendation"


def test_notification_error():
    error = NotificationError(
        "Notification failed"
    )

    assert isinstance(
        error,
        VolteraError,
    )

    assert error.module == "notification"


def test_module_errors_are_distinguishable():
    decision_error = UnifiedDecisionError(
        "Decision failed"
    )

    recommendation_error = RecommendationError(
        "Recommendation failed"
    )

    notification_error = NotificationError(
        "Notification failed"
    )

    assert (
        decision_error.module
        != recommendation_error.module
    )

    assert (
        recommendation_error.module
        != notification_error.module
    )