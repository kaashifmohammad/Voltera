import time

import pytest

from performance.metrics import PerformanceMetrics
from performance.profiler import PerformanceProfiler


def test_profiler_measures_code_block():
    profiler = PerformanceProfiler()

    with profiler.measure("sleep"):
        time.sleep(0.001)

    metric = profiler.latest("sleep")

    assert metric is not None
    assert metric.duration_seconds >= 0
    assert metric.success is True


def test_profiler_records_successful_operation():
    profiler = PerformanceProfiler()

    result = profiler.run(
        "addition",
        lambda a, b: a + b,
        2,
        3,
    )

    assert result == 5

    metric = profiler.latest("addition")

    assert metric is not None
    assert metric.success is True


def test_profiler_records_failed_operation():
    profiler = PerformanceProfiler()

    def failing_operation():
        raise RuntimeError("failure")

    with pytest.raises(RuntimeError):
        profiler.run(
            "failure",
            failing_operation,
        )

    metric = profiler.latest("failure")

    assert metric is not None
    assert metric.success is False


def test_profiler_preserves_operation_exception():
    profiler = PerformanceProfiler()

    with pytest.raises(ValueError, match="expected"):
        profiler.run(
            "operation",
            lambda: (_ for _ in ()).throw(
                ValueError("expected")
            ),
        )


def test_profiler_preserves_return_value():
    profiler = PerformanceProfiler()

    expected = {
        "battery": 75,
        "charging": False,
    }

    result = profiler.run(
        "state",
        lambda: expected,
    )

    assert result is expected


def test_callable_wrapper_records_metrics():
    profiler = PerformanceProfiler()

    wrapped = profiler.measure_callable(
        "wrapped",
        lambda value: value * 2,
    )

    assert wrapped(5) == 10

    metric = profiler.latest("wrapped")

    assert metric is not None
    assert metric.success is True


def test_profiler_can_use_existing_metrics():
    metrics = PerformanceMetrics()
    profiler = PerformanceProfiler(metrics)

    profiler.run(
        "operation",
        lambda: "done",
    )

    assert metrics.count("operation") == 1


def test_latest_returns_none_when_empty():
    profiler = PerformanceProfiler()

    assert profiler.latest() is None


def test_latest_returns_most_recent_metric():
    profiler = PerformanceProfiler()

    profiler.run(
        "cycle",
        lambda: 1,
    )

    profiler.run(
        "cycle",
        lambda: 2,
    )

    metric = profiler.latest("cycle")

    assert metric is not None
    assert profiler.metrics.count("cycle") == 2


def test_reset_clears_profiler_metrics():
    profiler = PerformanceProfiler()

    profiler.run(
        "cycle",
        lambda: None,
    )

    profiler.reset()

    assert profiler.latest() is None
    assert profiler.metrics.count() == 0