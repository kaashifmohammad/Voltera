from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class UnifiedDecisionResult:
    """
    Final intelligence decision produced by combining:

    - Context + Prediction Intelligence
    - Learning + Adaptive Intelligence
    - Historical Intelligence

    Historical intelligence is preserved as supporting evidence.
    It does not independently change risk, priority, or decision
    policy at this stage.
    """

    context_prediction: Dict[str, Any]
    learning_adaptive: Dict[str, Any]
    historical: Dict[str, Any] = field(default_factory=dict)

    risk_level: str = "Unknown"
    priority: str = "Unknown"
    confidence: str = "Unknown"
    user_relevance: str = "Unknown"
    adaptation_strength: str = "Unknown"

    decision: str = "Monitor"

    signals: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the unified decision into a serializable dictionary.
        """

        return {
            "context_prediction": dict(self.context_prediction),
            "learning_adaptive": dict(self.learning_adaptive),
            "historical": dict(self.historical),
            "risk_level": self.risk_level,
            "priority": self.priority,
            "confidence": self.confidence,
            "user_relevance": self.user_relevance,
            "adaptation_strength": self.adaptation_strength,
            "decision": self.decision,
            "signals": list(self.signals),
        }


class UnifiedDecisionCoordinator:
    """
    Coordinates the outputs of the Context/Prediction Intelligence,
    Learning/Adaptive Intelligence, and Historical Intelligence
    components into one final intelligence decision.

    Responsibilities:

    - Combine context/prediction risk
    - Incorporate learning/adaptive intelligence
    - Preserve historical intelligence
    - Evaluate user relevance
    - Evaluate adaptive strength
    - Determine confidence
    - Determine final priority
    - Produce one unified decision
    - Preserve supporting signals

    Historical intelligence is supporting evidence only at this
    integration stage. Decision-policy changes are handled by
    later historical decision-signal phases.

    This component does not generate recommendations or notifications.
    """

    RISK_LEVELS = (
        "Low",
        "Medium",
        "High",
        "Critical",
        "Unknown",
    )

    PRIORITY_LEVELS = (
        "Low",
        "Medium",
        "High",
        "Critical",
        "Unknown",
    )

    CONFIDENCE_LEVELS = (
        "Low",
        "Medium",
        "High",
        "Unknown",
    )

    RELEVANCE_LEVELS = (
        "Low",
        "Medium",
        "High",
        "Unknown",
    )

    ADAPTATION_LEVELS = (
        "Low",
        "Medium",
        "High",
        "Very High",
        "Active",
        "Unknown",
    )

    def coordinate(
        self,
        context_prediction: Any,
        learning_adaptive: Any,
        historical: Any = None,
    ) -> UnifiedDecisionResult:
        """
        Combine Context/Prediction, Learning/Adaptive, and
        Historical Intelligence.

        Context/Prediction and Learning/Adaptive inputs remain
        required for backward compatibility.

        Historical intelligence is optional and is preserved
        as supporting evidence.
        """

        context_prediction_data = self._normalize_input(
            context_prediction,
            "context_prediction",
        )

        learning_adaptive_data = self._normalize_input(
            learning_adaptive,
            "learning_adaptive",
        )

        historical_data = self._normalize_optional_input(
            historical,
            "historical",
        )

        risk_level = self._determine_risk(
            context_prediction_data,
        )

        adaptation_strength = self._determine_adaptation_strength(
            learning_adaptive_data,
        )

        user_relevance = self._determine_user_relevance(
            context_prediction_data,
            learning_adaptive_data,
        )

        confidence = self._determine_confidence(
            context_prediction_data,
            learning_adaptive_data,
            risk_level,
            adaptation_strength,
        )

        explicit_high_relevance = self._has_explicit_high_relevance(
            context_prediction_data,
        )

        priority = self._determine_priority(
            risk_level,
            user_relevance,
            adaptation_strength,
            confidence,
            explicit_high_relevance,
        )

        decision = self._determine_decision(
            priority,
            risk_level,
            user_relevance,
        )

        signals = self._build_signals(
            context_prediction_data,
            learning_adaptive_data,
            historical_data,
            risk_level,
            priority,
            confidence,
            user_relevance,
            adaptation_strength,
            decision,
        )

        return UnifiedDecisionResult(
            context_prediction=context_prediction_data,
            learning_adaptive=learning_adaptive_data,
            historical=historical_data,
            risk_level=risk_level,
            priority=priority,
            confidence=confidence,
            user_relevance=user_relevance,
            adaptation_strength=adaptation_strength,
            decision=decision,
            signals=signals,
        )

    def _normalize_input(
        self,
        value: Any,
        name: str,
    ) -> Dict[str, Any]:
        """
        Normalize required orchestration outputs into dictionaries.
        """

        if value is None:
            raise ValueError(
                f"{name} cannot be None."
            )

        if isinstance(value, dict):
            return dict(value)

        if hasattr(value, "to_dict"):
            normalized = value.to_dict()

            if not isinstance(normalized, dict):
                raise TypeError(
                    f"{name}.to_dict() must return a dictionary."
                )

            return dict(normalized)

        raise TypeError(
            f"{name} must be a dictionary or provide to_dict()."
        )

    def _normalize_optional_input(
        self,
        value: Any,
        name: str,
    ) -> Dict[str, Any]:
        """
        Normalize optional orchestration inputs.

        None represents an absent historical intelligence payload
        and therefore becomes an empty dictionary.
        """

        if value is None:
            return {}

        return self._normalize_input(
            value,
            name,
        )

    def _determine_risk(
        self,
        context_prediction: Dict[str, Any],
    ) -> str:
        """
        Use the already-combined Context + Prediction risk.

        This preserves the risk calculation performed by the
        upstream intelligence layer rather than duplicating it.
        """

        risk = context_prediction.get(
            "combined_risk"
        )

        if isinstance(risk, str):
            normalized = self._normalize_level(
                risk
            )

            if normalized in self.RISK_LEVELS:
                return normalized

        return "Unknown"

    def _determine_adaptation_strength(
        self,
        learning_adaptive: Dict[str, Any],
    ) -> str:
        """
        Extract adaptation strength produced by the learning/adaptive
        intelligence layer.
        """

        strength = learning_adaptive.get(
            "adaptation_strength"
        )

        if isinstance(strength, str):
            normalized = self._normalize_adaptation(
                strength
            )

            if normalized in self.ADAPTATION_LEVELS:
                return normalized

        return "Unknown"

    def _determine_user_relevance(
        self,
        context_prediction: Dict[str, Any],
        learning_adaptive: Dict[str, Any],
    ) -> str:
        """
        Determine user relevance from explicit context relevance
        and learning alignment.

        Learning alignment can increase relevance, but derived
        relevance alone must not automatically make a High-risk
        situation Critical.
        """

        relevance = self._extract_nested_value(
            context_prediction,
            "user_relevance",
        )

        if relevance is None:
            relevance = self._extract_nested_value(
                context_prediction,
                "relevance",
            )

        if relevance is not None:
            normalized = self._normalize_level(
                relevance
            )

            if normalized in self.RELEVANCE_LEVELS:
                return normalized

        learning_relevance = self._extract_nested_value(
            learning_adaptive,
            "user_relevance",
        )

        if learning_relevance is None:
            learning_relevance = self._extract_nested_value(
                learning_adaptive,
                "relevance",
            )

        if learning_relevance is not None:
            normalized = self._normalize_level(
                learning_relevance
            )

            if normalized in self.RELEVANCE_LEVELS:
                return normalized

        alignment = str(
            learning_adaptive.get(
                "user_alignment",
                "Unknown",
            )
        ).strip().lower()

        strength = str(
            learning_adaptive.get(
                "adaptation_strength",
                "Unknown",
            )
        ).strip().lower()

        if alignment == "aligned":
            if strength in {
                "high",
                "very high",
            }:
                return "High"

            return "Medium"

        if alignment == "misaligned":
            return "Low"

        if alignment == "inferred":
            return "Medium"

        return "Unknown"

    def _determine_confidence(
        self,
        context_prediction: Dict[str, Any],
        learning_adaptive: Dict[str, Any],
        risk_level: str,
        adaptation_strength: str,
    ) -> str:
        """
        Determine confidence from the availability and agreement
        of the underlying intelligence signals.
        """

        context_prediction_available = bool(
            context_prediction
        )

        learning_adaptive_available = bool(
            learning_adaptive
        )

        if not (
            context_prediction_available
            or learning_adaptive_available
        ):
            return "Unknown"

        explicit_confidence = (
            context_prediction.get("confidence")
        )

        if explicit_confidence is None:
            explicit_confidence = (
                learning_adaptive.get("confidence")
            )

        if explicit_confidence is not None:
            normalized = self._normalize_level(
                explicit_confidence
            )

            if normalized in self.CONFIDENCE_LEVELS:
                return normalized

        if (
            risk_level != "Unknown"
            and adaptation_strength
            in {"High", "Very High"}
        ):
            return "High"

        if (
            risk_level != "Unknown"
            and learning_adaptive_available
        ):
            return "Medium"

        if context_prediction_available:
            return "Medium"

        return "Low"

    def _determine_priority(
        self,
        risk_level: str,
        user_relevance: str,
        adaptation_strength: str,
        confidence: str,
        explicit_high_relevance: bool,
    ) -> str:
        """
        Determine final decision priority.

        Critical priority requires explicit High user relevance
        for a High-risk situation.
        """

        if risk_level == "Critical":
            return "Critical"

        if risk_level == "High":
            if (
                explicit_high_relevance
                and user_relevance == "High"
                and adaptation_strength in {
                    "High",
                    "Very High",
                }
                and confidence == "High"
            ):
                return "Critical"

            return "High"

        if risk_level == "Medium":
            if (
                user_relevance == "High"
                and adaptation_strength in {
                    "High",
                    "Very High",
                }
            ):
                return "High"

            return "Medium"

        if risk_level == "Low":
            if (
                user_relevance == "High"
                and adaptation_strength == "Very High"
                and confidence == "High"
            ):
                return "Medium"

            return "Low"

        return "Unknown"

    def _determine_decision(
        self,
        priority: str,
        risk_level: str,
        user_relevance: str,
    ) -> str:
        """
        Produce the single final intelligence decision.

        Recommendation generation happens in the next orchestration
        layer.
        """

        if priority == "Critical":
            return "Act Immediately"

        if priority == "High":
            return "Act"

        if priority == "Medium":
            return "Consider Action"

        if (
            priority == "Low"
            and user_relevance == "Low"
        ):
            return "Monitor"

        if risk_level == "Low":
            return "Monitor"

        return "Monitor"

    def _build_signals(
        self,
        context_prediction: Dict[str, Any],
        learning_adaptive: Dict[str, Any],
        historical: Dict[str, Any],
        risk_level: str,
        priority: str,
        confidence: str,
        user_relevance: str,
        adaptation_strength: str,
        decision: str,
    ) -> list[str]:
        """
        Build an auditable list of signals supporting the decision.

        Historical intelligence contributes descriptive decision
        signals only. It does not directly modify risk, priority,
        confidence, or the final decision at this stage.
        """

        signals: list[str] = []

        prediction_signals = context_prediction.get(
            "signals"
        )

        if isinstance(prediction_signals, list):
            signals.extend(
                str(signal)
                for signal in prediction_signals
            )

        learning_signals = learning_adaptive.get(
            "signals"
        )

        if isinstance(learning_signals, list):
            signals.extend(
                str(signal)
                for signal in learning_signals
            )

        historical_signals = self._build_historical_signals(
            historical
        )

        signals.extend(historical_signals)

        signals.append(
            f"Unified risk: {risk_level}"
        )

        signals.append(
            f"User relevance: {user_relevance}"
        )

        signals.append(
            f"Adaptation strength: {adaptation_strength}"
        )

        signals.append(
            f"Decision confidence: {confidence}"
        )

        signals.append(
            f"Final priority: {priority}"
        )

        signals.append(
            f"Unified decision: {decision}"
        )

        return signals

    @staticmethod
    def _build_historical_signals(
        historical: Dict[str, Any],
    ) -> list[str]:
        """
        Convert historical intelligence into descriptive,
        auditable decision signals.

        These signals provide historical evidence without
        changing the existing decision policy.
        """

        if not historical:
            return []

        signals: list[str] = [
            "Historical intelligence available"
        ]

        observation_count = historical.get(
            "observation_count"
        )

        if observation_count is not None:
            signals.append(
                f"Historical observations available: "
                f"{observation_count}"
            )

        average_battery = historical.get(
            "average_battery"
        )

        if average_battery is not None:
            signals.append(
                f"Historical average battery: "
                f"{float(average_battery):.1f}%"
            )

        battery_trend = historical.get(
            "battery_trend"
        )

        if battery_trend:
            trend = str(
                battery_trend
            ).strip()

            if "." in trend:
                trend = trend.rsplit(
                    ".",
                    1,
                )[-1]

            trend = trend.replace(
                "_",
                " ",
            ).lower()

            if trend == "declining":
                signals.append(
                    "Historical battery trend is declining"
                )
            elif trend == "rising":
                signals.append(
                    "Historical battery trend is rising"
                )
            elif trend == "stable":
                signals.append(
                    "Historical battery trend is stable"
                )
            elif trend == "insufficient data":
                signals.append(
                    "Historical battery trend has insufficient data"
                )

        average_drain_rate = historical.get(
            "average_drain_rate"
        )

        if average_drain_rate is not None:
            signals.append(
                f"Historical average drain rate: "
                f"{float(average_drain_rate):.2f}%/hour"
            )

        heavy_usage_count = historical.get(
            "heavy_usage_session_count"
        )

        if heavy_usage_count is not None:
            try:
                heavy_usage_count = int(
                    heavy_usage_count
                )
            except (TypeError, ValueError):
                heavy_usage_count = None

            if heavy_usage_count is not None:
                if heavy_usage_count > 0:
                    signals.append(
                        f"Historical heavy usage detected: "
                        f"{heavy_usage_count} session(s)"
                    )
                else:
                    signals.append(
                        "No historical heavy usage sessions detected"
                    )

        strongest_period = historical.get(
            "strongest_usage_period"
        )

        if strongest_period:
            period = str(
                strongest_period
            ).strip()

            if "." in period:
                period = period.rsplit(
                    ".",
                    1,
                )[-1]

            period = period.replace(
                "_",
                " ",
            ).title()

            signals.append(
                f"Historical strongest usage period: "
                f"{period}"
            )

        application_patterns = historical.get(
            "application_patterns"
        )

        if application_patterns:
            try:
                pattern_count = len(
                    application_patterns
                )
            except TypeError:
                pattern_count = 0

            if pattern_count:
                signals.append(
                    f"Historical application battery patterns: "
                    f"{pattern_count}"
                )

        return signals

    @staticmethod
    def _normalize_level(
        value: Any,
    ) -> str:
        """
        Normalize standard intelligence levels.
        """

        if not isinstance(value, str):
            return "Unknown"

        value = value.strip().lower()

        mapping = {
            "low": "Low",
            "medium": "Medium",
            "high": "High",
            "critical": "Critical",
            "unknown": "Unknown",
        }

        return mapping.get(
            value,
            "Unknown",
        )

    @staticmethod
    def _normalize_adaptation(
        value: Any,
    ) -> str:
        """
        Normalize adaptive strength values.
        """

        if not isinstance(value, str):
            return "Unknown"

        value = value.strip().lower()

        mapping = {
            "low": "Low",
            "medium": "Medium",
            "high": "High",
            "very high": "Very High",
            "active": "Active",
            "unknown": "Unknown",
        }

        return mapping.get(
            value,
            "Unknown",
        )

    @staticmethod
    def _extract_nested_value(
        data: Dict[str, Any],
        key: str,
    ) -> Optional[Any]:
        """
        Extract a value from the top level or the nested
        decision structure.
        """

        if key in data:
            return data[key]

        decision = data.get(
            "decision"
        )

        if isinstance(decision, dict):
            return decision.get(key)

        return None

    @staticmethod
    def _has_explicit_high_relevance(
        context_prediction: Dict[str, Any],
    ) -> bool:
        """
        Check whether High user relevance was explicitly supplied
        by the Context/Prediction intelligence layer.
        """

        relevance = context_prediction.get(
            "user_relevance"
        )

        if relevance is None:
            relevance = context_prediction.get(
                "relevance"
            )

        if relevance is None:
            decision = context_prediction.get(
                "decision"
            )

            if isinstance(decision, dict):
                relevance = decision.get(
                    "user_relevance"
                )

                if relevance is None:
                    relevance = decision.get(
                        "relevance"
                    )

        return (
            isinstance(relevance, str)
            and relevance.strip().lower() == "high"
        )
    