from __future__ import annotations

from typing import Any


class StressValidator:
    """
    Validates stress simulation results for stability and
    consistency.
    """

    def validate_completion(
        self,
        result: Any,
    ) -> bool:
        return (
            result is not None
            and hasattr(result, "total_cycles")
            and hasattr(result, "successful_cycles")
            and hasattr(result, "failed_cycles")
            and result.total_cycles
            == (
                result.successful_cycles
                + result.failed_cycles
            )
        )

    def validate_no_unexpected_failures(
        self,
        result: Any,
    ) -> bool:
        return (
            self.validate_completion(result)
            and result.failed_cycles == 0
        )

    def validate_success_rate(
        self,
        result: Any,
        minimum: float = 1.0,
    ) -> bool:
        if not 0 <= minimum <= 1:
            raise ValueError(
                "minimum must be between 0 and 1."
            )

        if not self.validate_completion(result):
            return False

        return result.success_rate >= minimum

    def validate_result_count(
        self,
        result: Any,
    ) -> bool:
        if not self.validate_completion(result):
            return False

        return len(result.results) == result.total_cycles

    def validate(
        self,
        result: Any,
        *,
        minimum_success_rate: float = 1.0,
    ) -> dict[str, bool]:
        return {
            "completion": self.validate_completion(
                result
            ),
            "result_count": self.validate_result_count(
                result
            ),
            "success_rate": self.validate_success_rate(
                result,
                minimum_success_rate,
            ),
        }