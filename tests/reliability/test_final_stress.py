import time

from validation.final_validator import FinalValidator


def all_passing_gates():
    return {
        stage: (lambda: True)
        for stage in FinalValidator.REQUIRED_STAGES
    }


def test_stress_gate_success():
    gates = all_passing_gates()

    gates["stress_tests"] = lambda: {
        "passed": True,
        "details": "Stress workload completed.",
        "metrics": {
            "iterations": 100,
            "failures": 0,
        },
    }

    validator = FinalValidator(gates=gates)
    report = validator.validate()

    stress = next(
        stage
        for stage in report.stages
        if stage.name == "stress_tests"
    )

    assert stress.passed is True
    assert stress.metrics["iterations"] == 100
    assert stress.metrics["failures"] == 0


def test_performance_gate_records_duration():
    gates = all_passing_gates()

    def performance_gate():
        time.sleep(0.001)
        return {
            "passed": True,
            "details": "Performance within limits.",
        }

    gates["performance_stability"] = performance_gate

    validator = FinalValidator(
        gates=gates,
        performance_limit_seconds=1.0,
    )

    report = validator.validate()

    performance = next(
        stage
        for stage in report.stages
        if stage.name == "performance_stability"
    )

    assert performance.passed is True
    assert performance.metrics["duration_seconds"] >= 0


def test_slow_performance_gate_fails():
    gates = all_passing_gates()

    def slow_gate():
        time.sleep(0.01)
        return True

    gates["performance_stability"] = slow_gate

    validator = FinalValidator(
        gates=gates,
        performance_limit_seconds=0.001,
    )

    report = validator.validate()

    assert report.passed is False
    assert "performance_stability" in report.failed_stages