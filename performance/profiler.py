from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Callable, Iterator, TypeVar

from .metrics import PerformanceMetric, PerformanceMetrics


T = TypeVar("T")


class PerformanceProfiler:
    """
    Lightweight execution profiler for VOLTERA.

    The profiler is intentionally independent from the
    intelligence pipeline. It measures operations without
    changing their behavior.
    """

    def __init__(
        self,
        metrics: PerformanceMetrics | None = None,
    ) -> None:
        self.metrics = (
            metrics
            if metrics is not None
            else PerformanceMetrics()
        )

    @contextmanager
    def measure(
        self,
        name: str,
    ) -> Iterator[None]:
        """
        Measure a code block.
        """

        start = perf_counter()
        success = False

        try:
            yield
            success = True
        finally:
            duration = perf_counter() - start

            self.metrics.record(
                name,
                duration,
                success=success,
            )

    def run(
        self,
        name: str,
        operation: Callable[..., T],
        *args,
        **kwargs,
    ) -> T:
        """
        Execute an operation while measuring its duration.

        The operation's return value and exceptions are preserved.
        """

        start = perf_counter()

        try:
            result = operation(
                *args,
                **kwargs,
            )
        except Exception:
            duration = perf_counter() - start

            self.metrics.record(
                name,
                duration,
                success=False,
            )

            raise

        duration = perf_counter() - start

        self.metrics.record(
            name,
            duration,
            success=True,
        )

        return result

    def measure_callable(
        self,
        name: str,
        operation: Callable[..., T],
    ) -> Callable[..., T]:
        """
        Return a wrapped callable that records performance
        metrics while preserving the callable's behavior.
        """

        def wrapped(*args, **kwargs) -> T:
            return self.run(
                name,
                operation,
                *args,
                **kwargs,
            )

        return wrapped

    def latest(
        self,
        name: str | None = None,
    ) -> PerformanceMetric | None:
        metrics = self.metrics.all()

        if name is not None:
            metrics = [
                metric
                for metric in metrics
                if metric.name == name
            ]

        if not metrics:
            return None

        return metrics[-1]

    def reset(self) -> None:
        self.metrics.clear()