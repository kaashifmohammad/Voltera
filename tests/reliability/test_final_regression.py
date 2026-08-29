from validation.final_validator import FinalValidator


def test_successful_regression_gate():
    gates = {
        stage: (lambda: True)
        for stage in FinalValidator.REQUIRED_STAGES
    }

    validator = FinalValidator(gates=gates)
    report = validator.validate()

    regression = next(
        stage
        for stage in report.stages
        if stage.name == "regression_tests"
    )

    assert regression.passed is True


def test_regression_failure_blocks_release():
    gates = {
        stage: (lambda: True)
        for stage in FinalValidator.REQUIRED_STAGES
    }

    gates["regression_tests"] = lambda: {
        "passed": False,
        "details": "Regression detected.",
        "metrics": {"failed": 1},
    }

    validator = FinalValidator(gates=gates)
    report = validator.validate()

    assert validator.is_release_ready(report) is False
    assert report.passed is False
    assert "regression_tests" in report.failed_stages