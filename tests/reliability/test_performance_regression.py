import time

import pytest

from performance.metrics import PerformanceMetrics
from performance.profiler import PerformanceProfiler


def test_multiple_cycles_can_be_measured():
    profiler = PerformanceProfiler()

    for _ in range(20):
        profiler.run(
            "cycle",
            lambda: sum(range(100)),
        )

    assert profiler.metrics.count("cycle") == 20


def test_cycle_metrics_are_non_negative():
    profiler = PerformanceProfiler()

    for _ in range(10):
        profiler.run(
            "cycle",
            lambda: sum(range(100)),
        )

    durations = profiler.metrics.durations("cycle")

    assert len(durations) == 10
    assert all(
        duration >= 0
        for duration in durations
    )


def test_performance_metrics_do_not_change_result():
    profiler = PerformanceProfiler()

    def operation():
        return {
            "battery": 50,
            "charging": False,
            "context": "active",
        }

    result = profiler.run(
        "state",
        operation,
    )

    assert result == {
        "battery": 50,
        "charging": False,
        "context": "active",
    }


def test_failed_cycle_is_measured_without_swallowing_error():
    profiler = PerformanceProfiler()

    def operation():
        raise RuntimeError("cycle failure")

    with pytest.raises(RuntimeError):
        profiler.run(
            "cycle",
            operation,
        )

    assert profiler.metrics.count("cycle") == 1
    assert (
        profiler.metrics.success_rate("cycle")
        == 0.0
    )


def test_successful_and_failed_cycles_are_distinguishable():
    profiler = PerformanceProfiler()

    profiler.run(
        "cycle",
        lambda: "success",
    )

    def fail():
        raise RuntimeError("failure")

    with pytest.raises(RuntimeError):
        profiler.run(
            "cycle",
            fail,
        )

    metrics = profiler.metrics.all()

    assert len(metrics) == 2
    assert metrics[0].success is True
    assert metrics[1].success is False


def test_repeated_measurement_has_reasonable_overhead():
    profiler = PerformanceProfiler()

    start = time.perf_counter()

    for _ in range(100):
        profiler.run(
            "lightweight",
            lambda: None,
        )

    elapsed = time.perf_counter() - start

    assert elapsed < 1.0


def test_threshold_can_be_used_as_regression_gate():
    metrics = PerformanceMetrics()

    for duration in [0.01, 0.02, 0.015]:
        metrics.record(
            "cycle",
            duration,
        )

    assert metrics.is_within_threshold(
        0.1,
        name="cycle",
    )


def test_regression_gate_detects_slow_operation():
    metrics = PerformanceMetrics()

    metrics.record(
        "cycle",
        0.25,
    )

    assert not metrics.is_within_threshold(
        0.1,
        name="cycle",
    )