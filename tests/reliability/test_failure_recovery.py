from orchestration.exceptions import (
    RecommendationError,
    UnifiedDecisionError,
)
from orchestration.intelligence_input import (
    IntelligenceInput,
)
from orchestration.orchestration_input import (
    OrchestrationInput,
)
from orchestration.orchestration_state import (
    OrchestrationState,
)
from orchestration.orchestrator import Orchestrator


class StableUnifiedDecision:
    def coordinate(
        self,
        context_prediction,
        learning_adaptive,
    ):
        class Result:
            def to_dict(self):
                return {
                    "decision": "Act",
                    "priority": "High",
                    "risk_level": "High",
                    "user_relevance": "High",
                    "adaptation_strength": "High",
                }

        return Result()


class StableRecommendation:
    def orchestrate(
        self,
        unified_result,
        battery_context=None,
    ):
        class Result:
            recommendation = (
                "Reduce battery consumption"
            )

            def to_dict(self):
                return {
                    "decision": "Act",
                    "priority": "High",
                    "recommendation": (
                        "Reduce battery consumption"
                    ),
                }

        return Result()


class StableNotification:
    def orchestrate(
        self,
        recommendation,
    ):
        class Result:
            def to_dict(self):
                return {
                    "recommendation": recommendation,
                    "signals": [
                        "Notification generated"
                    ],
                }

        return Result()


class FailingUnifiedDecision:
    def coordinate(
        self,
        context_prediction,
        learning_adaptive,
    ):
        raise RuntimeError(
            "temporary decision failure"
        )


class FailingRecommendation:
    def orchestrate(
        self,
        unified_result,
        battery_context=None,
    ):
        raise RuntimeError(
            "temporary recommendation failure"
        )


def build_input():
    return OrchestrationInput(
        intelligence=IntelligenceInput(
            context={
                "battery": 40,
                "battery_percent": 40,
            },
            learning={
                "user_alignment": "Aligned",
            },
            prediction={
                "risk_level": "High",
            },
            adaptive={
                "adaptation_strength": "High",
            },
        )
    )


def test_orchestrator_recovers_after_decision_failure():
    orchestrator = Orchestrator(
        unified_decision_coordinator=(
            FailingUnifiedDecision()
        ),
        recommendation_orchestrator=(
            StableRecommendation()
        ),
        notification_orchestrator=(
            StableNotification()
        ),
    )

    failed = orchestrator.orchestrate(
        build_input()
    )

    assert (
        failed.state
        == OrchestrationState.FAILED
    )

    orchestrator.unified_decision_coordinator = (
        StableUnifiedDecision()
    )

    recovered = orchestrator.orchestrate(
        build_input()
    )

    assert (
        recovered.state
        == OrchestrationState.COMPLETED
    )

    assert recovered.error is None


def test_orchestrator_recovers_after_recommendation_failure():
    orchestrator = Orchestrator(
        unified_decision_coordinator=(
            StableUnifiedDecision()
        ),
        recommendation_orchestrator=(
            FailingRecommendation()
        ),
        notification_orchestrator=(
            StableNotification()
        ),
    )

    failed = orchestrator.orchestrate(
        build_input()
    )

    assert (
        failed.state
        == OrchestrationState.FAILED
    )

    orchestrator.recommendation_orchestrator = (
        StableRecommendation()
    )

    recovered = orchestrator.orchestrate(
        build_input()
    )

    assert (
        recovered.state
        == OrchestrationState.COMPLETED
    )

    assert recovered.error is None


def test_reset_after_failure_returns_idle():
    orchestrator = Orchestrator(
        unified_decision_coordinator=(
            FailingUnifiedDecision()
        ),
        recommendation_orchestrator=(
            StableRecommendation()
        ),
        notification_orchestrator=(
            StableNotification()
        ),
    )

    result = orchestrator.orchestrate(
        build_input()
    )

    assert (
        result.state
        == OrchestrationState.FAILED
    )

    orchestrator.reset()

    assert (
        orchestrator.get_state()
        == OrchestrationState.IDLE
    )


def test_failed_cycle_does_not_return_partial_success():
    orchestrator = Orchestrator(
        unified_decision_coordinator=(
            StableUnifiedDecision()
        ),
        recommendation_orchestrator=(
            FailingRecommendation()
        ),
        notification_orchestrator=(
            StableNotification()
        ),
    )

    result = orchestrator.orchestrate(
        build_input()
    )

    assert (
        result.state
        == OrchestrationState.FAILED
    )

    assert result.decision is None
    assert result.recommendation is None
    assert result.notification is None
    assert result.error is not None


def test_repeated_failures_do_not_break_orchestrator():
    orchestrator = Orchestrator(
        unified_decision_coordinator=(
            FailingUnifiedDecision()
        ),
        recommendation_orchestrator=(
            StableRecommendation()
        ),
        notification_orchestrator=(
            StableNotification()
        ),
    )

    for _ in range(5):
        result = orchestrator.orchestrate(
            build_input()
        )

        assert (
            result.state
            == OrchestrationState.FAILED
        )

        assert result.error is not None

    assert (
        orchestrator.get_state()
        == OrchestrationState.FAILED
    )