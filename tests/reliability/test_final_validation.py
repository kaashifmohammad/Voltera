from validation.final_validator import FinalValidator


STAGES = FinalValidator.REQUIRED_STAGES


def passing_gates():
    return {stage: (lambda: True) for stage in STAGES}


def test_final_validator_runs_all_required_stages():
    calls = []

    def make_gate(name):
        def gate():
            calls.append(name)
            return True

        return gate

    gates = {stage: make_gate(stage) for stage in STAGES}

    validator = FinalValidator(gates=gates)
    report = validator.validate()

    assert report.passed is True
    assert report.completed is True
    assert calls == list(STAGES)


def test_final_validator_requires_all_stages():
    gates = passing_gates()
    gates.pop("stress_tests")

    validator = FinalValidator(gates=gates)
    report = validator.validate()

    assert report.passed is False
    assert "stress_tests" in report.failed_stages


def test_final_validator_handles_gate_failure():
    gates = passing_gates()
    gates["regression_tests"] = lambda: False

    validator = FinalValidator(gates=gates)
    report = validator.validate()

    assert report.passed is False
    assert "regression_tests" in report.failed_stages


def test_final_validator_handles_gate_exception():
    gates = passing_gates()

    def failing_gate():
        raise RuntimeError("database integrity failure")

    gates["persistence_integrity"] = failing_gate

    validator = FinalValidator(gates=gates)
    report = validator.validate()

    assert report.passed is False
    assert "persistence_integrity" in report.failed_stages

    failed_stage = next(
        stage
        for stage in report.stages
        if stage.name == "persistence_integrity"
    )

    assert "RuntimeError" in failed_stage.details