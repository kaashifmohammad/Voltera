from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Iterable


@dataclass(frozen=True)
class PerformanceMetric:
    """
    Represents one measured operation.
    """

    name: str
    duration_seconds: float
    success: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Metric name must be a non-empty string.")

        if self.duration_seconds < 0:
            raise ValueError("Metric duration cannot be negative.")


@dataclass
class PerformanceMetrics:
    """
    Collection and analysis of VOLTERA performance measurements.
    """

    _metrics: list[PerformanceMetric] = field(
        default_factory=list
    )

    def record(
        self,
        name: str,
        duration_seconds: float,
        *,
        success: bool = True,
    ) -> PerformanceMetric:
        metric = PerformanceMetric(
            name=name,
            duration_seconds=float(duration_seconds),
            success=success,
        )

        self._metrics.append(metric)
        return metric

    def add(self, metric: PerformanceMetric) -> None:
        if not isinstance(metric, PerformanceMetric):
            raise TypeError(
                "metric must be a PerformanceMetric instance."
            )

        self._metrics.append(metric)

    def all(self) -> list[PerformanceMetric]:
        return list(self._metrics)

    def clear(self) -> None:
        self._metrics.clear()

    def count(self, name: str | None = None) -> int:
        if name is None:
            return len(self._metrics)

        return sum(
            1
            for metric in self._metrics
            if metric.name == name
        )

    def durations(
        self,
        name: str | None = None,
    ) -> list[float]:
        metrics = self._select(name)

        return [
            metric.duration_seconds
            for metric in metrics
        ]

    def average(
        self,
        name: str | None = None,
    ) -> float:
        values = self.durations(name)

        if not values:
            return 0.0

        return mean(values)

    def minimum(
        self,
        name: str | None = None,
    ) -> float:
        values = self.durations(name)

        if not values:
            return 0.0

        return min(values)

    def maximum(
        self,
        name: str | None = None,
    ) -> float:
        values = self.durations(name)

        if not values:
            return 0.0

        return max(values)

    def success_rate(
        self,
        name: str | None = None,
    ) -> float:
        metrics = self._select(name)

        if not metrics:
            return 0.0

        successful = sum(
            1
            for metric in metrics
            if metric.success
        )

        return successful / len(metrics)

    def summary(
        self,
        name: str | None = None,
    ) -> dict[str, float | int]:
        values = self.durations(name)
        metrics = self._select(name)

        if not values:
            return {
                "count": 0,
                "average": 0.0,
                "minimum": 0.0,
                "maximum": 0.0,
                "success_rate": 0.0,
            }

        return {
            "count": len(metrics),
            "average": mean(values),
            "minimum": min(values),
            "maximum": max(values),
            "success_rate": self.success_rate(name),
        }

    def is_within_threshold(
        self,
        threshold_seconds: float,
        *,
        name: str | None = None,
    ) -> bool:
        if threshold_seconds < 0:
            raise ValueError(
                "Performance threshold cannot be negative."
            )

        values = self.durations(name)

        if not values:
            return True

        return max(values) <= threshold_seconds

    def _select(
        self,
        name: str | None,
    ) -> list[PerformanceMetric]:
        if name is None:
            return list(self._metrics)

        return [
            metric
            for metric in self._metrics
            if metric.name == name
        ]

    @classmethod
    def from_metrics(
        cls,
        metrics: Iterable[PerformanceMetric],
    ) -> "PerformanceMetrics":
        result = cls()

        for metric in metrics:
            result.add(metric)

        return result