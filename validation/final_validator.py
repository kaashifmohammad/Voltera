from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import Any

from .validation_report import ValidationReport


ValidationGate = Callable[[], Any]


class FinalValidator:
    """
    Coordinates the final VOLTERA validation gates.

    Gates are injected so the validator remains independent of the
    individual VOLTERA subsystems and can be tested deterministically.
    """

    REQUIRED_STAGES = (
        "build_validation",
        "reliability_tests",
        "stress_tests",
        "regression_tests",
        "state_integrity",
        "persistence_integrity",
        "performance_stability",
    )

    def __init__(
        self,
        gates: Mapping[str, ValidationGate] | None = None,
        performance_limit_seconds: float = 10.0,
    ) -> None:
        self.gates = dict(gates or {})
        self.performance_limit_seconds = float(performance_limit_seconds)

    def validate(self) -> ValidationReport:
        report = ValidationReport()

        for stage_name in self.REQUIRED_STAGES:
            self._run_stage(report, stage_name)

        report.complete()
        return report

    def _run_stage(
        self,
        report: ValidationReport,
        stage_name: str,
    ) -> None:
        gate = self.gates.get(stage_name)

        if gate is None:
            report.add_stage(
                stage_name,
                False,
                "Required validation gate was not supplied.",
            )
            return

        started = time.perf_counter()

        try:
            result = gate()
            elapsed = time.perf_counter() - started

            passed, details, metrics = self._interpret_result(result)

            if (
                stage_name == "performance_stability"
                and elapsed > self.performance_limit_seconds
            ):
                passed = False
                details = (
                    f"Gate exceeded performance limit: "
                    f"{elapsed:.4f}s > "
                    f"{self.performance_limit_seconds:.4f}s."
                )

            metrics.setdefault("duration_seconds", round(elapsed, 6))

            report.add_stage(
                stage_name,
                passed,
                details,
                metrics,
            )

        except Exception as exc:
            elapsed = time.perf_counter() - started

            report.add_stage(
                stage_name,
                False,
                f"{type(exc).__name__}: {exc}",
                {"duration_seconds": round(elapsed, 6)},
            )

    @staticmethod
    def _interpret_result(
        result: Any,
    ) -> tuple[bool, str, dict[str, Any]]:
        if isinstance(result, bool):
            return result, "", {}

        if result is None:
            return True, "", {}

        if isinstance(result, Mapping):
            passed = bool(result.get("passed", True))
            details = str(result.get("details", ""))

            metrics = result.get("metrics", {})
            if not isinstance(metrics, Mapping):
                metrics = {}

            return passed, details, dict(metrics)

        return bool(result), "", {"result": result}

    def is_release_ready(self, report: ValidationReport) -> bool:
        return report.completed and report.passed