import pytest

from performance.metrics import (
    PerformanceMetric,
    PerformanceMetrics,
)


def test_metric_can_be_created():
    metric = PerformanceMetric(
        name="orchestration",
        duration_seconds=0.25,
    )

    assert metric.name == "orchestration"
    assert metric.duration_seconds == 0.25
    assert metric.success is True


def test_metric_rejects_empty_name():
    with pytest.raises(ValueError):
        PerformanceMetric(
            name="",
            duration_seconds=0.1,
        )


def test_metric_rejects_negative_duration():
    with pytest.raises(ValueError):
        PerformanceMetric(
            name="operation",
            duration_seconds=-1,
        )


def test_record_adds_metric():
    metrics = PerformanceMetrics()

    metric = metrics.record(
        "cycle",
        0.5,
    )

    assert metric in metrics.all()
    assert metrics.count() == 1


def test_metrics_can_be_filtered_by_name():
    metrics = PerformanceMetrics()

    metrics.record("cycle", 1.0)
    metrics.record("context", 0.2)
    metrics.record("cycle", 0.5)

    assert metrics.count("cycle") == 2
    assert metrics.count("context") == 1


def test_average_duration():
    metrics = PerformanceMetrics()

    metrics.record("cycle", 1.0)
    metrics.record("cycle", 3.0)

    assert metrics.average("cycle") == pytest.approx(2.0)


def test_minimum_duration():
    metrics = PerformanceMetrics()

    metrics.record("cycle", 1.0)
    metrics.record("cycle", 0.5)
    metrics.record("cycle", 2.0)

    assert metrics.minimum("cycle") == pytest.approx(0.5)


def test_maximum_duration():
    metrics = PerformanceMetrics()

    metrics.record("cycle", 1.0)
    metrics.record("cycle", 2.5)

    assert metrics.maximum("cycle") == pytest.approx(2.5)


def test_success_rate():
    metrics = PerformanceMetrics()

    metrics.record("cycle", 1.0, success=True)
    metrics.record("cycle", 1.0, success=False)
    metrics.record("cycle", 1.0, success=True)

    assert metrics.success_rate("cycle") == pytest.approx(
        2 / 3
    )


def test_empty_metrics_return_safe_summary():
    metrics = PerformanceMetrics()

    assert metrics.summary() == {
        "count": 0,
        "average": 0.0,
        "minimum": 0.0,
        "maximum": 0.0,
        "success_rate": 0.0,
    }


def test_threshold_passes():
    metrics = PerformanceMetrics()

    metrics.record("cycle", 0.1)
    metrics.record("cycle", 0.2)

    assert metrics.is_within_threshold(
        0.5,
        name="cycle",
    )


def test_threshold_fails():
    metrics = PerformanceMetrics()

    metrics.record("cycle", 0.1)
    metrics.record("cycle", 0.8)

    assert not metrics.is_within_threshold(
        0.5,
        name="cycle",
    )


def test_no_metrics_are_within_threshold():
    metrics = PerformanceMetrics()

    assert metrics.is_within_threshold(0.1)


def test_clear_removes_metrics():
    metrics = PerformanceMetrics()

    metrics.record("cycle", 0.1)
    metrics.clear()

    assert metrics.count() == 0


def test_from_metrics_creates_collection():
    source = [
        PerformanceMetric("a", 0.1),
        PerformanceMetric("b", 0.2),
    ]

    metrics = PerformanceMetrics.from_metrics(source)

    assert metrics.count() == 2
    assert metrics.average() == pytest.approx(0.15)