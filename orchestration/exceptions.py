class VolteraError(Exception):
    """
    Base exception for VOLTERA orchestration failures.
    """

    def __init__(
        self,
        message: str,
        *,
        stage: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.stage = stage
        self.cause = cause

    def __str__(self) -> str:
        if self.stage:
            return f"[{self.stage}] {self.message}"

        return self.message


class OrchestrationError(VolteraError):
    """
    Base exception for orchestration-level failures.
    """


class InputValidationError(OrchestrationError):
    """
    Raised when orchestration input is invalid.
    """


class IntelligenceModuleError(OrchestrationError):
    """
    Raised when an intelligence module fails.
    """

    def __init__(
        self,
        message: str,
        *,
        module: str,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            stage=module,
            cause=cause,
        )

        self.module = module


class UnifiedDecisionError(IntelligenceModuleError):
    """
    Unified Decision failure.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            module="unified_decision",
            cause=cause,
        )


class RecommendationError(IntelligenceModuleError):
    """
    Recommendation failure.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            module="recommendation",
            cause=cause,
        )


class NotificationError(IntelligenceModuleError):
    """
    Notification failure.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            module="notification",
            cause=cause,
        )