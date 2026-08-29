from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ValidationStage:
    name: str
    passed: bool
    details: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)


class ValidationReport:
    """Structured report for the final VOLTERA validation."""

    def __init__(self) -> None:
        self.started_at = datetime.now(timezone.utc)
        self.completed_at: datetime | None = None
        self.stages: list[ValidationStage] = []

    def add_stage(
        self,
        name: str,
        passed: bool,
        details: str = "",
        metrics: dict[str, Any] | None = None,
    ) -> None:
        self.stages.append(
            ValidationStage(
                name=name,
                passed=bool(passed),
                details=details,
                metrics=metrics or {},
            )
        )

    @property
    def passed(self) -> bool:
        return bool(self.stages) and all(stage.passed for stage in self.stages)

    @property
    def completed(self) -> bool:
        return self.completed_at is not None

    @property
    def failed_stages(self) -> list[str]:
        return [stage.name for stage in self.stages if not stage.passed]

    def complete(self) -> None:
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at is not None
                else None
            ),
            "passed": self.passed,
            "completed": self.completed,
            "total_stages": len(self.stages),
            "passed_stages": sum(stage.passed for stage in self.stages),
            "failed_stages": self.failed_stages,
            "stages": [
                {
                    "name": stage.name,
                    "passed": stage.passed,
                    "details": stage.details,
                    "metrics": stage.metrics,
                }
                for stage in self.stages
            ],
        }

    def summary(self) -> str:
        status = "RELEASE READY" if self.passed else "VALIDATION FAILED"

        return (
            f"{status}: "
            f"{sum(stage.passed for stage in self.stages)}/"
            f"{len(self.stages)} validation stages passed."
        )