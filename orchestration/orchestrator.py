from typing import Any, Dict

from .orchestration_input import OrchestrationInput
from .orchestration_result import OrchestrationResult
from .orchestration_state import OrchestrationState

from .exceptions import (
    InputValidationError,
    NotificationError,
    RecommendationError,
    UnifiedDecisionError,
)

from .unified_decision import UnifiedDecisionCoordinator
from .recommendation.recommendation_orchestrator import (
    RecommendationOrchestrator,
)
from .notification.notification_orchestrator import (
    NotificationOrchestrator,
)


class Orchestrator:
    """
    Central coordinator for VOLTERA intelligence.

    Pipeline:

        OrchestrationInput
                ↓
        Unified Decision
                ↓
        Recommendation
                ↓
        Notification
                ↓
        OrchestrationResult

    The orchestrator coordinates existing intelligence layers
    and provides a controlled failure boundary.
    """

    def __init__(
        self,
        unified_decision_coordinator=None,
        recommendation_orchestrator=None,
        notification_orchestrator=None,
    ) -> None:
        self.state = OrchestrationState.IDLE

        self.unified_decision_coordinator = (
            unified_decision_coordinator
            if unified_decision_coordinator is not None
            else UnifiedDecisionCoordinator()
        )

        self.recommendation_orchestrator = (
            recommendation_orchestrator
            if recommendation_orchestrator is not None
            else RecommendationOrchestrator()
        )

        self.notification_orchestrator = (
            notification_orchestrator
            if notification_orchestrator is not None
            else NotificationOrchestrator()
        )

    def orchestrate(
        self,
        orchestration_input: OrchestrationInput,
    ) -> OrchestrationResult:
        """
        Execute one complete VOLTERA orchestration cycle.

        Every cycle has a controlled failure boundary.

        Invalid input or module failures are converted into
        structured OrchestrationResult objects rather than
        escaping to the caller.
        """

        self.state = OrchestrationState.RUNNING

        try:
            self._validate_input(
                orchestration_input
            )

            intelligence = orchestration_input.intelligence

            context = dict(
                intelligence.context
            )

            learning = dict(
                intelligence.learning
            )

            prediction = dict(
                intelligence.prediction
            )

            adaptive = dict(
                intelligence.adaptive
            )

            context_prediction = (
                self._build_context_prediction(
                    context,
                    prediction,
                )
            )

            learning_adaptive = (
                self._build_learning_adaptive(
                    learning,
                    adaptive,
                )
            )

            unified_result = (
                self._run_unified_decision(
                    context_prediction,
                    learning_adaptive,
                )
            )

            decision_data = unified_result.to_dict()

            battery_context = (
                self._build_battery_context(
                    context,
                    prediction,
                )
            )

            recommendation_result = (
                self._run_recommendation(
                    unified_result,
                    battery_context,
                )
            )

            recommendation_data = (
                recommendation_result.to_dict()
            )

            notification_result = (
                self._run_notification(
                    recommendation_result.recommendation
                )
            )

            notification_data = (
                notification_result.to_dict()
            )

            self.state = OrchestrationState.COMPLETED

            return OrchestrationResult(
                state=self.state,
                decision=decision_data,
                recommendation=recommendation_data,
                notification=notification_data,
                error=None,
            )

        except Exception as exc:
            self.state = OrchestrationState.FAILED

            return OrchestrationResult(
                state=self.state,
                decision=None,
                recommendation=None,
                notification=None,
                error=str(exc),
            )

    @staticmethod
    def _validate_input(
        orchestration_input: OrchestrationInput,
    ) -> None:
        if not isinstance(
            orchestration_input,
            OrchestrationInput,
        ):
            raise InputValidationError(
                "orchestration_input must be an "
                "OrchestrationInput instance.",
                stage="input_validation",
            )

        if orchestration_input.intelligence is None:
            raise InputValidationError(
                "intelligence input cannot be None.",
                stage="input_validation",
            )

    def _run_unified_decision(
        self,
        context_prediction: Dict[str, Any],
        learning_adaptive: Dict[str, Any],
    ):
        try:
            return (
                self.unified_decision_coordinator.coordinate(
                    context_prediction,
                    learning_adaptive,
                )
            )

        except Exception as exc:
            if isinstance(
                exc,
                UnifiedDecisionError,
            ):
                raise

            message = str(exc).strip() or (
                "Unified decision failure"
            )
            raise UnifiedDecisionError(
                message,
                cause=exc,
            ) from exc

    def _run_recommendation(
        self,
        unified_result,
        battery_context: Dict[str, Any],
    ):
        try:
            return (
                self.recommendation_orchestrator.orchestrate(
                    unified_result,
                    battery_context=battery_context,
                )
            )

        except Exception as exc:
            if isinstance(
                exc,
                RecommendationError,
            ):
                raise

            message = str(exc).strip() or (
                "Recommendation failure"
            )
            raise RecommendationError(
                message,
                cause=exc,
            ) from exc

    def _run_notification(
        self,
        recommendation,
    ):
        try:
            return (
                self.notification_orchestrator.orchestrate(
                    recommendation
                )
            )

        except Exception as exc:
            if isinstance(
                exc,
                NotificationError,
            ):
                raise

            message = str(exc).strip() or (
                "Notification failure"
            )
            raise NotificationError(
                message,
                cause=exc,
            ) from exc

    @staticmethod
    def _build_context_prediction(
        context: Dict[str, Any],
        prediction: Dict[str, Any],
    ) -> Dict[str, Any]:
        data: Dict[str, Any] = {}

        data.update(context)
        data.update(prediction)

        if "combined_risk" not in data:
            risk = prediction.get(
                "risk_level"
            )

            if risk is None:
                risk = context.get(
                    "risk_level"
                )

            if risk is not None:
                data["combined_risk"] = risk

        if "user_relevance" not in data:
            relevance = context.get(
                "relevance"
            )

            if relevance is not None:
                data["user_relevance"] = relevance

        signals = []

        context_signals = context.get(
            "signals"
        )

        if isinstance(
            context_signals,
            list,
        ):
            signals.extend(
                str(signal)
                for signal in context_signals
            )

        prediction_signals = prediction.get(
            "signals"
        )

        if isinstance(
            prediction_signals,
            list,
        ):
            signals.extend(
                str(signal)
                for signal in prediction_signals
            )

        if signals:
            data["signals"] = signals

        return data

    @staticmethod
    def _build_learning_adaptive(
        learning: Dict[str, Any],
        adaptive: Dict[str, Any],
    ) -> Dict[str, Any]:
        data: Dict[str, Any] = {}

        data.update(learning)
        data.update(adaptive)

        if "adaptation_strength" not in data:
            strength = adaptive.get(
                "adaptive_strength"
            )

            if strength is None:
                strength = learning.get(
                    "adaptation_strength"
                )

            if strength is not None:
                data["adaptation_strength"] = strength

        if "user_alignment" not in data:
            alignment = learning.get(
                "user_alignment"
            )

            if alignment is None:
                alignment = adaptive.get(
                    "user_alignment"
                )

            if alignment is not None:
                data["user_alignment"] = alignment

        signals = []

        learning_signals = learning.get(
            "signals"
        )

        if isinstance(
            learning_signals,
            list,
        ):
            signals.extend(
                str(signal)
                for signal in learning_signals
            )

        adaptive_signals = adaptive.get(
            "signals"
        )

        if isinstance(
            adaptive_signals,
            list,
        ):
            signals.extend(
                str(signal)
                for signal in adaptive_signals
            )

        if signals:
            data["signals"] = signals

        return data

    @staticmethod
    def _build_battery_context(
        context: Dict[str, Any],
        prediction: Dict[str, Any],
    ) -> Dict[str, Any]:
        battery_context: Dict[str, Any] = {}

        battery_context.update(context)

        battery_percentage = context.get(
            "battery_percentage"
        )

        if battery_percentage is None:
            battery_percentage = context.get(
                "battery_percent"
            )

        if battery_percentage is None:
            battery_percentage = context.get(
                "battery"
            )

        if battery_percentage is not None:
            battery_context[
                "battery_percentage"
            ] = battery_percentage

        if "charging" not in battery_context:
            battery_context["charging"] = bool(
                context.get(
                    "charging_status",
                    context.get(
                        "is_charging",
                        False,
                    ),
                )
            )

        for key in (
            "cpu_usage",
            "ram_usage",
        ):
            if key not in battery_context:
                battery_context[key] = 0

        if "predicted_battery" not in battery_context:
            predicted_battery = prediction.get(
                "predicted_battery",
                prediction.get(
                    "predicted_battery_percentage",
                    battery_context.get(
                        "battery_percentage"
                    ),
                ),
            )

            battery_context[
                "predicted_battery"
            ] = predicted_battery

        if "prediction_horizon_minutes" not in battery_context:
            battery_context[
                "prediction_horizon_minutes"
            ] = prediction.get(
                "prediction_horizon_minutes",
                0,
            )

        if "expected_change" not in battery_context:
            battery_context[
                "expected_change"
            ] = prediction.get(
                "expected_change",
                prediction.get(
                    "battery_delta",
                    0,
                ),
            )

        for key in (
            "risk_level",
            "predicted_battery",
            "predicted_battery_percentage",
            "battery_delta",
        ):
            if (
                key in prediction
                and key not in battery_context
            ):
                battery_context[key] = (
                    prediction[key]
                )

        return battery_context

    def reset(self) -> None:
        """
        Reset the orchestrator to its initial state.
        """
        self.state = OrchestrationState.IDLE

    def get_state(self) -> OrchestrationState:
        """
        Return the current orchestration state.
        """
        return self.state