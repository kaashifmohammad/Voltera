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


class FakeDecisionResult:
    def to_dict(self):
        return {
            "decision": "Act",
            "priority": "High",
            "risk_level": "High",
            "user_relevance": "High",
            "adaptation_strength": "High",
        }


class FakeRecommendationResult:
    recommendation = "Reduce battery consumption"

    def to_dict(self):
        return {
            "decision": "Act",
            "priority": "High",
            "recommendation": (
                "Reduce battery consumption"
            ),
        }


class FakeNotificationResult:
    def to_dict(self):
        return {
            "recommendation": (
                "Reduce battery consumption"
            ),
            "signals": [
                "Notification generated"
            ],
        }


class StableDecision:
    def coordinate(
        self,
        context_prediction,
        learning_adaptive,
    ):
        return FakeDecisionResult()


class StableRecommendation:
    def orchestrate(
        self,
        unified_result,
        battery_context=None,
    ):
        return FakeRecommendationResult()


class StableNotification:
    def orchestrate(
        self,
        recommendation,
    ):
        return FakeNotificationResult()


class BrokenDecision:
    def coordinate(
        self,
        context_prediction,
        learning_adaptive,
    ):
        raise ValueError(
            "decision dependency unavailable"
        )


class BrokenRecommendation:
    def orchestrate(
        self,
        unified_result,
        battery_context=None,
    ):
        raise ValueError(
            "recommendation dependency unavailable"
        )


class BrokenNotification:
    def orchestrate(
        self,
        recommendation,
    ):
        raise ValueError(
            "notification dependency unavailable"
        )


def build_input():
    return OrchestrationInput(
        intelligence=IntelligenceInput(
            context={
                "battery": 50,
                "battery_percent": 50,
            },
            learning={
                "user_alignment": "Aligned",
            },
            prediction={
                "risk_level": "Medium",
            },
            adaptive={
                "adaptation_strength": "Medium",
            },
        )
    )


def test_decision_failure_stops_downstream_modules():
    recommendation = StableRecommendation()
    notification = StableNotification()

    orchestrator = Orchestrator(
        unified_decision_coordinator=(
            BrokenDecision()
        ),
        recommendation_orchestrator=recommendation,
        notification_orchestrator=notification,
    )

    result = orchestrator.orchestrate(
        build_input()
    )

    assert (
        result.state
        == OrchestrationState.FAILED
    )

    assert result.error is not None


def test_recommendation_failure_prevents_notification():
    notification = StableNotification()

    orchestrator = Orchestrator(
        unified_decision_coordinator=(
            StableDecision()
        ),
        recommendation_orchestrator=(
            BrokenRecommendation()
        ),
        notification_orchestrator=notification,
    )

    result = orchestrator.orchestrate(
        build_input()
    )

    assert (
        result.state
        == OrchestrationState.FAILED
    )

    assert result.error is not None


def test_notification_failure_does_not_corrupt_state():
    orchestrator = Orchestrator(
        unified_decision_coordinator=(
            StableDecision()
        ),
        recommendation_orchestrator=(
            StableRecommendation()
        ),
        notification_orchestrator=(
            BrokenNotification()
        ),
    )

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


def test_successful_modules_continue_to_work():
    orchestrator = Orchestrator(
        unified_decision_coordinator=(
            StableDecision()
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
        == OrchestrationState.COMPLETED
    )

    assert result.error is None
    assert result.decision is not None
    assert result.recommendation is not None
    assert result.notification is not None