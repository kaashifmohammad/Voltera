from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class SimulationResult:
    """
    Result of a stress simulation.
    """

    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    results: list[Any] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_cycles == 0:
            return 0.0

        return self.successful_cycles / self.total_cycles

    @property
    def failure_rate(self) -> float:
        if self.total_cycles == 0:
            return 0.0

        return self.failed_cycles / self.total_cycles


class StressSimulator:
    """
    Executes repeatable VOLTERA stress scenarios.

    The simulator deliberately does not depend on the
    internal implementation of the orchestrator.
    """

    def __init__(
        self,
        cycle_runner: Callable[[Any], Any],
    ) -> None:
        if not callable(cycle_runner):
            raise TypeError(
                "cycle_runner must be callable."
            )

        self.cycle_runner = cycle_runner

    def run(
        self,
        scenarios: list[Any],
    ) -> SimulationResult:
        result = SimulationResult()

        for scenario in scenarios:
            result.total_cycles += 1

            try:
                cycle_result = self.cycle_runner(
                    scenario
                )

                result.results.append(
                    cycle_result
                )

                result.successful_cycles += 1

            except Exception as exc:
                result.results.append(
                    {
                        "error": str(exc),
                        "scenario": scenario,
                    }
                )

                result.failed_cycles += 1

        return result

    def run_repeated(
        self,
        scenario: Any,
        cycles: int,
    ) -> SimulationResult:
        if cycles < 0:
            raise ValueError(
                "cycles cannot be negative."
            )

        return self.run(
            [scenario] * cycles
        )

    def run_sequence(
        self,
        scenarios: list[Any],
        repetitions: int = 1,
    ) -> SimulationResult:
        if repetitions < 0:
            raise ValueError(
                "repetitions cannot be negative."
            )

        sequence: list[Any] = []

        for _ in range(repetitions):
            sequence.extend(scenarios)

        return self.run(sequence)